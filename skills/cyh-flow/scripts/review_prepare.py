#!/usr/bin/env python3
"""Prepare raw GitHub PR evidence and a shared disposable source cache."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable


SCHEMA_VERSION = 1
PR_URL_RE = re.compile(
    r"^https://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/pull/(?P<number>\d+)/?$"
)
PR_REF_RE = re.compile(
    r"^(?P<owner>[^/\s]+)/(?P<repo>[^#\s]+)#(?P<number>\d+)$"
)


class PrepareError(RuntimeError):
    pass


@dataclass(frozen=True)
class Target:
    owner: str
    repo: str
    number: int

    @property
    def slug(self) -> str:
        return f"{self.owner}/{self.repo}#{self.number}"

    @property
    def repo_slug(self) -> str:
        return f"{self.owner}/{self.repo}"

    @property
    def url(self) -> str:
        return f"https://github.com/{self.owner}/{self.repo}/pull/{self.number}"

    @property
    def directory_name(self) -> str:
        return f"{self.owner}-{self.repo}-{self.number}"


class CommandRunner:
    def run_text(self, command: list[str], *, input_bytes: bytes | None = None) -> str:
        try:
            result = subprocess.run(
                command,
                input=input_bytes,
                check=False,
                capture_output=True,
            )
        except FileNotFoundError as error:
            raise PrepareError(f"command is unavailable: {command[0]}") from error
        if result.returncode != 0:
            message = (result.stderr or result.stdout).decode(
                "utf-8", errors="replace"
            ).strip()
            raise PrepareError(
                f"command exited {result.returncode}: {' '.join(command)}: {message}"
            )
        return result.stdout.decode("utf-8", errors="strict")

    def run_bytes(self, command: list[str]) -> bytes:
        try:
            result = subprocess.run(command, check=False, capture_output=True)
        except FileNotFoundError as error:
            raise PrepareError(f"command is unavailable: {command[0]}") from error
        if result.returncode != 0:
            message = (result.stderr or result.stdout).decode(
                "utf-8", errors="replace"
            ).strip()
            raise PrepareError(
                f"command exited {result.returncode}: {' '.join(command)}: {message}"
            )
        return result.stdout

    def run_json(self, command: list[str]) -> Any:
        raw = self.run_text(command)
        try:
            return json.loads(raw)
        except json.JSONDecodeError as error:
            raise PrepareError(f"command returned malformed JSON: {' '.join(command)}") from error


JsonFetcher = Callable[[list[str]], Any]


def parse_target(value: str) -> Target:
    match = PR_URL_RE.fullmatch(value) or PR_REF_RE.fullmatch(value)
    if not match:
        raise ValueError("target must be a GitHub PR URL or OWNER/REPO#NUMBER")
    return Target(
        owner=match.group("owner"),
        repo=match.group("repo"),
        number=int(match.group("number")),
    )


def flatten_pages(payload: Any, endpoint: str) -> list[dict[str, Any]]:
    if not isinstance(payload, list):
        raise PrepareError(f"expected list response from {endpoint}")
    pages = payload if payload and all(isinstance(item, list) for item in payload) else [payload]
    records: list[dict[str, Any]] = []
    for page in pages:
        if not isinstance(page, list):
            raise PrepareError(f"expected list pages from {endpoint}")
        records.extend(item for item in page if isinstance(item, dict))
    return records


def fetch_paged(endpoint: str, fetcher: JsonFetcher) -> list[dict[str, Any]]:
    payload = fetcher(["gh", "api", "--paginate", "--slurp", endpoint])
    return flatten_pages(payload, endpoint)


def fetch_raw_pages(endpoint: str, fetcher: JsonFetcher) -> list[dict[str, Any]]:
    payload = fetcher(["gh", "api", "--paginate", "--slurp", endpoint])
    if not isinstance(payload, list) or not all(
        isinstance(page, dict) for page in payload
    ):
        raise PrepareError(f"expected object pages from {endpoint}")
    return payload


def atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    encoded = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    try:
        with temporary.open("x", encoding="utf-8") as handle:
            os.chmod(temporary, 0o600)
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def atomic_write_bytes(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        with temporary.open("xb") as handle:
            os.chmod(temporary, 0o600)
            handle.write(value)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def collect_target(target: Target, fetcher: JsonFetcher, root: Path) -> dict[str, Any]:
    endpoint_root = f"repos/{target.owner}/{target.repo}"
    pull = fetcher(["gh", "api", f"{endpoint_root}/pulls/{target.number}"])
    if not isinstance(pull, dict):
        raise PrepareError(f"malformed PR metadata for {target.slug}")
    head = pull.get("head") if isinstance(pull.get("head"), dict) else {}
    pull_base = pull.get("base") if isinstance(pull.get("base"), dict) else {}
    head_sha = head.get("sha")
    base_sha = pull_base.get("sha")
    base_name = pull_base.get("ref")
    head_name = head.get("ref")
    if not all(
        isinstance(value, str) and value
        for value in (head_sha, base_sha, base_name, head_name)
    ):
        raise PrepareError(f"missing base/head ref or SHA for {target.slug}")

    endpoints: dict[str, str] = {
        "files": f"{endpoint_root}/pulls/{target.number}/files?per_page=100",
        "commits": f"{endpoint_root}/pulls/{target.number}/commits?per_page=100",
        "issue_comments": f"{endpoint_root}/issues/{target.number}/comments?per_page=100",
        "reviews": f"{endpoint_root}/pulls/{target.number}/reviews?per_page=100",
        "review_comments": f"{endpoint_root}/pulls/{target.number}/comments?per_page=100",
        "timeline": f"{endpoint_root}/issues/{target.number}/timeline?per_page=100",
    }
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(endpoints) + 2) as pool:
        futures = {
            name: pool.submit(fetch_paged, endpoint, fetcher)
            for name, endpoint in endpoints.items()
        }
        futures["checks"] = pool.submit(
            fetch_raw_pages,
            f"{endpoint_root}/commits/{head_sha}/check-runs?per_page=100",
            fetcher,
        )
        futures["statuses"] = pool.submit(
            fetch_paged,
            f"{endpoint_root}/commits/{head_sha}/statuses?per_page=100",
            fetcher,
        )
        fetched = {name: future.result() for name, future in futures.items()}

    target_dir = root / "targets" / target.directory_name
    documents: dict[str, str] = {}
    values = {"pull": pull, **fetched}
    for name, value in values.items():
        path = target_dir / f"{name.replace('_', '-')}.json"
        atomic_write_json(path, value)
        documents[name] = str(path.resolve())

    return {
        "slug": target.slug,
        "url": target.url,
        "repository": target.repo_slug,
        "number": target.number,
        "base_ref": base_name,
        "head_ref": head_name,
        "base_oid": base_sha,
        "head_oid": head_sha,
        "documents": documents,
    }


def repository_directory(root: Path, repo_slug: str) -> Path:
    return root / "repositories" / repo_slug.replace("/", "--") / "objects"


def create_object_cache(
    repo_slug: str,
    records: list[dict[str, Any]],
    root: Path,
    runner: CommandRunner,
    source_repo: Path | None,
) -> dict[str, Any]:
    object_dir = repository_directory(root, repo_slug)
    object_dir.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if source_repo is not None:
        source_remote = runner.run_text(
            ["git", "-C", str(source_repo), "remote", "get-url", "origin"]
        ).strip()
        if not source_remote:
            raise PrepareError("--source-repo has no origin remote")
        runner.run_text(
            ["git", "clone", "--shared", "--no-checkout", str(source_repo), str(object_dir)]
        )
        runner.run_text(
            [
                "git",
                "-C",
                str(object_dir),
                "remote",
                "set-url",
                "origin",
                source_remote,
            ]
        )
    else:
        runner.run_text(
            [
                "gh",
                "repo",
                "clone",
                repo_slug,
                str(object_dir),
                "--",
                "--filter=blob:none",
                "--no-checkout",
            ]
        )

    refspecs: list[str] = []
    for record in records:
        number = int(record["number"])
        refspecs.extend(
            [
                f"+refs/heads/{record['base_ref']}:refs/cyh-flow/base-{number}",
                f"+refs/pull/{number}/head:refs/cyh-flow/pr-{number}",
            ]
        )
    runner.run_text(
        ["git", "-C", str(object_dir), "fetch", "--no-tags", "origin", *refspecs]
    )

    worktree_root = object_dir.parent / "worktrees"
    worktree_root.mkdir(parents=True, exist_ok=True, mode=0o700)
    individual: dict[str, str] = {}
    for record in records:
        number = int(record["number"])
        record["source_base_oid"] = runner.run_text(
            [
                "git",
                "-C",
                str(object_dir),
                "rev-parse",
                f"refs/cyh-flow/base-{number}",
            ]
        ).strip()
        record["source_head_oid"] = runner.run_text(
            [
                "git",
                "-C",
                str(object_dir),
                "rev-parse",
                f"refs/cyh-flow/pr-{number}",
            ]
        ).strip()
        path = worktree_root / f"pr-{number}"
        runner.run_text(
            [
                "git",
                "-C",
                str(object_dir),
                "worktree",
                "add",
                "--detach",
                str(path),
                f"refs/cyh-flow/pr-{number}",
            ]
        )
        individual[record["slug"]] = str(path.resolve())
        diff_path = root / "targets" / Target(
            *str(record["repository"]).split("/", 1), number
        ).directory_name / "diff.patch"
        diff = runner.run_bytes(
            [
                "git",
                "-C",
                str(object_dir),
                "diff",
                "--binary",
                f"{record['source_base_oid']}...{record['source_head_oid']}",
            ]
        )
        atomic_write_bytes(diff_path, diff)
        record["documents"]["diff"] = str(diff_path.resolve())

    combined: dict[str, Any] | None = None
    if len(records) > 1:
        base_oids = {str(record["base_oid"]) for record in records}
        combined = {"status": "unavailable", "path": None, "reason": None}
        if len(base_oids) != 1:
            combined["reason"] = "targets have different observed base OIDs"
        else:
            combined_path = worktree_root / "combined"
            first_number = int(records[0]["number"])
            try:
                runner.run_text(
                    [
                        "git",
                        "-C",
                        str(object_dir),
                        "worktree",
                        "add",
                        "--detach",
                        str(combined_path),
                        f"refs/cyh-flow/base-{first_number}",
                    ]
                )
                for record in records:
                    patch = Path(record["documents"]["diff"]).read_bytes()
                    runner.run_text(
                        ["git", "-C", str(combined_path), "apply", "--whitespace=nowarn", "-"],
                        input_bytes=patch,
                    )
            except PrepareError as error:
                combined["reason"] = str(error)
            else:
                combined = {
                    "status": "ready",
                    "path": str(combined_path.resolve()),
                    "reason": None,
                }

    return {
        "repository": repo_slug,
        "object_cache": str(object_dir.resolve()),
        "worktrees": individual,
        "combined": combined,
    }


def prepare(
    targets: list[Target],
    output_dir: Path,
    runner: CommandRunner,
    source_repo: Path | None = None,
) -> dict[str, Any]:
    if not targets:
        raise PrepareError("at least one PR target is required")
    slugs = [target.slug for target in targets]
    if len(set(slugs)) != len(slugs):
        raise PrepareError("duplicate PR targets are not allowed")
    if output_dir.exists() and any(output_dir.iterdir()):
        raise PrepareError(f"--output-dir must be empty: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(output_dir, 0o700)
    manifest_path = output_dir / "manifest.json"
    if manifest_path.exists():
        raise PrepareError(f"refusing to overwrite existing manifest: {manifest_path}")

    auth = runner.run_json(["gh", "api", "user"])
    login = auth.get("login") if isinstance(auth, dict) else None
    if not isinstance(login, str) or not login:
        raise PrepareError("cannot resolve authenticated GitHub user")

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(targets)) as pool:
        records = list(
            pool.map(
                lambda target: collect_target(target, runner.run_json, output_dir),
                targets,
            )
        )

    grouped: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        grouped.setdefault(str(record["repository"]), []).append(record)
    if source_repo is not None and len(grouped) != 1:
        raise PrepareError("--source-repo requires all targets to use one repository")

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(grouped)) as pool:
        futures = [
            pool.submit(
                create_object_cache,
                repo_slug,
                repo_records,
                output_dir,
                runner,
                source_repo,
            )
            for repo_slug, repo_records in grouped.items()
        ]
        repositories = [future.result() for future in futures]
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "created_at": datetime.now(UTC).isoformat(),
        "authenticated_user": login,
        "transport_only": True,
        "stability_gate": False,
        "targets": records,
        "repositories": repositories,
    }
    atomic_write_json(manifest_path, manifest)
    return {
        "status": "ready",
        "manifest": str(manifest_path.resolve()),
        "sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "targets": slugs,
        "repositories": sorted(grouped),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Cache complete raw PR evidence and source objects once for reviewers."
    )
    parser.add_argument("targets", nargs="+", help="PR URL or OWNER/REPO#NUMBER")
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument(
        "--source-repo",
        type=Path,
        help="optional readable local clone used only as an object source for one repository",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        targets = [parse_target(value) for value in args.targets]
        result = prepare(
            targets,
            args.output_dir.resolve(),
            CommandRunner(),
            args.source_repo.resolve() if args.source_repo else None,
        )
    except (PrepareError, ValueError) as error:
        print(json.dumps({"status": "blocked", "error": str(error)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
