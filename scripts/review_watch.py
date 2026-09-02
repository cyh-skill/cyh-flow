#!/usr/bin/env python3
"""Poll GitHub PR activity without involving the model until something changes."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import re
import subprocess
import tempfile
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable


SCHEMA_VERSION = 1
AUTO_MARKER = "<!-- cyh-flow-review-auto:"
PR_URL_RE = re.compile(
    r"^https://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/pull/(?P<number>\d+)/?$"
)
PR_REF_RE = re.compile(
    r"^(?P<owner>[^/\s]+)/(?P<repo>[^#\s]+)#(?P<number>\d+)$"
)
PR_NUMBER_RE = re.compile(r"^#?(?P<number>\d+)$")


class GitHubQueryError(RuntimeError):
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


Runner = Callable[[list[str]], Any]


def canonical_digest(value: Any) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def default_runner(arguments: list[str]) -> Any:
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
        raise GitHubQueryError("authenticated gh CLI is not available") from error
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "unknown gh error"
        raise GitHubQueryError(f"gh exited {result.returncode}: {message}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise GitHubQueryError("gh returned malformed JSON") from error


def resolve_repo(runner: Runner) -> str:
    payload = runner(["repo", "view", "--json", "nameWithOwner"])
    value = payload.get("nameWithOwner") if isinstance(payload, dict) else None
    if not isinstance(value, str) or "/" not in value:
        raise GitHubQueryError("cannot resolve the current GitHub repository")
    return value


def parse_target(value: str, repo: str | None, runner: Runner) -> Target:
    match = PR_URL_RE.fullmatch(value) or PR_REF_RE.fullmatch(value)
    if match:
        return Target(
            owner=match.group("owner"),
            repo=match.group("repo"),
            number=int(match.group("number")),
        )

    match = PR_NUMBER_RE.fullmatch(value)
    if not match:
        raise ValueError(
            "target must be a GitHub PR URL, OWNER/REPO#NUMBER, or PR number"
        )
    name_with_owner = repo or resolve_repo(runner)
    parts = name_with_owner.split("/", 1)
    if len(parts) != 2 or not all(parts):
        raise ValueError("--repo must use OWNER/REPO")
    return Target(parts[0], parts[1], int(match.group("number")))


def paged_list(endpoint: str, runner: Runner) -> list[dict[str, Any]]:
    payload = runner(["api", "--paginate", "--slurp", endpoint])
    if not isinstance(payload, list):
        raise GitHubQueryError(f"expected a paginated list from {endpoint}")
    pages = payload if payload and all(isinstance(item, list) for item in payload) else [payload]
    records: list[dict[str, Any]] = []
    for page in pages:
        if not isinstance(page, list):
            raise GitHubQueryError(f"expected list pages from {endpoint}")
        records.extend(item for item in page if isinstance(item, dict))
    return records


def actor(record: dict[str, Any]) -> tuple[str, str]:
    user = record.get("user")
    if not isinstance(user, dict):
        return "", ""
    return str(user.get("login") or ""), str(user.get("type") or "")


def human_records(
    records: list[dict[str, Any]], viewer: str, kind: str
) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for record in records:
        login, actor_type = actor(record)
        if actor_type and actor_type != "User":
            continue
        body = str(record.get("body") or "")
        if login == viewer and AUTO_MARKER in body:
            continue
        record_id = str(record.get("id") or record.get("node_id") or "")
        if not record_id:
            continue
        visible = {
            "author": login,
            "body": body,
            "commit_id": record.get("commit_id"),
            "created_at": record.get("created_at") or record.get("submitted_at"),
            "dismissed_at": record.get("dismissed_at"),
            "line": record.get("line") or record.get("original_line"),
            "path": record.get("path"),
            "state": record.get("state"),
            "updated_at": record.get("updated_at"),
        }
        html_url = str(record.get("html_url") or "")
        result[record_id] = {
            "author": login,
            "kind": kind,
            "url": html_url,
            "digest": canonical_digest(visible),
        }
    return result


def fetch_review_threads(target: Target, runner: Runner) -> dict[str, dict[str, str]]:
    records: dict[str, dict[str, str]] = {}
    after: str | None = None
    while True:
        after_declaration = ",$after:String!" if after is not None else ""
        after_argument = ",after:$after" if after is not None else ""
        query = f"""
query($owner:String!,$repo:String!,$number:Int!{after_declaration}) {{
  repository(owner:$owner,name:$repo) {{
    pullRequest(number:$number) {{
      reviewThreads(first:100{after_argument}) {{
        nodes {{ id isResolved isOutdated comments(last:1) {{ nodes {{ id updatedAt body url author {{ login __typename }} }} }} }}
        pageInfo {{ hasNextPage endCursor }}
      }}
    }}
  }}
}}
""".strip()
        arguments = [
            "api",
            "graphql",
            "-f",
            f"query={query}",
            "-f",
            f"owner={target.owner}",
            "-f",
            f"repo={target.repo}",
            "-F",
            f"number={target.number}",
        ]
        if after is not None:
            arguments.extend(["-f", f"after={after}"])
        payload = runner(arguments)
        try:
            connection = payload["data"]["repository"]["pullRequest"]["reviewThreads"]
        except (KeyError, TypeError) as error:
            raise GitHubQueryError("GitHub did not return review thread data") from error
        for thread in connection.get("nodes") or []:
            if not isinstance(thread, dict) or not thread.get("id"):
                continue
            comments = ((thread.get("comments") or {}).get("nodes") or [])
            last_comment = comments[-1] if comments else {}
            author = last_comment.get("author") or {}
            visible = {
                "is_resolved": thread.get("isResolved"),
                "is_outdated": thread.get("isOutdated"),
                "last_comment_id": last_comment.get("id"),
                "last_comment_updated_at": last_comment.get("updatedAt"),
                "last_comment_body": last_comment.get("body"),
            }
            records[str(thread["id"])] = {
                "author": str(author.get("login") or ""),
                "kind": "review_thread",
                "url": str(last_comment.get("url") or ""),
                "digest": canonical_digest(visible),
            }
        page_info = connection.get("pageInfo") or {}
        if not page_info.get("hasNextPage"):
            return records
        after = page_info.get("endCursor")
        if not isinstance(after, str) or not after:
            raise GitHubQueryError("review thread pagination omitted endCursor")


def fetch_cursor(target: Target, viewer: str, runner: Runner) -> dict[str, Any]:
    prefix = f"repos/{target.owner}/{target.repo}"
    pr = runner(["api", f"{prefix}/pulls/{target.number}"])
    if not isinstance(pr, dict) or not isinstance(pr.get("head"), dict):
        raise GitHubQueryError("GitHub did not return pull request metadata")
    head_oid = str(pr["head"].get("sha") or "")
    if not head_oid:
        raise GitHubQueryError("pull request metadata omitted head SHA")

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            "issue_comments": executor.submit(
                paged_list,
                f"{prefix}/issues/{target.number}/comments?per_page=100",
                runner,
            ),
            "reviews": executor.submit(
                paged_list,
                f"{prefix}/pulls/{target.number}/reviews?per_page=100",
                runner,
            ),
            "review_comments": executor.submit(
                paged_list,
                f"{prefix}/pulls/{target.number}/comments?per_page=100",
                runner,
            ),
            "review_threads": executor.submit(fetch_review_threads, target, runner),
        }
        results = {name: future.result() for name, future in futures.items()}

    issue_comments = results["issue_comments"]
    reviews = results["reviews"]
    review_comments = results["review_comments"]
    requested_users = [
        user.get("login")
        for user in pr.get("requested_reviewers") or []
        if isinstance(user, dict)
    ]
    requested_teams = [
        team.get("slug")
        for team in pr.get("requested_teams") or []
        if isinstance(team, dict)
    ]
    pr_core = {
        "base_oid": (pr.get("base") or {}).get("sha"),
        "body": pr.get("body"),
        "draft": pr.get("draft"),
        "merged_at": pr.get("merged_at"),
        "requested_reviewers": sorted(str(item) for item in requested_users if item),
        "requested_teams": sorted(str(item) for item in requested_teams if item),
        "state": pr.get("state"),
        "title": pr.get("title"),
    }
    cursor: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "target": target.slug,
        "captured_at": datetime.now(UTC).isoformat(),
        "head_oid": head_oid,
        "pr": {"digest": canonical_digest(pr_core), "state": str(pr.get("state") or "")},
        "issue_comments": human_records(issue_comments, viewer, "issue_comment"),
        "reviews": human_records(reviews, viewer, "review"),
        "review_comments": human_records(review_comments, viewer, "review_comment"),
        "review_threads": results["review_threads"],
    }
    return cursor


def collection_changes(
    source: str, before: dict[str, Any], after: dict[str, Any]
) -> list[dict[str, str]]:
    changes: list[dict[str, str]] = []
    before_ids = set(before)
    after_ids = set(after)
    for record_id in sorted(after_ids - before_ids):
        record = after[record_id]
        changes.append(
            {
                "source": source,
                "change": "added",
                "id": record_id,
                "author": str(record.get("author") or ""),
                "url": str(record.get("url") or ""),
            }
        )
    for record_id in sorted(before_ids - after_ids):
        record = before[record_id]
        changes.append(
            {
                "source": source,
                "change": "deleted",
                "id": record_id,
                "author": str(record.get("author") or ""),
                "url": str(record.get("url") or ""),
            }
        )
    for record_id in sorted(before_ids & after_ids):
        if before[record_id].get("digest") != after[record_id].get("digest"):
            record = after[record_id]
            changes.append(
                {
                    "source": source,
                    "change": "updated",
                    "id": record_id,
                    "author": str(record.get("author") or ""),
                    "url": str(record.get("url") or ""),
                }
            )
    return changes


def diff_cursors(before: dict[str, Any], after: dict[str, Any]) -> list[dict[str, str]]:
    if before.get("target") != after.get("target"):
        raise ValueError("cursor target does not match the requested pull request")
    changes: list[dict[str, str]] = []
    if before.get("head_oid") != after.get("head_oid"):
        changes.append(
            {
                "source": "head",
                "change": "updated",
                "before": str(before.get("head_oid") or ""),
                "after": str(after.get("head_oid") or ""),
            }
        )
    if (before.get("pr") or {}).get("digest") != (after.get("pr") or {}).get("digest"):
        changes.append({"source": "pull_request", "change": "updated"})
    for source in ("issue_comments", "reviews", "review_comments", "review_threads"):
        changes.extend(
            collection_changes(source, before.get(source) or {}, after.get(source) or {})
        )
    return changes


def load_cursor(path: Path | None, target: Target) -> dict[str, Any] | None:
    if path is None or not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("cursor must be a JSON object")
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported cursor schema version")
    if payload.get("target") != target.slug:
        raise ValueError("cursor target does not match the requested pull request")
    return payload


def write_cursor(path: Path | None, cursor: dict[str, Any]) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    )
    temporary = Path(handle.name)
    try:
        with handle:
            json.dump(cursor, handle, ensure_ascii=False, sort_keys=True)
            handle.write("\n")
        os.chmod(temporary, 0o600)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True), flush=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Wait for GitHub PR activity using gh, without model polling."
    )
    parser.add_argument("target", help="PR URL, OWNER/REPO#NUMBER, or PR number")
    parser.add_argument("--repo", help="OWNER/REPO for a numeric target")
    parser.add_argument("--state-file", type=Path, help="optional temp cursor file")
    parser.add_argument("--interval", type=float, default=30.0, help="poll seconds")
    parser.add_argument(
        "--max-errors",
        type=int,
        default=5,
        help="consecutive gh errors before reporting blocked",
    )
    return parser


def main(argv: list[str] | None = None, runner: Runner = default_runner) -> int:
    arguments = build_parser().parse_args(argv)
    if arguments.interval <= 0:
        raise ValueError("--interval must be positive")
    if arguments.max_errors <= 0:
        raise ValueError("--max-errors must be positive")

    target = parse_target(arguments.target, arguments.repo, runner)
    user_payload = runner(["api", "user"])
    viewer = str(user_payload.get("login") or "") if isinstance(user_payload, dict) else ""
    if not viewer:
        raise GitHubQueryError("cannot resolve the authenticated GitHub user")

    baseline = load_cursor(arguments.state_file, target)
    consecutive_errors = 0
    while True:
        try:
            current = fetch_cursor(target, viewer, runner)
            consecutive_errors = 0
        except (GitHubQueryError, OSError, ValueError) as error:
            consecutive_errors += 1
            if consecutive_errors >= arguments.max_errors:
                emit(
                    {
                        "status": "blocked",
                        "target": target.slug,
                        "error": str(error),
                        "consecutive_errors": consecutive_errors,
                    }
                )
                return 2
            time.sleep(min(arguments.interval * (2 ** (consecutive_errors - 1)), 300.0))
            continue

        if baseline is None:
            baseline = current
            write_cursor(arguments.state_file, baseline)
            emit(
                {
                    "status": "ready",
                    "target": target.slug,
                    "head_oid": baseline["head_oid"],
                }
            )
        else:
            changes = diff_cursors(baseline, current)
            baseline = current
            write_cursor(arguments.state_file, baseline)
            if changes:
                emit(
                    {
                        "status": "changed",
                        "target": target.slug,
                        "head_oid": baseline["head_oid"],
                        "changes": changes,
                    }
                )
                return 0
        time.sleep(arguments.interval)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        emit({"status": "stopped"})
        raise SystemExit(130) from None
    except (GitHubQueryError, ValueError, json.JSONDecodeError) as error:
        emit({"status": "blocked", "error": str(error)})
        raise SystemExit(2) from error
