from __future__ import annotations

import json
import stat
import tempfile
import unittest
from pathlib import Path

from skills.flow.scripts import review_artifacts


TARGET = "acme/widgets#42"
ROLES = sorted(review_artifacts.ROLES)


def specialist(role: str, *, candidate: bool = False) -> dict:
    candidates = []
    if candidate:
        candidates.append(
            {
                "id": f"{role}:one",
                "title": "delete redundant wrapper",
                "category": "complexity" if role == "ponytail-complexity" else "correctness",
                "claim_type": "complexity" if role == "ponytail-complexity" else "local-behavior",
                "path": "src/change.py",
                "line_start": 10,
                "line_end": 12,
                "introduced": "the target adds the wrapper",
                "trigger": "every caller enters the wrapper",
                "impact": "duplicate control flow adds maintenance cost",
                "authority": None,
                "evidence_refs": ["src/change.py:10"],
                "counterevidence": ["checked callers for distinct behavior; none found"],
            }
        )
    return {
        "schema_version": 1,
        "reviewer": role,
        "target": TARGET,
        "status": "completed",
        "terminal_reason": None,
        "coverage": {"inspected": ["full diff"], "limits": []},
        "candidates": candidates,
        "open_questions": [],
    }


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


class ReviewArtifactTests(unittest.TestCase):
    def build_specialist_manifest(
        self,
        root: Path,
        *,
        candidate_role: str | None = "ponytail-complexity",
        limit_role: str | None = None,
    ) -> Path:
        paths = []
        for role in ROLES:
            path = root / f"{role}.json"
            value = specialist(role, candidate=role == candidate_role)
            if role == limit_role:
                value["coverage"]["limits"] = ["generated client was unavailable"]
            write_json(path, value)
            paths.append(path)
        manifest = root / "specialists.json"
        review_artifacts.build_manifest(paths, manifest)
        return manifest

    def test_advisory_is_visible_but_does_not_block_clean(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest = self.build_specialist_manifest(root)
            master = root / "master.json"
            write_json(
                master,
                {
                    "schema_version": 1,
                    "target": TARGET,
                    "status": "completed",
                    "terminal_reason": None,
                    "verified_findings": [],
                    "dispositions": [
                        {
                            "source_ids": ["ponytail-complexity:one"],
                            "disposition": "advisory",
                            "reason": "equivalent simplification with material line reduction",
                        }
                    ],
                    "impact_unexplained": [],
                    "coverage_limits": [],
                    "clean_eligible": True,
                },
            )

            result = review_artifacts.validate_file(
                master,
                "master",
                specialist_manifest=manifest,
            )
            self.assertEqual(result["status"], "valid")
            self.assertEqual(stat.S_IMODE(manifest.stat().st_mode), 0o600)

    def test_manifest_requires_all_four_roles(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            paths = []
            for role in ROLES[:-1]:
                path = root / f"{role}.json"
                write_json(path, specialist(role))
                paths.append(path)
            with self.assertRaises(review_artifacts.ArtifactError):
                review_artifacts.build_manifest(paths, root / "manifest.json")

    def test_removed_specialist_fields_are_rejected(self) -> None:
        value = specialist("codex-correctness", candidate=True)
        value["candidates"][0]["native_severity"] = "P1"
        with self.assertRaisesRegex(review_artifacts.ArtifactError, "unexpected fields"):
            review_artifacts.validate_specialist(value)

    def test_malformed_finding_reports_artifact_error(self) -> None:
        with self.assertRaisesRegex(review_artifacts.ArtifactError, "priority"):
            review_artifacts.validate_finding(
                {
                    "id": "finding-one",
                    "source_ids": ["codex-correctness:one"],
                    "title": "defect",
                    "category": "correctness",
                    "path": "src/change.py",
                    "line_start": 10,
                    "line_end": 10,
                    "root_cause": "cause",
                    "trigger": "trigger",
                    "impact": "impact",
                    "evidence_refs": ["src/change.py:10"],
                    "counterevidence": ["checked alternate path"],
                    "fix_boundary": "owner",
                    "reported_by": ["codex-correctness"],
                }
            )

    def test_master_must_dispose_every_source_id_and_recompute_clean(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest = self.build_specialist_manifest(root)
            master = root / "master.json"
            base = {
                "schema_version": 1,
                "target": TARGET,
                "status": "completed",
                "terminal_reason": None,
                "verified_findings": [],
                "dispositions": [],
                "impact_unexplained": [],
                "coverage_limits": [],
                "clean_eligible": True,
            }
            write_json(master, base)
            with self.assertRaisesRegex(review_artifacts.ArtifactError, "source ids mismatch"):
                review_artifacts.validate_file(
                    master,
                    "master",
                    specialist_manifest=manifest,
                )

            base["dispositions"] = [
                {
                    "source_ids": ["ponytail-complexity:one"],
                    "disposition": "unresolved",
                    "reason": "authority unavailable",
                }
            ]
            write_json(master, base)
            with self.assertRaisesRegex(review_artifacts.ArtifactError, "clean_eligible"):
                review_artifacts.validate_file(
                    master,
                    "master",
                    specialist_manifest=manifest,
                )

    def test_master_must_preserve_specialist_coverage_limits(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest = self.build_specialist_manifest(
                root,
                candidate_role=None,
                limit_role="codex-correctness",
            )
            master = root / "master.json"
            value = {
                "schema_version": 1,
                "target": TARGET,
                "status": "completed",
                "terminal_reason": None,
                "verified_findings": [],
                "dispositions": [],
                "impact_unexplained": [],
                "coverage_limits": [],
                "clean_eligible": True,
            }
            write_json(master, value)
            with self.assertRaisesRegex(review_artifacts.ArtifactError, "omitted"):
                review_artifacts.validate_file(
                    master,
                    "master",
                    specialist_manifest=manifest,
                )

            value["coverage_limits"] = [
                {
                    "source": "codex-correctness",
                    "item": "generated client was unavailable",
                    "material": False,
                    "reason": "the changed path does not call that client",
                }
            ]
            write_json(master, value)
            review_artifacts.validate_file(
                master,
                "master",
                specialist_manifest=manifest,
            )


if __name__ == "__main__":
    unittest.main()
