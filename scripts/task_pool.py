#!/usr/bin/env python3
"""Maintain CYH Flow's Markdown task pool with atomic document-backed claims."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterator


TASK_START_RE = re.compile(
    r"^<!-- cyh-flow-task:(?P<id>TASK-\d{8}-\d{3}) -->$", re.MULTILINE
)
TASK_ID_RE = re.compile(r"^TASK-(?P<date>\d{8})-(?P<sequence>\d{3})$")
DAY_FILE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}\.md$")
IMAGE_SUFFIXES = {
    ".bmp",
    ".gif",
    ".heic",
    ".heif",
    ".jpeg",
    ".jpg",
    ".png",
    ".tif",
    ".tiff",
    ".webp",
}
FIELDS = (
    "状态",
    "类型",
    "来源",
    "创建时间",
    "更新时间",
    "领取人",
    "领取时间",
    "完成时间",
)


class PoolError(RuntimeError):
    pass


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def local_day() -> str:
    return date.today().isoformat()


def one_line(value: Any, *, fallback: str = "—") -> str:
    text = " ".join(str(value or "").split())
    return text or fallback


def markdown_body(value: Any) -> str:
    text = str(value or "").strip()
    return text or "—"


def markdown_label(value: Any) -> str:
    return one_line(value, fallback="用户截图").replace("[", "\\[").replace("]", "\\]")


@contextmanager
def pool_lock(pool: Path) -> Iterator[None]:
    pool.mkdir(parents=True, exist_ok=True)
    identity = hashlib.sha256(str(pool.resolve()).encode("utf-8")).hexdigest()[:24]
    lock_path = Path(tempfile.gettempdir()) / f"cyh-flow-task-pool-{identity}.lock"
    with lock_path.open("a+", encoding="utf-8") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def day_files(pool: Path) -> list[Path]:
    if not pool.exists():
        return []
    return sorted(path for path in pool.iterdir() if path.is_file() and DAY_FILE_RE.match(path.name))


def read_field(segment: str, name: str) -> str:
    match = re.search(rf"^- {re.escape(name)}：(.*)$", segment, re.MULTILINE)
    if not match:
        raise PoolError(f"task is missing required field: {name}")
    return match.group(1).strip()


def replace_field(segment: str, name: str, value: str) -> str:
    pattern = re.compile(rf"^- {re.escape(name)}：.*$", re.MULTILINE)
    if not pattern.search(segment):
        raise PoolError(f"task is missing required field: {name}")
    return pattern.sub(f"- {name}：{one_line(value)}", segment, count=1)


def append_history(segment: str, entry: str) -> str:
    if "### 处理记录" not in segment:
        raise PoolError("task is missing handling history")
    return f"{segment.rstrip()}\n- {one_line(entry)}\n\n"


def parse_tasks(path: Path, content: str) -> list[dict[str, Any]]:
    matches = list(TASK_START_RE.finditer(content))
    tasks: list[dict[str, Any]] = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
        segment = content[start:end]
        task_id = match.group("id")
        heading = re.search(
            rf"^## {re.escape(task_id)} · (?P<title>.+)$", segment, re.MULTILINE
        )
        if not heading:
            raise PoolError(f"{path}: {task_id} is missing its heading")
        fields = {name: read_field(segment, name) for name in FIELDS}
        tasks.append(
            {
                "id": task_id,
                "title": heading.group("title").strip(),
                "path": path,
                "start": start,
                "end": end,
                "segment": segment,
                **fields,
            }
        )
    return tasks


def all_tasks(pool: Path) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    for path in day_files(pool):
        content = path.read_text(encoding="utf-8")
        tasks.extend(parse_tasks(path, content))
    return tasks


def replace_task(path: Path, content: str, task: dict[str, Any], segment: str) -> None:
    updated = f"{content[:task['start']]}{segment}{content[task['end'] :]}"
    atomic_write(path, updated)


def validate_day(value: str) -> str:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date().isoformat()
    except ValueError as error:
        raise PoolError(f"invalid date {value!r}; expected YYYY-MM-DD") from error


def load_input(source: str) -> list[dict[str, Any]]:
    if source == "-":
        payload = json.load(sys.stdin)
    else:
        with Path(source).expanduser().open(encoding="utf-8") as handle:
            payload = json.load(handle)
    items = payload if isinstance(payload, list) else [payload]
    if not items or not all(isinstance(item, dict) for item in items):
        raise PoolError("input must be a JSON object or a non-empty array of objects")
    return items


def normalize_screenshots(value: Any) -> list[dict[str, Any]]:
    if value in (None, "", []):
        return []
    entries = value if isinstance(value, list) else [value]
    screenshots: list[dict[str, Any]] = []
    for entry in entries:
        if isinstance(entry, str):
            raw_path = entry
            label = "用户截图"
            source = "用户提供"
        elif isinstance(entry, dict):
            raw_path = entry.get("path")
            label = markdown_label(entry.get("label"))
            source = one_line(entry.get("source"), fallback="用户提供")
        else:
            raise PoolError("each screenshots entry must be a path or an object")
        if not raw_path:
            raise PoolError("screenshot path is required")
        path = Path(str(raw_path)).expanduser().resolve()
        if not path.is_file():
            raise PoolError(f"screenshot does not exist or is not a file: {path}")
        suffix = path.suffix.lower()
        if suffix not in IMAGE_SUFFIXES:
            raise PoolError(f"unsupported screenshot extension {suffix or '<none>'}: {path}")
        screenshots.append(
            {"path": path, "label": label, "source": source, "suffix": suffix}
        )
    return screenshots


def normalize_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for item in items:
        title = one_line(item.get("title"), fallback="")
        if not title:
            raise PoolError("every task requires a non-empty title")
        normalized.append(
            {
                "title": title,
                "type": one_line(item.get("type"), fallback="task"),
                "source": one_line(item.get("source"), fallback="用户输入"),
                "content": markdown_body(item.get("content")),
                "analysis": markdown_body(item.get("analysis")),
                "acceptance": markdown_body(item.get("acceptance")),
                "screenshots": normalize_screenshots(item.get("screenshots")),
            }
        )
    return normalized


def next_sequence(pool: Path, day_compact: str) -> int:
    maximum = 0
    for task in all_tasks(pool):
        match = TASK_ID_RE.match(task["id"])
        if match and match.group("date") == day_compact:
            maximum = max(maximum, int(match.group("sequence")))
    return maximum + 1


def render_task(
    task_id: str,
    item: dict[str, Any],
    timestamp: str,
    screenshot_links: list[dict[str, str]],
) -> str:
    if screenshot_links:
        evidence = "\n\n".join(
            (
                f"![{link['label']}]({link['path']})\n\n"
                f"- 截图来源：{link['source']}；收录时间：{timestamp}；原图：`{link['path']}`"
            )
            for link in screenshot_links
        )
    else:
        evidence = "—"
    return (
        f"<!-- cyh-flow-task:{task_id} -->\n"
        f"## {task_id} · {item['title']}\n\n"
        "- 状态：pending\n"
        f"- 类型：{item['type']}\n"
        f"- 来源：{item['source']}\n"
        f"- 创建时间：{timestamp}\n"
        f"- 更新时间：{timestamp}\n"
        "- 领取人：—\n"
        "- 领取时间：—\n"
        "- 完成时间：—\n\n"
        f"### 内容\n\n{item['content']}\n\n"
        f"### 分析\n\n{item['analysis']}\n\n"
        f"### 验收\n\n{item['acceptance']}\n\n"
        f"### 截图\n\n{evidence}\n\n"
        "### 处理记录\n\n"
        f"- {timestamp} 收录任务\n\n"
    )


def command_add(args: argparse.Namespace) -> int:
    pool = Path(args.pool).expanduser()
    items = normalize_items(load_input(args.input))
    day = validate_day(args.date or local_day())
    day_compact = day.replace("-", "")
    timestamp = now_iso()
    added: list[dict[str, str]] = []
    created_asset_dirs: list[Path] = []
    with pool_lock(pool):
        sequence = next_sequence(pool, day_compact)
        sections: list[str] = []
        try:
            for item in items:
                if sequence > 999:
                    raise PoolError(f"daily task limit reached for {day}")
                task_id = f"TASK-{day_compact}-{sequence:03d}"
                sequence += 1
                screenshot_links: list[dict[str, str]] = []
                if item["screenshots"]:
                    asset_dir = pool / "assets" / task_id
                    if asset_dir.exists():
                        raise PoolError(f"asset directory already exists: {asset_dir}")
                    asset_dir.mkdir(parents=True)
                    created_asset_dirs.append(asset_dir)
                    for index, screenshot in enumerate(item["screenshots"], start=1):
                        destination = asset_dir / f"{index:03d}{screenshot['suffix']}"
                        shutil.copy2(screenshot["path"], destination)
                        screenshot_links.append(
                            {
                                "label": screenshot["label"],
                                "source": screenshot["source"],
                                "path": f"assets/{task_id}/{destination.name}",
                            }
                        )
                sections.append(render_task(task_id, item, timestamp, screenshot_links))
                added.append(
                    {
                        "id": task_id,
                        "title": item["title"],
                        "file": str((pool / f"{day}.md").resolve()),
                    }
                )

            path = pool / f"{day}.md"
            if path.exists():
                content = path.read_text(encoding="utf-8").rstrip() + "\n\n"
            else:
                content = f"# Task Pool · {day}\n\n"
            atomic_write(path, content + "".join(sections))
        except Exception:
            for asset_dir in reversed(created_asset_dirs):
                shutil.rmtree(asset_dir, ignore_errors=True)
            raise
    print(json.dumps({"added": added}, ensure_ascii=False, indent=2))
    return 0


def command_claim(args: argparse.Namespace) -> int:
    pool = Path(args.pool).expanduser()
    agent = one_line(args.agent, fallback="")
    if not agent:
        raise PoolError("agent identity is required")
    with pool_lock(pool):
        candidates = all_tasks(pool)
        if args.task_id:
            candidates = [task for task in candidates if task["id"] == args.task_id]
            if not candidates:
                raise PoolError(f"task not found: {args.task_id}")
        task = next((item for item in candidates if item["状态"] == "pending"), None)
        if task is None:
            reason = "selected task is not pending" if args.task_id else "no pending task"
            print(json.dumps({"claimed": False, "reason": reason}, ensure_ascii=False))
            return 3
        path = task["path"]
        content = path.read_text(encoding="utf-8")
        timestamp = now_iso()
        segment = replace_field(task["segment"], "状态", "doing")
        segment = replace_field(segment, "领取人", agent)
        segment = replace_field(segment, "领取时间", timestamp)
        segment = replace_field(segment, "更新时间", timestamp)
        segment = append_history(segment, f"{timestamp} {agent} 领取任务")
        replace_task(path, content, task, segment)
    print(
        json.dumps(
            {
                "claimed": True,
                "id": task["id"],
                "title": task["title"],
                "file": str(path.resolve()),
                "agent": agent,
                "claimed_at": timestamp,
                "markdown": segment.strip(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def note_from_args(args: argparse.Namespace) -> str:
    if args.note_file:
        return one_line(Path(args.note_file).expanduser().read_text(encoding="utf-8"), fallback="")
    return one_line(args.note, fallback="")


def command_finish(args: argparse.Namespace) -> int:
    pool = Path(args.pool).expanduser()
    agent = one_line(args.agent, fallback="")
    note = note_from_args(args)
    if not agent:
        raise PoolError("agent identity is required")
    if not note:
        raise PoolError("a non-empty --note or --note-file is required")
    with pool_lock(pool):
        matches = [task for task in all_tasks(pool) if task["id"] == args.task_id]
        if not matches:
            raise PoolError(f"task not found: {args.task_id}")
        task = matches[0]
        if task["状态"] != "doing":
            raise PoolError(f"task {args.task_id} is {task['状态']}, not doing")
        if task["领取人"] != agent:
            raise PoolError(
                f"task {args.task_id} is owned by {task['领取人']}, not {agent}"
            )
        path = task["path"]
        content = path.read_text(encoding="utf-8")
        timestamp = now_iso()
        segment = replace_field(task["segment"], "状态", args.status)
        segment = replace_field(segment, "更新时间", timestamp)
        if args.status == "done":
            segment = replace_field(segment, "完成时间", timestamp)
        action = "完成任务" if args.status == "done" else "等待用户"
        segment = append_history(segment, f"{timestamp} {agent} {action}：{note}")
        replace_task(path, content, task, segment)
    print(
        json.dumps(
            {
                "updated": True,
                "id": task["id"],
                "status": args.status,
                "file": str(path.resolve()),
                "agent": agent,
                "updated_at": timestamp,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def command_reopen(args: argparse.Namespace) -> int:
    pool = Path(args.pool).expanduser()
    agent = one_line(args.agent, fallback="")
    note = note_from_args(args)
    if not agent:
        raise PoolError("agent identity is required")
    if not note:
        raise PoolError("a non-empty --note or --note-file is required")
    with pool_lock(pool):
        matches = [task for task in all_tasks(pool) if task["id"] == args.task_id]
        if not matches:
            raise PoolError(f"task not found: {args.task_id}")
        task = matches[0]
        if task["状态"] != "waiting":
            raise PoolError(f"task {args.task_id} is {task['状态']}, not waiting")
        path = task["path"]
        content = path.read_text(encoding="utf-8")
        timestamp = now_iso()
        segment = replace_field(task["segment"], "状态", "pending")
        segment = replace_field(segment, "更新时间", timestamp)
        segment = replace_field(segment, "领取人", "—")
        segment = replace_field(segment, "领取时间", "—")
        segment = append_history(segment, f"{timestamp} {agent} 根据用户答复重新开放：{note}")
        replace_task(path, content, task, segment)
    print(
        json.dumps(
            {
                "updated": True,
                "id": task["id"],
                "status": "pending",
                "file": str(path.resolve()),
                "agent": agent,
                "updated_at": timestamp,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def command_list(args: argparse.Namespace) -> int:
    pool = Path(args.pool).expanduser()
    with pool_lock(pool):
        tasks = all_tasks(pool)
    if args.status:
        tasks = [task for task in tasks if task["状态"] == args.status]
    output = [
        {
            "id": task["id"],
            "title": task["title"],
            "status": task["状态"],
            "owner": task["领取人"],
            "claimed_at": task["领取时间"],
            "file": str(task["path"].resolve()),
        }
        for task in tasks
    ]
    print(json.dumps({"tasks": output}, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pool", required=True, help="path to .cyh-flow/tasks")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="append tasks to a dated Markdown file")
    add_parser.add_argument("--input", required=True, help="JSON file path, or - for stdin")
    add_parser.add_argument("--date", help="intake date in YYYY-MM-DD")
    add_parser.set_defaults(handler=command_add)

    claim_parser = subparsers.add_parser("claim", help="atomically claim one pending task")
    claim_parser.add_argument("--agent", required=True, help="stable unique Agent identity")
    claim_parser.add_argument("--task-id", help="claim this task instead of the oldest pending task")
    claim_parser.set_defaults(handler=command_claim)

    finish_parser = subparsers.add_parser("finish", help="mark an owned doing task done or waiting")
    finish_parser.add_argument("--task-id", required=True)
    finish_parser.add_argument("--agent", required=True)
    finish_parser.add_argument("--status", choices=("done", "waiting"), required=True)
    finish_parser.add_argument("--note")
    finish_parser.add_argument("--note-file")
    finish_parser.set_defaults(handler=command_finish)

    reopen_parser = subparsers.add_parser("reopen", help="return a waiting task to pending")
    reopen_parser.add_argument("--task-id", required=True)
    reopen_parser.add_argument("--agent", required=True)
    reopen_parser.add_argument("--note")
    reopen_parser.add_argument("--note-file")
    reopen_parser.set_defaults(handler=command_reopen)

    list_parser = subparsers.add_parser("list", help="list task status from the Markdown pool")
    list_parser.add_argument("--status", choices=("pending", "doing", "waiting", "done"))
    list_parser.set_defaults(handler=command_list)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.handler(args)
    except (PoolError, json.JSONDecodeError, OSError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
