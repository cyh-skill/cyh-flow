from __future__ import annotations

import io
import json
import stat
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from scripts import review_watch


def cursor(*, head: str = "aaa", comments: dict | None = None) -> dict:
    return {
        "schema_version": review_watch.SCHEMA_VERSION,
        "target": "acme/widgets#42",
        "captured_at": "2026-09-02T00:00:00+00:00",
        "head_oid": head,
        "pr": {"digest": "pr", "state": "open"},
        "issue_comments": comments or {},
        "reviews": {},
        "review_comments": {},
        "review_threads": {},
    }


class ReviewWatchTests(unittest.TestCase):
    def test_parse_target_accepts_url_reference_and_number(self) -> None:
        unused = lambda arguments: self.fail(f"unexpected runner call: {arguments}")

        self.assertEqual(
            review_watch.parse_target(
                "https://github.com/acme/widgets/pull/42", None, unused
            ),
            review_watch.Target("acme", "widgets", 42),
        )
        self.assertEqual(
            review_watch.parse_target("acme/widgets#42", None, unused),
            review_watch.Target("acme", "widgets", 42),
        )
        self.assertEqual(
            review_watch.parse_target("#42", "acme/widgets", unused),
            review_watch.Target("acme", "widgets", 42),
        )

    def test_human_records_ignore_bots_and_own_auto_marker(self) -> None:
        records = [
            {
                "id": 1,
                "body": "please recheck",
                "user": {"login": "alice", "type": "User"},
            },
            {
                "id": 2,
                "body": "automation noise",
                "user": {"login": "ci[bot]", "type": "Bot"},
            },
            {
                "id": 3,
                "body": "done\n<!-- cyh-flow-review-auto:acme/widgets#42:x:y -->",
                "user": {"login": "reviewer", "type": "User"},
            },
        ]

        result = review_watch.human_records(records, "reviewer", "issue_comment")

        self.assertEqual(set(result), {"1"})
        self.assertEqual(result["1"]["author"], "alice")

    def test_diff_detects_head_and_comment_changes(self) -> None:
        before = cursor(
            comments={
                "1": {
                    "author": "alice",
                    "kind": "issue_comment",
                    "url": "https://example.test/1",
                    "digest": "old",
                },
                "2": {
                    "author": "bob",
                    "kind": "issue_comment",
                    "url": "https://example.test/2",
                    "digest": "gone",
                },
            }
        )
        after = cursor(
            head="bbb",
            comments={
                "1": {
                    "author": "alice",
                    "kind": "issue_comment",
                    "url": "https://example.test/1",
                    "digest": "new",
                },
                "3": {
                    "author": "carol",
                    "kind": "issue_comment",
                    "url": "https://example.test/3",
                    "digest": "added",
                },
            },
        )

        changes = review_watch.diff_cursors(before, after)

        self.assertIn(
            {"source": "head", "change": "updated", "before": "aaa", "after": "bbb"},
            changes,
        )
        self.assertEqual(
            {(item["change"], item.get("id")) for item in changes if item["source"] == "issue_comments"},
            {("updated", "1"), ("deleted", "2"), ("added", "3")},
        )

    def test_cursor_file_round_trip_is_private(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cursor.json"
            target = review_watch.Target("acme", "widgets", 42)

            review_watch.write_cursor(path, cursor())

            self.assertEqual(review_watch.load_cursor(path, target), cursor())
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)

    def test_main_emits_only_ready_then_changed(self) -> None:
        initial = cursor()
        changed = cursor(head="bbb")
        output = io.StringIO()

        def runner(arguments: list[str]) -> dict:
            if arguments == ["api", "user"]:
                return {"login": "reviewer"}
            self.fail(f"unexpected runner call: {arguments}")

        with (
            mock.patch.object(
                review_watch, "fetch_cursor", side_effect=[initial, changed]
            ),
            mock.patch.object(review_watch.time, "sleep"),
            redirect_stdout(output),
        ):
            result = review_watch.main(
                ["acme/widgets#42", "--interval", "0.01"], runner=runner
            )

        events = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual(result, 0)
        self.assertEqual([event["status"] for event in events], ["ready", "changed"])
        self.assertEqual(events[-1]["changes"][0]["source"], "head")


if __name__ == "__main__":
    unittest.main()
