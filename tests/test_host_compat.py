from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise AssertionError(f"missing frontmatter: {path}")
    try:
        end = lines.index("---", 1)
    except ValueError as error:
        raise AssertionError(f"unterminated frontmatter: {path}") from error
    result: dict[str, str] = {}
    for line in lines[1:end]:
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip().strip('"')
    return result


class HostCompatibilityTests(unittest.TestCase):
    def test_claude_plugin_manifest_points_to_canonical_skill(self) -> None:
        manifest_path = ROOT / ".claude-plugin" / "plugin.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        self.assertEqual(manifest["name"], "cyh-flow")
        self.assertEqual(manifest["license"], "MIT")
        self.assertEqual(
            manifest["$schema"],
            "https://json.schemastore.org/claude-code-plugin-manifest.json",
        )
        self.assertEqual(manifest["skills"], ["./"])
        skill_path = ROOT / manifest["skills"][0]
        self.assertTrue(skill_path.is_dir())
        self.assertTrue((skill_path / "SKILL.md").is_file())

    def test_marketplace_entry_matches_plugin(self) -> None:
        marketplace = json.loads(
            (ROOT / ".claude-plugin" / "marketplace.json").read_text(
                encoding="utf-8"
            )
        )
        plugins = marketplace["plugins"]

        self.assertEqual(marketplace["name"], "cyh-flow")
        self.assertEqual(len(plugins), 1)
        self.assertEqual(plugins[0]["name"], "cyh-flow")
        self.assertEqual(plugins[0]["source"], "./")
        self.assertEqual(plugins[0]["license"], "MIT")

    def test_mit_license_matches_manifests_and_readme(self) -> None:
        license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertTrue(license_text.startswith("MIT License\n\n"))
        self.assertIn("Copyright (c) 2026 cyh-skill", license_text)
        self.assertIn("Permission is hereby granted, free of charge", license_text)
        self.assertIn('THE SOFTWARE IS PROVIDED "AS IS"', license_text)
        self.assertIn("[MIT License](LICENSE)", readme)
        self.assertNotIn("尚未附带开源许可证", readme)

    def test_canonical_skill_is_shared_by_both_hosts(self) -> None:
        canonical = ROOT / "SKILL.md"
        metadata = frontmatter(canonical)
        text = canonical.read_text(encoding="utf-8")

        self.assertEqual(metadata["name"], "cyh-flow")
        self.assertIn("Use only when the user explicitly invokes", metadata["description"])
        self.assertIn("$ARGUMENTS", text)
        self.assertTrue(canonical.is_file())

    def test_codex_and_claude_explicit_entrypoints_remain_documented(self) -> None:
        root_skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        openai = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")

        self.assertIn("$cyh-flow", root_skill)
        self.assertIn("/cyh-flow:cyh-flow", root_skill)
        self.assertIn("$cyh-flow", readme)
        self.assertIn("/cyh-flow:cyh-flow", readme)
        self.assertIn("/cyh-flow", readme)
        self.assertIn("allow_implicit_invocation: false", openai)

    def test_host_specific_fallback_contracts_are_present(self) -> None:
        root_skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        plan = (ROOT / "references" / "plan.md").read_text(encoding="utf-8")
        review = (ROOT / "references" / "review.md").read_text(encoding="utf-8")
        review_auto = (ROOT / "references" / "review-auto.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("not the Codex create/get/update Goal API", root_skill)
        self.assertIn("experimental agent teams", root_skill)
        self.assertIn("editing-capable permission mode", plan)
        self.assertIn("without enabled persistent mailbox delivery", review)
        self.assertIn("<cyh-flow> review auto", root_skill)
        self.assertIn("review-auto.md", review)
        self.assertIn("latest completed review cycle is clean", review_auto)
        self.assertIn("Never merge a PR", review_auto)
        for path in (ROOT / "references").rglob("*.md"):
            self.assertNotIn("$cyh-flow", path.read_text(encoding="utf-8"), path)

    def test_all_relative_markdown_links_resolve(self) -> None:
        link_pattern = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
        for markdown in ROOT.rglob("*.md"):
            text = markdown.read_text(encoding="utf-8")
            for target in link_pattern.findall(text):
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                target_path = target.split("#", 1)[0]
                with self.subTest(markdown=markdown, target=target_path):
                    self.assertTrue((markdown.parent / target_path).resolve().exists())


if __name__ == "__main__":
    unittest.main()
