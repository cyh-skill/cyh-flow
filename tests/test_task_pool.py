from __future__ import annotations

import base64
import errno
import importlib.util
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "flow"
    / "scripts"
    / "task_pool.py"
)
ONE_PIXEL_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


def load_task_pool_module():
    spec = importlib.util.spec_from_file_location("cyh_flow_task_pool", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load task_pool.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


TASK_POOL = load_task_pool_module()


class TaskPoolTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.pool = self.root / ".cyh-flow" / "tasks"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_cli(
        self, *arguments: str, payload: object | None = None
    ) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["PYTHONIOENCODING"] = "cp1252"
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--pool", str(self.pool), *arguments],
            input=json.dumps(payload, ensure_ascii=False) if payload is not None else None,
            text=True,
            encoding="utf-8",
            errors="strict",
            capture_output=True,
            check=False,
            env=environment,
            timeout=30,
        )

    def add_tasks(self, count: int) -> list[str]:
        result = self.run_cli(
            "add",
            "--input",
            "-",
            "--date",
            "2026-09-01",
            payload=[{"title": f"任务 {index}"} for index in range(count)],
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return [item["id"] for item in json.loads(result.stdout)["added"]]

    def test_add_preserves_screenshot_and_embeds_relative_link(self) -> None:
        screenshot = self.root / "shot.png"
        screenshot.write_bytes(ONE_PIXEL_PNG)
        result = self.run_cli(
            "add",
            "--input",
            "-",
            "--date",
            "2026-09-01",
            payload={
                "title": "保留截图",
                "type": "change",
                "screenshots": [
                    {"path": str(screenshot), "label": "原始界面", "source": "用户附件"}
                ],
            },
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        task_id = json.loads(result.stdout)["added"][0]["id"]
        preserved = self.pool / "assets" / task_id / "001.png"
        self.assertEqual(preserved.read_bytes(), ONE_PIXEL_PNG)
        document = (self.pool / "2026-09-01.md").read_text(encoding="utf-8")
        self.assertIn(f"## {task_id} · 保留截图", document)
        self.assertIn(f"![原始界面](assets/{task_id}/001.png)", document)
        self.assertIn("- 截图来源：用户附件；收录时间：", document)
        self.assertIn("- 状态：pending", document)
        self.assertIn("- 领取人：—", document)

    def test_add_rejects_reserved_task_marker_without_mutating_pool(self) -> None:
        result = self.run_cli(
            "add",
            "--input",
            "-",
            "--date",
            "2026-09-01",
            payload={
                "title": "包含内部标记",
                "content": "before\n\n<!-- cyh-flow-task:TASK-20990101-001 -->\nafter",
            },
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("reserved cyh-flow task marker", result.stderr)
        self.assertFalse(self.pool.exists())

    def test_atomic_update_preserves_existing_document_mode(self) -> None:
        self.pool.mkdir(parents=True)
        document = self.pool / "2026-09-01.md"
        document.write_text("# Task Pool · 2026-09-01\n", encoding="utf-8")
        document.chmod(0o640)
        expected_mode = stat.S_IMODE(document.stat().st_mode)

        result = self.run_cli(
            "add",
            "--input",
            "-",
            "--date",
            "2026-09-01",
            payload={"title": "保留权限"},
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(stat.S_IMODE(document.stat().st_mode), expected_mode)

    def test_concurrent_agents_claim_unique_tasks(self) -> None:
        task_ids = set(self.add_tasks(8))

        def claim(index: int) -> subprocess.CompletedProcess[str]:
            return self.run_cli("claim", "--agent", f"agent-{index:02d}")

        with ThreadPoolExecutor(max_workers=16) as executor:
            results = list(executor.map(claim, range(16)))

        successful = [result for result in results if result.returncode == 0]
        empty = [result for result in results if result.returncode == 3]
        self.assertEqual(len(successful), 8)
        self.assertEqual(len(empty), 8)
        claimed_ids = {json.loads(result.stdout)["id"] for result in successful}
        self.assertEqual(claimed_ids, task_ids)
        self.assertEqual(len(claimed_ids), len(successful))

        listed = self.run_cli("list", "--status", "doing")
        self.assertEqual(listed.returncode, 0, listed.stderr)
        tasks = json.loads(listed.stdout)["tasks"]
        self.assertEqual(len(tasks), 8)
        self.assertEqual(len({task["owner"] for task in tasks}), 8)

    def test_unix_lock_backend_retains_flock_contract(self) -> None:
        calls: list[tuple[int, int]] = []
        fake_fcntl = SimpleNamespace(
            LOCK_EX=1,
            LOCK_UN=2,
            flock=lambda descriptor, operation: calls.append((descriptor, operation)),
        )
        lock_path = self.root / "unix.lock"

        with lock_path.open("a+b", buffering=0) as lock_file:
            with mock.patch.object(TASK_POOL, "_lock_backend_name", return_value="unix"):
                with mock.patch.object(TASK_POOL, "_load_lock_module", return_value=fake_fcntl):
                    with TASK_POOL._exclusive_file_lock(lock_file):
                        self.assertEqual(calls, [(lock_file.fileno(), fake_fcntl.LOCK_EX)])

        self.assertEqual(
            calls,
            [
                (calls[0][0], fake_fcntl.LOCK_EX),
                (calls[0][0], fake_fcntl.LOCK_UN),
            ],
        )

    def test_windows_lock_backend_imports_msvcrt_retries_and_unlocks(self) -> None:
        calls: list[tuple[int, int, int]] = []
        attempts = 0

        def locking(descriptor: int, operation: int, size: int) -> None:
            nonlocal attempts
            calls.append((descriptor, operation, size))
            if operation == 11:
                attempts += 1
                if attempts == 1:
                    raise OSError(errno.EACCES, "lock is held")

        fake_msvcrt = SimpleNamespace(LK_NBLCK=11, LK_UNLCK=12, locking=locking)
        lock_path = self.root / "windows.lock"

        with lock_path.open("a+b", buffering=0) as lock_file:
            with mock.patch.object(TASK_POOL, "_lock_backend_name", return_value="windows"):
                with mock.patch.object(
                    TASK_POOL, "_load_lock_module", return_value=fake_msvcrt
                ) as load_module:
                    with mock.patch.object(TASK_POOL.time, "sleep") as sleep:
                        with TASK_POOL._exclusive_file_lock(lock_file):
                            self.assertEqual(lock_path.stat().st_size, 1)
                            self.assertEqual(lock_file.tell(), 0)

            load_module.assert_called_once_with("msvcrt")
            sleep.assert_called_once_with(0.05)

        descriptor = calls[0][0]
        self.assertEqual(
            calls,
            [
                (descriptor, fake_msvcrt.LK_NBLCK, 1),
                (descriptor, fake_msvcrt.LK_NBLCK, 1),
                (descriptor, fake_msvcrt.LK_UNLCK, 1),
            ],
        )

    def test_windows_lock_backend_times_out_instead_of_waiting_forever(self) -> None:
        def locking(descriptor: int, operation: int, size: int) -> None:
            del descriptor, operation, size
            raise OSError(errno.EACCES, "lock is held")

        fake_msvcrt = SimpleNamespace(LK_NBLCK=11, locking=locking)
        lock_path = self.root / "windows-timeout.lock"

        with lock_path.open("a+b", buffering=0) as lock_file:
            with mock.patch.object(
                TASK_POOL.time, "monotonic", side_effect=(100.0, 131.0)
            ):
                with self.assertRaisesRegex(TASK_POOL.PoolError, "timed out after 30s"):
                    TASK_POOL._acquire_windows_lock(lock_file, fake_msvcrt)

    def test_claim_preserves_backslashes_in_agent_identity(self) -> None:
        task_id = self.add_tasks(1)[0]
        agent = r"DOMAIN\alice\1\g<0>"

        claimed = self.run_cli("claim", "--agent", agent, "--task-id", task_id)

        self.assertEqual(claimed.returncode, 0, claimed.stderr)
        self.assertEqual(json.loads(claimed.stdout)["agent"], agent)
        listed = self.run_cli("list", "--status", "doing")
        self.assertEqual(listed.returncode, 0, listed.stderr)
        self.assertEqual(json.loads(listed.stdout)["tasks"][0]["owner"], agent)
        document = (self.pool / "2026-09-01.md").read_text(encoding="utf-8")
        self.assertIn(f"- 领取人：{agent}", document)
        self.assertNotIn("\a", document)

    def test_only_owner_can_finish_and_waiting_can_reopen(self) -> None:
        task_id = self.add_tasks(1)[0]
        claimed = self.run_cli("claim", "--agent", "agent-a", "--task-id", task_id)
        self.assertEqual(claimed.returncode, 0, claimed.stderr)

        rejected = self.run_cli(
            "finish",
            "--task-id",
            task_id,
            "--agent",
            "agent-b",
            "--status",
            "done",
            "--note",
            "不应成功",
        )
        self.assertEqual(rejected.returncode, 2)
        self.assertIn("owned by agent-a", rejected.stderr)

        waiting = self.run_cli(
            "finish",
            "--task-id",
            task_id,
            "--agent",
            "agent-a",
            "--status",
            "waiting",
            "--note",
            "需要确认颜色",
        )
        self.assertEqual(waiting.returncode, 0, waiting.stderr)
        reopened = self.run_cli(
            "reopen",
            "--task-id",
            task_id,
            "--agent",
            "agent-c",
            "--note",
            "用户确认使用蓝色",
        )
        self.assertEqual(reopened.returncode, 0, reopened.stderr)
        reclaimed = self.run_cli("claim", "--agent", "agent-b", "--task-id", task_id)
        self.assertEqual(reclaimed.returncode, 0, reclaimed.stderr)
        completed = self.run_cli(
            "finish",
            "--task-id",
            task_id,
            "--agent",
            "agent-b",
            "--status",
            "done",
            "--note",
            "已实现并通过测试",
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)

        document = (self.pool / "2026-09-01.md").read_text(encoding="utf-8")
        self.assertIn("- 状态：done", document)
        self.assertIn("agent-a 等待用户：需要确认颜色", document)
        self.assertIn("agent-c 根据用户答复重新开放：用户确认使用蓝色", document)
        self.assertIn("agent-b 完成任务：已实现并通过测试", document)


if __name__ == "__main__":
    unittest.main()
