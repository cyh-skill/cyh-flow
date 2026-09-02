from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "review_snapshot.py"


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


class ReviewSnapshotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        run(["git", "init", "-q"], self.repo)
        run(["git", "config", "user.name", "cyh-flow test"], self.repo)
        run(["git", "config", "user.email", "cyh-flow@example.invalid"], self.repo)
        (self.repo / "tracked.txt").write_text("base\n", encoding="utf-8")
        run(["git", "add", "tracked.txt"], self.repo)
        run(["git", "commit", "-qm", "base"], self.repo)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def invoke(self, *arguments: str) -> dict[str, object]:
        completed = run([sys.executable, str(SCRIPT), *arguments], self.repo)
        return json.loads(completed.stdout)

    def invoke_without_check(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *arguments],
            cwd=self.repo,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def test_local_snapshot_survives_live_worktree_drift(self) -> None:
        (self.repo / "tracked.txt").write_text("base\nstaged\n", encoding="utf-8")
        run(["git", "add", "tracked.txt"], self.repo)
        with (self.repo / "tracked.txt").open("a", encoding="utf-8") as handle:
            handle.write("unstaged\n")
        (self.repo / "untracked.bin").write_bytes(b"\x00review\xff")
        (self.repo / "link").symlink_to("tracked.txt")

        packet = self.root / "packet"
        frozen = self.invoke(
            "freeze",
            "--repo",
            str(self.repo),
            "--kind",
            "local",
            "--output",
            str(packet),
        )
        self.assertEqual(frozen["changed_files"], ["link", "tracked.txt", "untracked.bin"])
        self.assertEqual(
            (packet / "snapshot" / "tracked.txt").read_text(encoding="utf-8"),
            "base\nstaged\nunstaged\n",
        )
        self.assertEqual((packet / "snapshot" / "untracked.bin").read_bytes(), b"\x00review\xff")
        self.assertTrue((packet / "snapshot" / "link").is_symlink())
        self.assertEqual(self.invoke("verify", "--packet-dir", str(packet))["status"], "ok")
        self.assertFalse(
            self.invoke("compare-live", "--packet-dir", str(packet))["drifted"]
        )

        with (self.repo / "tracked.txt").open("a", encoding="utf-8") as handle:
            handle.write("later edit\n")

        self.assertTrue(
            self.invoke("compare-live", "--packet-dir", str(packet))["drifted"]
        )
        self.assertEqual(self.invoke("verify", "--packet-dir", str(packet))["status"], "ok")

    def test_verify_rejects_tampered_artifact(self) -> None:
        (self.repo / "tracked.txt").write_text("changed\n", encoding="utf-8")
        packet = self.root / "tampered-packet"
        self.invoke(
            "freeze",
            "--repo",
            str(self.repo),
            "--kind",
            "local",
            "--output",
            str(packet),
        )
        with (packet / "unstaged.diff").open("ab") as handle:
            handle.write(b"tampered")
        failed_verify = self.invoke_without_check("verify", "--packet-dir", str(packet))
        self.assertEqual(failed_verify.returncode, 2)
        self.assertIn("artifact mismatch", failed_verify.stderr)

    def test_verify_rejects_tampered_committed_snapshot(self) -> None:
        base = run(["git", "rev-parse", "HEAD"], self.repo).stdout.strip()
        (self.repo / "tracked.txt").write_text("base\nnext\n", encoding="utf-8")
        run(["git", "add", "tracked.txt"], self.repo)
        run(["git", "commit", "-qm", "next"], self.repo)
        head = run(["git", "rev-parse", "HEAD"], self.repo).stdout.strip()
        packet = self.root / "committed-tamper-packet"
        self.invoke(
            "freeze",
            "--repo",
            str(self.repo),
            "--kind",
            "range",
            "--base",
            base,
            "--head",
            head,
            "--output",
            str(packet),
        )

        (packet / "snapshot" / "tracked.txt").write_text("tampered\n", encoding="utf-8")
        failed_verify = self.invoke_without_check("verify", "--packet-dir", str(packet))

        self.assertEqual(failed_verify.returncode, 2)
        self.assertIn("snapshot worktree differs", failed_verify.stderr)

    def test_verify_rejects_unexpected_untracked_snapshot_file(self) -> None:
        packet = self.root / "unexpected-untracked-packet"
        self.invoke(
            "freeze",
            "--repo",
            str(self.repo),
            "--kind",
            "local",
            "--output",
            str(packet),
        )
        (packet / "snapshot" / "unexpected.txt").write_text("unexpected\n", encoding="utf-8")

        failed_verify = self.invoke_without_check("verify", "--packet-dir", str(packet))

        self.assertEqual(failed_verify.returncode, 2)
        self.assertIn("untracked files do not match manifest", failed_verify.stderr)

    def test_explicit_packet_uses_private_permissions(self) -> None:
        packet = self.root / "private-packet"
        self.invoke(
            "freeze",
            "--repo",
            str(self.repo),
            "--kind",
            "local",
            "--output",
            str(packet),
        )

        self.assertEqual(stat.S_IMODE(packet.stat().st_mode), 0o700)
        for name in (
            "cached.diff",
            "snapshot-meta.json",
            "target-id.txt",
            "target-manifest.jcs.json",
            "unstaged.diff",
        ):
            self.assertEqual(stat.S_IMODE((packet / name).stat().st_mode), 0o600)

    def test_rejects_output_inside_source_repository(self) -> None:
        result = self.invoke_without_check(
            "freeze",
            "--repo",
            str(self.repo),
            "--kind",
            "local",
            "--output",
            str(self.repo / "packet"),
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("outside the source repository", result.stderr)

    def test_failed_automatic_freeze_removes_temporary_packet(self) -> None:
        temporary_root = self.root / "automatic-packets"
        temporary_root.mkdir()
        environment = os.environ.copy()
        environment["TMPDIR"] = str(temporary_root)

        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "freeze",
                "--repo",
                str(self.repo),
                "--kind",
                "range",
                "--base",
                "HEAD",
                "--head",
                "missing-review-head",
            ],
            cwd=self.repo,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=environment,
        )

        self.assertEqual(result.returncode, 2)
        self.assertEqual(list(temporary_root.iterdir()), [])

    def test_committed_range_snapshot_is_reproducible(self) -> None:
        base = run(["git", "rev-parse", "HEAD"], self.repo).stdout.strip()
        (self.repo / "tracked.txt").write_text("base\nnext\n", encoding="utf-8")
        run(["git", "add", "tracked.txt"], self.repo)
        run(["git", "commit", "-qm", "next"], self.repo)
        head = run(["git", "rev-parse", "HEAD"], self.repo).stdout.strip()

        packet = self.root / "range-packet"
        frozen = self.invoke(
            "freeze",
            "--repo",
            str(self.repo),
            "--kind",
            "range",
            "--base",
            base,
            "--head",
            head,
            "--output",
            str(packet),
        )
        self.assertEqual(frozen["changed_files"], ["tracked.txt"])
        self.assertEqual(self.invoke("verify", "--packet-dir", str(packet))["status"], "ok")
        self.assertFalse(
            self.invoke("compare-live", "--packet-dir", str(packet))["drifted"]
        )

    def test_rejects_incorrect_explicit_merge_base(self) -> None:
        base = run(["git", "rev-parse", "HEAD"], self.repo).stdout.strip()
        (self.repo / "tracked.txt").write_text("base\nnext\n", encoding="utf-8")
        run(["git", "add", "tracked.txt"], self.repo)
        run(["git", "commit", "-qm", "next"], self.repo)
        head = run(["git", "rev-parse", "HEAD"], self.repo).stdout.strip()

        result = self.invoke_without_check(
            "freeze",
            "--repo",
            str(self.repo),
            "--kind",
            "range",
            "--base",
            base,
            "--head",
            head,
            "--merge-base",
            head,
            "--output",
            str(self.root / "wrong-merge-base-packet"),
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("provided merge base does not match", result.stderr)

    def test_branch_compare_detects_local_ref_movement(self) -> None:
        base = run(["git", "rev-parse", "HEAD"], self.repo).stdout.strip()
        run(["git", "branch", "review-target", "HEAD"], self.repo)
        packet = self.root / "branch-packet"
        self.invoke(
            "freeze",
            "--repo",
            str(self.repo),
            "--kind",
            "branch",
            "--base",
            base,
            "--head",
            "review-target",
            "--output",
            str(packet),
        )
        self.assertFalse(
            self.invoke("compare-live", "--packet-dir", str(packet))["drifted"]
        )

        (self.repo / "tracked.txt").write_text("base\nbranch moved\n", encoding="utf-8")
        run(["git", "add", "tracked.txt"], self.repo)
        run(["git", "commit", "-qm", "move branch"], self.repo)
        run(["git", "branch", "-f", "review-target", "HEAD"], self.repo)

        self.assertTrue(
            self.invoke("compare-live", "--packet-dir", str(packet))["drifted"]
        )
        self.assertEqual(self.invoke("verify", "--packet-dir", str(packet))["status"], "ok")


if __name__ == "__main__":
    unittest.main()
