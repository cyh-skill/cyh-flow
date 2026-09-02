from __future__ import annotations

import json
import stat
import tempfile
import unittest
from pathlib import Path

from skills.flow.scripts import review_prepare


class FakeRunner:
    def __init__(self) -> None:
        self.commands: list[list[str]] = []

    def run_json(self, command: list[str]):
        self.commands.append(command)
        if command == ["gh", "api", "user"]:
            return {"login": "reviewer"}
        endpoint = command[-1]
        if endpoint == "repos/acme/widgets/pulls/42":
            return {
                "number": 42,
                "title": "Change",
                "base": {"ref": "main", "sha": "a" * 40},
                "head": {"ref": "feature", "sha": "b" * 40},
            }
        if endpoint.endswith("/check-runs?per_page=100"):
            return [{"check_runs": []}]
        if "--slurp" in command:
            if "/files?" in endpoint:
                return [[{"filename": "src/change.py", "status": "modified"}]]
            return [[]]
        raise AssertionError(f"unexpected JSON command: {command}")

    def run_text(self, command: list[str], *, input_bytes: bytes | None = None) -> str:
        self.commands.append(command)
        if command[-3:] == ["remote", "get-url", "origin"]:
            return "git@github.com:acme/widgets.git\n"
        if command[:3] == ["gh", "repo", "clone"]:
            Path(command[4]).mkdir(parents=True)
        elif command[:3] == ["git", "clone", "--shared"]:
            Path(command[-1]).mkdir(parents=True)
        elif "worktree" in command and "add" in command:
            Path(command[command.index("--detach") + 1]).mkdir(parents=True)
        elif command[-2:-1] == ["rev-parse"]:
            return ("a" if "base-" in command[-1] else "b") * 40 + "\n"
        return ""

    def run_bytes(self, command: list[str]) -> bytes:
        self.commands.append(command)
        return b""


class ReviewPrepareTests(unittest.TestCase):
    def test_parse_target_accepts_url_and_slug(self) -> None:
        expected = review_prepare.Target("acme", "widgets", 42)
        self.assertEqual(
            review_prepare.parse_target("https://github.com/acme/widgets/pull/42"),
            expected,
        )
        self.assertEqual(review_prepare.parse_target("acme/widgets#42"), expected)
        with self.assertRaises(ValueError):
            review_prepare.parse_target("#42")

    def test_prepare_caches_raw_transport_and_one_source_tree(self) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "review"
            result = review_prepare.prepare(
                [review_prepare.Target("acme", "widgets", 42)],
                root,
                runner,
            )

            self.assertEqual(result["status"], "ready")
            self.assertEqual(result["targets"], ["acme/widgets#42"])
            self.assertNotIn("authenticated_user", result)
            manifest_path = Path(result["manifest"])
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertTrue(manifest["transport_only"])
            self.assertFalse(manifest["stability_gate"])
            target = manifest["targets"][0]
            self.assertEqual(target["base_ref"], "main")
            self.assertEqual(target["head_oid"], "b" * 40)
            self.assertEqual(target["source_head_oid"], "b" * 40)
            self.assertTrue(Path(target["documents"]["files"]).is_file())
            self.assertTrue(Path(target["documents"]["statuses"]).is_file())
            self.assertTrue(Path(target["documents"]["diff"]).is_file())
            mode = stat.S_IMODE(Path(target["documents"]["pull"]).stat().st_mode)
            self.assertEqual(mode, 0o600)
            self.assertEqual(
                stat.S_IMODE(Path(target["documents"]["diff"]).stat().st_mode),
                0o600,
            )
            worktree = manifest["repositories"][0]["worktrees"][target["slug"]]
            self.assertTrue(Path(worktree).is_dir())

    def test_local_object_source_is_repointed_only_inside_disposable_clone(self) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = base / "source"
            source.mkdir()
            review_prepare.prepare(
                [review_prepare.Target("acme", "widgets", 42)],
                base / "review",
                runner,
                source,
            )

        self.assertIn(
            "git@github.com:acme/widgets.git",
            [part for command in runner.commands for part in command],
        )

    def test_duplicate_targets_are_rejected_before_github_access(self) -> None:
        target = review_prepare.Target("acme", "widgets", 42)
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(review_prepare.PrepareError):
                review_prepare.prepare([target, target], Path(temporary), FakeRunner())


if __name__ == "__main__":
    unittest.main()
