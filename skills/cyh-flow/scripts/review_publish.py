#!/usr/bin/env python3
"""Idempotently publish and verify a cyh-flow GitHub PR review comment."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol


PR_URL_RE = re.compile(
    r"^https://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/pull/(?P<number>\d+)/?$"
)
PR_REF_RE = re.compile(
    r"^(?P<owner>[^/\s]+)/(?P<repo>[^#\s]+)#(?P<number>\d+)$"
)
COMMENT_URL_RE = re.compile(r"/pull/\d+#issuecomment-(?P<id>\d+)$")


class PublishError(RuntimeError):
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
    def url(self) -> str:
        return f"https://github.com/{self.owner}/{self.repo}/pull/{self.number}"


class Runner(Protocol):
    def json(self, arguments: list[str]) -> Any: ...

    def text(self, arguments: list[str], *, check: bool = True) -> tuple[int, str]: ...


class GhRunner:
    def text(self, arguments: list[str], *, check: bool = True) -> tuple[int, str]:
        command = ["gh", *arguments]
        try:
            result = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
        except FileNotFoundError as error:
            raise PublishError("authenticated gh CLI is unavailable") from error
        if check and result.returncode != 0:
            message = result.stderr.strip() or result.stdout.strip() or "unknown gh error"
            raise PublishError(f"gh exited {result.returncode}: {message}")
        output = result.stdout if result.stdout else result.stderr
        return result.returncode, output

    def json(self, arguments: list[str]) -> Any:
        _, raw = self.text(arguments)
        try:
            return json.loads(raw)
        except json.JSONDecodeError as error:
            raise PublishError("gh returned malformed JSON") from error


def parse_target(value: str) -> Target:
    match = PR_URL_RE.fullmatch(value) or PR_REF_RE.fullmatch(value)
    if not match:
        raise ValueError("target must be a GitHub PR URL or OWNER/REPO#NUMBER")
    return Target(match.group("owner"), match.group("repo"), int(match.group("number")))


def canonical_visible_body(path: Path) -> str:
    body = path.read_text(encoding="utf-8")
    if not body.strip():
        raise PublishError("body file must contain visible review text")
    if any(
        marker in body
        for marker in (
            "<!-- cyh-flow-review:",
            "<!-- cyh-flow-review-auto:",
            "<!-- cyh-flow-re-review:",
        )
    ):
        raise PublishError("body file already contains a cyh-flow review marker")
    return body.rstrip("\r\n") + "\n"


def build_marker(target: Target, visible: str, mode: str, head_oid: str | None) -> tuple[str, str]:
    digest = hashlib.sha256(visible.encode("utf-8")).hexdigest()
    if mode == "ordinary":
        if head_oid is not None:
            raise PublishError("--head-oid is valid only in head-bound review modes")
        marker = f"<!-- cyh-flow-review:{target.slug}:{digest} -->"
    elif mode in {"auto", "re-review"}:
        if not head_oid or not re.fullmatch(r"[0-9a-fA-F]{7,64}", head_oid):
            raise PublishError(f"{mode} mode requires --head-oid with a Git object ID")
        marker_name = "cyh-flow-review-auto" if mode == "auto" else "cyh-flow-re-review"
        marker = f"<!-- {marker_name}:{target.slug}:{head_oid.lower()}:{digest} -->"
    else:
        raise PublishError(f"unsupported review mode: {mode}")
    return marker, digest


def flatten_pages(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, list):
        raise PublishError("comment query did not return a list")
    pages = payload if payload and all(isinstance(item, list) for item in payload) else [payload]
    records: list[dict[str, Any]] = []
    for page in pages:
        if not isinstance(page, list):
            raise PublishError("comment query returned malformed pages")
        records.extend(item for item in page if isinstance(item, dict))
    return records


def find_existing(target: Target, marker: str, login: str, runner: Runner) -> dict[str, Any] | None:
    endpoint = f"repos/{target.owner}/{target.repo}/issues/{target.number}/comments?per_page=100"
    payload = runner.json(["api", "--paginate", "--slurp", endpoint])
    matches = []
    for comment in flatten_pages(payload):
        user = comment.get("user") if isinstance(comment.get("user"), dict) else {}
        if marker in str(comment.get("body", "")) and user.get("login") == login:
            matches.append(comment)
    if len(matches) > 1:
        raise PublishError("multiple authenticated comments contain the same marker")
    return matches[0] if matches else None


def comment_id(comment: dict[str, Any]) -> int:
    value = comment.get("id")
    if isinstance(value, int):
        return value
    url = str(comment.get("html_url", ""))
    match = COMMENT_URL_RE.search(url)
    if not match:
        raise PublishError("cannot resolve posted comment ID")
    return int(match.group("id"))


def verify_comment(
    target: Target,
    value: dict[str, Any],
    login: str,
    expected_body: str,
    runner: Runner,
) -> dict[str, Any]:
    identifier = comment_id(value)
    actual = runner.json(
        ["api", f"repos/{target.owner}/{target.repo}/issues/comments/{identifier}"]
    )
    if not isinstance(actual, dict):
        raise PublishError("comment readback is malformed")
    user = actual.get("user") if isinstance(actual.get("user"), dict) else {}
    if user.get("login") != login:
        raise PublishError("comment author does not match authenticated user")
    if actual.get("body") != expected_body:
        raise PublishError("comment body readback does not exactly match")
    url = actual.get("html_url")
    if not isinstance(url, str) or not url:
        raise PublishError("verified comment has no URL")
    return {"comment_id": identifier, "url": url}


def publish(
    target: Target,
    body_path: Path,
    mode: str,
    head_oid: str | None,
    runner: Runner,
) -> dict[str, Any]:
    visible = canonical_visible_body(body_path)
    marker, digest = build_marker(target, visible, mode, head_oid)
    full_body = f"{visible}{marker}\n"
    user = runner.json(["api", "user"])
    login = user.get("login") if isinstance(user, dict) else None
    if not isinstance(login, str) or not login:
        raise PublishError("cannot resolve authenticated GitHub user")

    existing = find_existing(target, marker, login, runner)
    status = "existing"
    if existing is None:
        temporary_path: str | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                prefix="cyh-flow-review-",
                suffix=".md",
                delete=False,
            ) as handle:
                os.chmod(handle.name, 0o600)
                handle.write(full_body)
                temporary_path = handle.name
            code, output = runner.text(
                ["pr", "comment", target.url, "--body-file", temporary_path], check=False
            )
            existing = find_existing(target, marker, login, runner)
            if existing is None:
                message = output.strip() or f"gh pr comment exited {code}"
                raise PublishError(f"comment was not found after delivery attempt: {message}")
            status = "posted"
        finally:
            if temporary_path is not None:
                Path(temporary_path).unlink(missing_ok=True)

    verified = verify_comment(target, existing, login, full_body, runner)
    return {
        "status": status,
        "target": target.slug,
        "mode": mode,
        "visible_body_sha256": digest,
        "marker": marker,
        **verified,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", help="GitHub PR URL or OWNER/REPO#NUMBER")
    parser.add_argument("--body-file", required=True, type=Path)
    parser.add_argument(
        "--mode", choices=("ordinary", "auto", "re-review"), default="ordinary"
    )
    parser.add_argument("--head-oid")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = publish(
            parse_target(args.target),
            args.body_file,
            args.mode,
            args.head_oid,
            GhRunner(),
        )
    except (OSError, PublishError, ValueError) as error:
        print(json.dumps({"status": "blocked", "error": str(error)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
