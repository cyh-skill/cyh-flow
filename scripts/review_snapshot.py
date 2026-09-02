#!/usr/bin/env python3
"""Freeze and verify immutable cyh-flow review targets."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable


FORMAT = "cyh-review-target/v1"
ARTIFACT_FILES = {
    "cached_diff": "cached.diff",
    "committed_diff": "committed.diff",
    "unstaged_diff": "unstaged.diff",
}


class SnapshotError(RuntimeError):
    pass


def canonical_json(value: Any) -> bytes:
    """Serialize the manifest's integer/string/null schema as RFC 8785 JSON."""
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def run_git(repo: Path, args: Iterable[str]) -> bytes:
    completed = subprocess.run(
        ["git", "-C", os.fspath(repo), *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        command = "git " + " ".join(args)
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise SnapshotError(f"{command} failed: {detail or 'unknown git error'}")
    return completed.stdout


def resolve_repo(value: str | Path) -> Path:
    requested = Path(value).expanduser().resolve()
    root = run_git(requested, ["rev-parse", "--show-toplevel"]).rstrip(b"\n")
    return Path(os.fsdecode(root)).resolve()


def resolve_commit(repo: Path, value: str) -> str:
    resolved = run_git(repo, ["rev-parse", f"{value}^{{commit}}"]).strip()
    return resolved.decode("ascii")


def repository_roots(repo: Path, head: str) -> list[str]:
    roots = run_git(repo, ["rev-list", "--max-parents=0", head]).splitlines()
    return sorted(root.decode("ascii") for root in roots if root)


def raw_untracked_paths(repo: Path) -> list[bytes]:
    raw = run_git(repo, ["ls-files", "--others", "--exclude-standard", "-z"])
    return sorted((item for item in raw.split(b"\0") if item), key=bytes)


def raw_ignored_paths(repo: Path) -> list[bytes]:
    raw = run_git(
        repo,
        ["ls-files", "--others", "--ignored", "--exclude-standard", "-z"],
    )
    return sorted((item for item in raw.split(b"\0") if item), key=bytes)


def read_path_bytes(path: bytes) -> tuple[bytes, str]:
    info = os.lstat(path)
    if stat.S_ISLNK(info.st_mode):
        target = os.readlink(path)
        return (target if isinstance(target, bytes) else os.fsencode(target), "120000")
    if not stat.S_ISREG(info.st_mode):
        raise SnapshotError(f"unsupported untracked entry type: {os.fsdecode(path)}")
    with open(path, "rb") as handle:
        content = handle.read()
    mode = "100755" if info.st_mode & 0o111 else "100644"
    return content, mode


def untracked_entries(repo: Path) -> tuple[list[dict[str, Any]], list[bytes]]:
    repo_bytes = os.fsencode(repo)
    paths = raw_untracked_paths(repo)
    entries: list[dict[str, Any]] = []
    for relative in paths:
        content, mode = read_path_bytes(os.path.join(repo_bytes, relative))
        entries.append(
            {
                "kind": "untracked",
                "mode": mode,
                "path_b64url": b64url(relative),
                "sha256": digest(content),
                "size": len(content),
            }
        )
    return entries, paths


def submodule_entries(
    repo: Path, *, committed_head: str | None = None
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    raw = (
        run_git(repo, ["ls-tree", "-r", "-z", committed_head])
        if committed_head
        else run_git(repo, ["ls-files", "--stage", "-z"])
    )
    repo_bytes = os.fsencode(repo)
    entries: list[dict[str, Any]] = []
    retained_states: list[dict[str, Any]] = []
    dirty: list[str] = []
    for record in (item for item in raw.split(b"\0") if item):
        header, separator, relative = record.partition(b"\t")
        if not separator:
            continue
        fields = header.split()
        if committed_head:
            if len(fields) < 3 or fields[0] != b"160000" or fields[1] != b"commit":
                continue
            index_oid = fields[2].decode("ascii")
        else:
            if len(fields) < 3 or fields[0] != b"160000" or fields[2] != b"0":
                continue
            index_oid = fields[1].decode("ascii")
        child = os.path.join(repo_bytes, relative)
        worktree_head: str | None = index_oid if committed_head else None
        status_sha256: str | None = None
        status_size = 0
        if not committed_head and os.path.isdir(child):
            try:
                child_path = Path(os.fsdecode(child))
                worktree_head = run_git(child_path, ["rev-parse", "HEAD"]).strip().decode("ascii")
                status = run_git(
                    child_path,
                    ["status", "--porcelain=v1", "-z", "--untracked-files=all"],
                )
                status_sha256 = digest(status)
                status_size = len(status)
                if status:
                    dirty.append(os.fsdecode(relative))
            except SnapshotError:
                worktree_head = None
                status_sha256 = None
        state = canonical_json(
            {
                "index_oid": index_oid,
                "status_sha256": status_sha256,
                "status_size": status_size,
                "worktree_head": worktree_head,
            }
        )
        path_token = b64url(relative)
        entries.append(
            {
                "kind": "submodule",
                "mode": "160000",
                "path_b64url": path_token,
                "sha256": digest(state),
                "size": len(state),
            }
        )
        retained_states.append(
            {"path_b64url": path_token, "state_b64url": b64url(state)}
        )
    return entries, retained_states, dirty


def sort_entries(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        entries,
        key=lambda item: (b64url_decode(item["path_b64url"]), item["kind"]),
    )


def changed_files(repo: Path, kind: str, base: str | None, head: str) -> list[str]:
    if kind == "local":
        chunks = [
            run_git(repo, ["diff", "--name-only", "-z", "--no-ext-diff"]),
            run_git(repo, ["diff", "--cached", "--name-only", "-z", "--no-ext-diff"]),
            b"\0".join(raw_untracked_paths(repo)) + b"\0",
        ]
    else:
        if base is None:
            raise SnapshotError("base is required for a committed target")
        chunks = [
            run_git(repo, ["diff", "--name-only", "-z", "--no-ext-diff", f"{base}...{head}"])
        ]
    raw_paths = {item for chunk in chunks for item in chunk.split(b"\0") if item}
    return [os.fsdecode(item) for item in sorted(raw_paths, key=bytes)]


def build_target(
    repo: Path,
    kind: str,
    base_value: str | None,
    head_value: str | None,
    merge_base_value: str | None,
) -> tuple[dict[str, Any], dict[str, bytes], dict[str, Any], list[bytes]]:
    if kind == "local":
        if any(value is not None for value in (base_value, head_value, merge_base_value)):
            raise SnapshotError(
                "local targets resolve HEAD automatically; omit base/head/merge-base"
            )
        head = resolve_commit(repo, "HEAD")
        base = None
        merge_base = None
        artifact_data = {
            "cached_diff": run_git(
                repo, ["diff", "--cached", "--binary", "--full-index", "--no-ext-diff"]
            ),
            "unstaged_diff": run_git(
                repo, ["diff", "--binary", "--full-index", "--no-ext-diff"]
            ),
        }
        untracked, untracked_paths = untracked_entries(repo)
    else:
        if base_value is None or head_value is None:
            raise SnapshotError(f"{kind} targets require --base and --head")
        base = resolve_commit(repo, base_value)
        head = resolve_commit(repo, head_value)
        actual_merge_base = run_git(repo, ["merge-base", base, head]).strip().decode("ascii")
        if merge_base_value:
            requested_merge_base = resolve_commit(repo, merge_base_value)
            if requested_merge_base != actual_merge_base:
                raise SnapshotError(
                    "provided merge base does not match git merge-base: "
                    f"expected {actual_merge_base}, got {requested_merge_base}"
                )
        merge_base = actual_merge_base
        artifact_data = {
            "committed_diff": run_git(
                repo,
                ["diff", "--binary", "--full-index", "--no-ext-diff", f"{base}...{head}"],
            )
        }
        untracked = []
        untracked_paths = []

    submodules, retained_states, dirty_submodules = submodule_entries(
        repo, committed_head=head if kind != "local" else None
    )
    artifacts = sorted(
        (
            {"kind": name, "length": len(data), "sha256": digest(data)}
            for name, data in artifact_data.items()
        ),
        key=lambda item: item["kind"],
    )
    manifest = {
        "artifacts": artifacts,
        "base_sha": base,
        "entries": sort_entries([*untracked, *submodules]),
        "format": FORMAT,
        "head_sha": head,
        "merge_base_sha": merge_base,
        "repository_roots": repository_roots(repo, head),
        "target_kind": kind,
    }
    metadata = {
        "base_input": base_value,
        "base_sha": base,
        "changed_files": changed_files(repo, kind, base, head),
        "dirty_submodules": dirty_submodules,
        "head_input": head_value,
        "head_sha": head,
        "kind": kind,
        "merge_base_input": merge_base_value,
        "merge_base_sha": merge_base,
        "repo_root": os.fspath(repo),
        "submodule_states": retained_states,
    }
    return manifest, artifact_data, metadata, untracked_paths


def prepare_output(value: str | None) -> Path:
    if value is None:
        return Path(tempfile.mkdtemp(prefix="cyh-review-"))
    output = Path(value).expanduser().resolve()
    if output.exists() and not output.is_dir():
        raise SnapshotError(f"output path is not a directory: {output}")
    if output.exists() and any(output.iterdir()):
        raise SnapshotError(f"output directory is not empty: {output}")
    output.mkdir(parents=True, mode=0o700, exist_ok=True)
    output.chmod(0o700)
    return output


def write_private_bytes(path: Path, content: bytes) -> None:
    path.write_bytes(content)
    path.chmod(0o600)


def write_private_text(path: Path, content: str, *, encoding: str) -> None:
    path.write_text(content, encoding=encoding)
    path.chmod(0o600)


def copy_untracked(repo: Path, snapshot: Path, paths: list[bytes]) -> None:
    repo_bytes = os.fsencode(repo)
    snapshot_bytes = os.fsencode(snapshot)
    for relative in paths:
        source = os.path.join(repo_bytes, relative)
        destination = os.path.join(snapshot_bytes, relative)
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        info = os.lstat(source)
        if stat.S_ISLNK(info.st_mode):
            os.symlink(os.readlink(source), destination)
        else:
            shutil.copy2(source, destination, follow_symlinks=False)


def create_snapshot(
    repo: Path,
    output: Path,
    metadata: dict[str, Any],
    artifact_data: dict[str, bytes],
    untracked_paths: list[bytes],
) -> Path:
    snapshot = output / "snapshot"
    completed = subprocess.run(
        [
            "git",
            "clone",
            "--quiet",
            "--local",
            "--no-checkout",
            os.fspath(repo),
            os.fspath(snapshot),
        ],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise SnapshotError(f"git clone failed: {detail or 'unknown git error'}")
    run_git(snapshot, ["checkout", "--quiet", "--detach", metadata["head_sha"]])
    if metadata["kind"] == "local":
        cached = artifact_data["cached_diff"]
        unstaged = artifact_data["unstaged_diff"]
        if cached:
            run_git(
                snapshot,
                [
                    "apply",
                    "--binary",
                    "--index",
                    "--whitespace=nowarn",
                    os.fspath(output / "cached.diff"),
                ],
            )
        if unstaged:
            run_git(
                snapshot,
                ["apply", "--binary", "--whitespace=nowarn", os.fspath(output / "unstaged.diff")],
            )
        copy_untracked(repo, snapshot, untracked_paths)
    return snapshot


def freeze(args: argparse.Namespace) -> dict[str, Any]:
    repo = resolve_repo(args.repo)
    if args.output is not None:
        requested_output = Path(args.output).expanduser().resolve()
        try:
            requested_output.relative_to(repo)
        except ValueError:
            pass
        else:
            raise SnapshotError("output directory must be outside the source repository")
    output = prepare_output(args.output)
    try:
        manifest, artifact_data, metadata, untracked_paths = build_target(
            repo, args.kind, args.base, args.head, args.merge_base
        )
        manifest_bytes = canonical_json(manifest)
        target_id = "sha256:" + digest(manifest_bytes)
        write_private_bytes(output / "target-manifest.jcs.json", manifest_bytes)
        write_private_text(output / "target-id.txt", target_id + "\n", encoding="ascii")
        for kind, data in artifact_data.items():
            write_private_bytes(output / ARTIFACT_FILES[kind], data)
        write_private_bytes(output / "snapshot-meta.json", canonical_json(metadata))
        snapshot = create_snapshot(repo, output, metadata, artifact_data, untracked_paths)
        verify(argparse.Namespace(packet_dir=output))
    except Exception:
        if args.output is None:
            shutil.rmtree(output, ignore_errors=True)
        raise
    return {
        "changed_files": metadata["changed_files"],
        "dirty_submodules": metadata["dirty_submodules"],
        "packet_dir": os.fspath(output),
        "snapshot_root": os.fspath(snapshot),
        "target_id": target_id,
    }


def read_packet(packet_dir: str | Path) -> tuple[Path, bytes, dict[str, Any], dict[str, Any], str]:
    packet = Path(packet_dir).expanduser().resolve()
    manifest_bytes = (packet / "target-manifest.jcs.json").read_bytes()
    manifest = json.loads(manifest_bytes)
    metadata = json.loads((packet / "snapshot-meta.json").read_bytes())
    target_id = (packet / "target-id.txt").read_text(encoding="ascii").strip()
    return packet, manifest_bytes, manifest, metadata, target_id


def entry_content(snapshot: Path, entry: dict[str, Any], metadata: dict[str, Any]) -> bytes:
    if entry["kind"] == "untracked":
        path = os.path.join(os.fsencode(snapshot), b64url_decode(entry["path_b64url"]))
        content, mode = read_path_bytes(path)
        if mode != entry["mode"]:
            raise SnapshotError(f"snapshot mode mismatch for {entry['path_b64url']}")
        return content
    if entry["kind"] == "submodule":
        for retained in metadata.get("submodule_states", []):
            if retained["path_b64url"] == entry["path_b64url"]:
                return b64url_decode(retained["state_b64url"])
        raise SnapshotError(f"missing retained submodule state for {entry['path_b64url']}")
    raise SnapshotError(f"unknown manifest entry kind: {entry['kind']}")


def verify(args: argparse.Namespace) -> dict[str, Any]:
    packet, manifest_bytes, manifest, metadata, expected_target = read_packet(args.packet_dir)
    actual_target = "sha256:" + digest(manifest_bytes)
    if actual_target != expected_target:
        raise SnapshotError(f"target id mismatch: expected {expected_target}, got {actual_target}")
    if canonical_json(manifest) != manifest_bytes:
        raise SnapshotError("manifest is not in canonical form")
    for artifact in manifest["artifacts"]:
        filename = ARTIFACT_FILES.get(artifact["kind"])
        if filename is None:
            raise SnapshotError(f"unknown artifact kind: {artifact['kind']}")
        data = (packet / filename).read_bytes()
        if len(data) != artifact["length"] or digest(data) != artifact["sha256"]:
            raise SnapshotError(f"artifact mismatch: {filename}")
    snapshot = packet / "snapshot"
    snapshot_head = resolve_commit(snapshot, "HEAD")
    if snapshot_head != manifest["head_sha"]:
        raise SnapshotError("snapshot HEAD does not match manifest")
    actual_untracked = raw_untracked_paths(snapshot)
    expected_untracked = sorted(
        b64url_decode(entry["path_b64url"])
        for entry in manifest["entries"]
        if entry["kind"] == "untracked"
    )
    if actual_untracked != expected_untracked:
        raise SnapshotError("snapshot untracked files do not match manifest")
    if raw_ignored_paths(snapshot):
        raise SnapshotError("snapshot contains unexpected ignored files")
    if manifest["target_kind"] == "local":
        live_artifacts = {
            "cached_diff": run_git(
                snapshot, ["diff", "--cached", "--binary", "--full-index", "--no-ext-diff"]
            ),
            "unstaged_diff": run_git(
                snapshot, ["diff", "--binary", "--full-index", "--no-ext-diff"]
            ),
        }
        for name, data in live_artifacts.items():
            if data != (packet / ARTIFACT_FILES[name]).read_bytes():
                raise SnapshotError(f"snapshot does not reproduce {name}")
    else:
        if run_git(snapshot, ["diff", "--binary", "--full-index", "--no-ext-diff"]):
            raise SnapshotError("snapshot worktree differs from committed target")
        if run_git(
            snapshot,
            ["diff", "--cached", "--binary", "--full-index", "--no-ext-diff"],
        ):
            raise SnapshotError("snapshot index differs from committed target")
    for entry in manifest["entries"]:
        content = entry_content(snapshot, entry, metadata)
        if len(content) != entry["size"] or digest(content) != entry["sha256"]:
            raise SnapshotError(f"entry mismatch: {entry['path_b64url']}")
    return {"snapshot_root": os.fspath(snapshot), "status": "ok", "target_id": expected_target}


def compare_live(args: argparse.Namespace) -> dict[str, Any]:
    _, _, _, metadata, expected_target = read_packet(args.packet_dir)
    repo = resolve_repo(metadata["repo_root"])
    if metadata["kind"] == "local":
        base = head = merge_base = None
    else:
        base = metadata.get("base_input") or metadata["base_sha"]
        head = metadata.get("head_input") or metadata["head_sha"]
        merge_base = None
    manifest, _, _, _ = build_target(repo, metadata["kind"], base, head, merge_base)
    live_target = "sha256:" + digest(canonical_json(manifest))
    return {
        "drifted": live_target != expected_target,
        "live_target_id": live_target,
        "target_id": expected_target,
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    subcommands = result.add_subparsers(dest="command", required=True)

    freeze_parser = subcommands.add_parser("freeze", help="freeze a review target")
    freeze_parser.add_argument("--repo", required=True)
    freeze_parser.add_argument(
        "--kind", required=True, choices=("local", "commit", "branch", "pr", "range")
    )
    freeze_parser.add_argument("--base")
    freeze_parser.add_argument("--head")
    freeze_parser.add_argument("--merge-base")
    freeze_parser.add_argument("--output")
    freeze_parser.set_defaults(handler=freeze)

    verify_parser = subcommands.add_parser("verify", help="verify retained packet artifacts")
    verify_parser.add_argument("--packet-dir", required=True)
    verify_parser.set_defaults(handler=verify)

    compare_parser = subcommands.add_parser(
        "compare-live", help="compare the mutable source with the frozen packet"
    )
    compare_parser.add_argument("--packet-dir", required=True)
    compare_parser.set_defaults(handler=compare_live)
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        output = args.handler(args)
    except (OSError, ValueError, SnapshotError, json.JSONDecodeError) as error:
        print(f"review_snapshot: {error}", file=sys.stderr)
        return 2
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
