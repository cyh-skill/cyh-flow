from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from skills.flow.scripts import review_publish


class FakeRunner:
    def __init__(self, *, delivery_code: int = 0) -> None:
        self.login = "reviewer"
        self.comments: list[dict] = []
        self.delivery_code = delivery_code
        self.delivery_paths: list[Path] = []

    def json(self, arguments: list[str]):
        if arguments == ["api", "user"]:
            return {"login": self.login}
        endpoint = arguments[-1]
        if endpoint.endswith("/comments?per_page=100"):
            return [list(self.comments)]
        if "/issues/comments/" in endpoint:
            identifier = int(endpoint.rsplit("/", 1)[1])
            return next(comment for comment in self.comments if comment["id"] == identifier)
        raise AssertionError(f"unexpected JSON arguments: {arguments}")

    def text(self, arguments: list[str], *, check: bool = True) -> tuple[int, str]:
        self.assert_comment_command(arguments)
        body_path = Path(arguments[-1])
        self.delivery_paths.append(body_path)
        identifier = len(self.comments) + 100
        url = f"https://github.com/acme/widgets/pull/42#issuecomment-{identifier}"
        self.comments.append(
            {
                "id": identifier,
                "body": body_path.read_text(encoding="utf-8"),
                "html_url": url,
                "user": {"login": self.login},
            }
        )
        return self.delivery_code, url if self.delivery_code == 0 else "network timeout"

    @staticmethod
    def assert_comment_command(arguments: list[str]) -> None:
        if arguments[:2] != ["pr", "comment"] or "--body-file" not in arguments:
            raise AssertionError(f"unexpected text arguments: {arguments}")


class ReviewPublishTests(unittest.TestCase):
    def test_publish_is_idempotent_and_verifies_exact_body(self) -> None:
        runner = FakeRunner()
        target = review_publish.Target("acme", "widgets", 42)
        with tempfile.TemporaryDirectory() as temporary:
            body = Path(temporary) / "comment.md"
            body.write_text("## Review\n\nNo findings.\n", encoding="utf-8")

            first = review_publish.publish(target, body, "ordinary", None, runner)
            second = review_publish.publish(target, body, "ordinary", None, runner)

        self.assertEqual(first["status"], "posted")
        self.assertEqual(second["status"], "existing")
        self.assertEqual(first["url"], second["url"])
        self.assertEqual(len(runner.comments), 1)
        self.assertIn("<!-- cyh-flow-review:acme/widgets#42:", runner.comments[0]["body"])
        self.assertTrue(all(not path.exists() for path in runner.delivery_paths))

    def test_uncertain_command_outcome_reuses_the_comment_it_created(self) -> None:
        runner = FakeRunner(delivery_code=1)
        target = review_publish.Target("acme", "widgets", 42)
        with tempfile.TemporaryDirectory() as temporary:
            body = Path(temporary) / "comment.md"
            body.write_text("Finding.\n", encoding="utf-8")
            result = review_publish.publish(target, body, "ordinary", None, runner)

        self.assertEqual(result["status"], "posted")
        self.assertEqual(len(runner.comments), 1)

    def test_auto_mode_requires_and_embeds_head_oid(self) -> None:
        target = review_publish.Target("acme", "widgets", 42)
        with self.assertRaises(review_publish.PublishError):
            review_publish.build_marker(target, "body\n", "auto", None)
        marker, _ = review_publish.build_marker(target, "body\n", "auto", "ABC1234")
        self.assertIn(":abc1234:", marker)
        with self.assertRaises(review_publish.PublishError):
            review_publish.build_marker(target, "body\n", "ordinary", "abc1234")

    def test_empty_body_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            body = Path(temporary) / "comment.md"
            body.write_text(" \n", encoding="utf-8")
            with self.assertRaises(review_publish.PublishError):
                review_publish.canonical_visible_body(body)


if __name__ == "__main__":
    unittest.main()
