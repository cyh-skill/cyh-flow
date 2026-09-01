from __future__ import annotations

import base64
import json
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "task_pool.py"
ONE_PIXEL_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


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
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--pool", str(self.pool), *arguments],
            input=json.dumps(payload, ensure_ascii=False) if payload is not None else None,
            text=True,
            capture_output=True,
            check=False,
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
        self.assertIn(f"![原始界面](assets/{task_id}/001.png)", document)
        self.assertIn("- 截图来源：用户附件；收录时间：", document)
        self.assertIn("- 状态：pending", document)
        self.assertIn("- 领取人：—", document)

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
