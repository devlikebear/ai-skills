import unittest
from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ANALYZER_ROOT = REPO_ROOT / "codex" / "skills" / "source-analyzer"
SKILL_GENERATOR_ROOT = REPO_ROOT / ".codex" / "skills" / "skill-generator"
PUBLIC_SKILLS_ROOT = REPO_ROOT / "codex" / "skills"
CLAUDE_CODE_SKILLS_ROOT = REPO_ROOT / "claude-code" / "skills"
CLAUDE_CODE_PLUGIN_ROOT = REPO_ROOT / "claude-code" / "plugin"
MARKETPLACE_ROOT = REPO_ROOT / ".claude-plugin"
EXPECTED_PUBLIC_SKILLS = {
    "source-analyzer",
    "implement",
    "plan-for-codex",
    "refactor",
    "review",
}
EXPECTED_CLAUDE_CODE_SKILLS = {
    "source-analyzer",
    "implement",
    "plan",
    "refactor",
    "review",
}
EXPECTED_PLUGIN_SKILLS = {
    "source-analyzer",
    "implement",
    "plan",
    "refactor",
    "review",
}


class SkillRepositoryContractTests(unittest.TestCase):
    def test_all_skill_frontmatter_descriptions_are_quoted(self):
        for skill_path in REPO_ROOT.glob("**/SKILL.md"):
            content = skill_path.read_text(encoding="utf-8")
            frontmatter = content.split("---", 2)[1]
            self.assertRegex(
                frontmatter,
                re.compile(r'^description:\s+".+"$', re.MULTILINE),
                msg=f"description must be quoted in {skill_path}",
            )

    def test_public_skills_exist_and_use_language_directories(self):
        actual = {path.name for path in PUBLIC_SKILLS_ROOT.iterdir() if path.is_dir()}
        self.assertTrue(EXPECTED_PUBLIC_SKILLS.issubset(actual))

        for skill_name in EXPECTED_PUBLIC_SKILLS:
            root = PUBLIC_SKILLS_ROOT / skill_name
            self.assertTrue((root / "README.md").exists(), msg=f"missing README for {skill_name}")
            self.assertTrue((root / "ko" / "README.md").exists(), msg=f"missing ko README for {skill_name}")
            self.assertTrue((root / "ko" / "SKILL.md").exists(), msg=f"missing ko SKILL for {skill_name}")
            self.assertTrue((root / "ko" / "agents" / "openai.yaml").exists(), msg=f"missing ko openai.yaml for {skill_name}")
            self.assertTrue((root / "en" / "README.md").exists(), msg=f"missing en README for {skill_name}")
            self.assertTrue((root / "en" / "SKILL.md").exists(), msg=f"missing en SKILL for {skill_name}")
            self.assertTrue((root / "en" / "agents" / "openai.yaml").exists(), msg=f"missing en openai.yaml for {skill_name}")
            self.assertTrue((root / "shared").is_dir(), msg=f"missing shared dir for {skill_name}")

    def test_source_analyzer_uses_language_directories(self):
        self.assertTrue((SOURCE_ANALYZER_ROOT / "README.md").exists())
        self.assertTrue((SOURCE_ANALYZER_ROOT / "ko" / "README.md").exists())
        self.assertTrue((SOURCE_ANALYZER_ROOT / "ko" / "SKILL.md").exists())
        self.assertTrue((SOURCE_ANALYZER_ROOT / "ko" / "agents" / "openai.yaml").exists())
        self.assertTrue((SOURCE_ANALYZER_ROOT / "en" / "README.md").exists())
        self.assertTrue((SOURCE_ANALYZER_ROOT / "en" / "SKILL.md").exists())
        self.assertTrue((SOURCE_ANALYZER_ROOT / "en" / "agents" / "openai.yaml").exists())
        self.assertTrue((SOURCE_ANALYZER_ROOT / "shared" / "scripts" / "checkpoint_manager.py").exists())

    def test_source_analyzer_root_readme_is_english_and_links_to_language_readmes(self):
        content = (SOURCE_ANALYZER_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("# Source Analyzer", content)
        self.assertIn("./ko/README.md", content)
        self.assertIn("./en/README.md", content)
        self.assertNotIn("AI 스킬 리포지토리", content)

    def test_language_specific_source_analyzer_skills_have_expected_policies(self):
        ko_skill = (SOURCE_ANALYZER_ROOT / "ko" / "SKILL.md").read_text(encoding="utf-8")
        en_skill = (SOURCE_ANALYZER_ROOT / "en" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("Write responses and generated outputs in Korean by default.", ko_skill)
        self.assertIn("If the user explicitly requests another language policy, follow it.", ko_skill)
        self.assertIn("Write responses and generated outputs in English by default.", en_skill)
        self.assertIn("If the user explicitly requests another language policy, follow it.", en_skill)
        self.assertIn("shared/references", ko_skill)
        self.assertIn("shared/references", en_skill)

    def test_skill_generator_wrapper_exists_in_dot_codex(self):
        self.assertTrue((SKILL_GENERATOR_ROOT / "README.md").exists())
        self.assertTrue((SKILL_GENERATOR_ROOT / "ko" / "README.md").exists())
        self.assertTrue((SKILL_GENERATOR_ROOT / "en" / "README.md").exists())
        self.assertTrue((SKILL_GENERATOR_ROOT / "SKILL.md").exists())
        self.assertTrue((SKILL_GENERATOR_ROOT / "agents" / "openai.yaml").exists())
        root_readme = (SKILL_GENERATOR_ROOT / "README.md").read_text(encoding="utf-8")
        root_skill = (SKILL_GENERATOR_ROOT / "SKILL.md").read_text(encoding="utf-8")
        root_agent = (SKILL_GENERATOR_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn("./ko/README.md", root_readme)
        self.assertIn("./en/README.md", root_readme)
        self.assertIn("skill-creator", root_skill)
        self.assertIn("wrapper", root_skill.lower())
        self.assertIn('display_name: "Skill Generator"', root_agent)

    def test_public_repo_readme_mentions_language_layout_and_installer(self):
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("AI Skills Repository", readme)
        self.assertIn("language-specific variants", readme)
        self.assertIn("codex/skills/source-analyzer", readme)
        self.assertIn("codex/skills/implement", readme)
        self.assertIn("codex/skills/plan-for-codex", readme)
        self.assertIn("codex/skills/refactor", readme)
        self.assertIn("codex/skills/review", readme)
        self.assertIn(".codex/skills/skill-generator", readme)
        self.assertIn("scripts/install_codex_skill.sh", readme)

    def test_claude_code_skills_exist_and_use_language_directories(self):
        actual = {path.name for path in CLAUDE_CODE_SKILLS_ROOT.iterdir() if path.is_dir()}
        self.assertTrue(EXPECTED_CLAUDE_CODE_SKILLS.issubset(actual))

        for skill_name in EXPECTED_CLAUDE_CODE_SKILLS:
            root = CLAUDE_CODE_SKILLS_ROOT / skill_name
            self.assertTrue((root / "README.md").exists(), msg=f"missing README for {skill_name}")
            self.assertTrue((root / "ko" / "README.md").exists(), msg=f"missing ko README for {skill_name}")
            self.assertTrue((root / "ko" / "SKILL.md").exists(), msg=f"missing ko SKILL for {skill_name}")
            self.assertTrue((root / "en" / "README.md").exists(), msg=f"missing en README for {skill_name}")
            self.assertTrue((root / "en" / "SKILL.md").exists(), msg=f"missing en SKILL for {skill_name}")
            self.assertTrue((root / "shared").is_dir(), msg=f"missing shared dir for {skill_name}")

    def test_claude_code_skills_do_not_have_openai_yaml(self):
        for skill_name in EXPECTED_CLAUDE_CODE_SKILLS:
            root = CLAUDE_CODE_SKILLS_ROOT / skill_name
            self.assertFalse(
                (root / "ko" / "agents").exists(),
                msg=f"claude-code skill {skill_name}/ko should not have agents/ directory",
            )
            self.assertFalse(
                (root / "en" / "agents").exists(),
                msg=f"claude-code skill {skill_name}/en should not have agents/ directory",
            )

    def test_claude_code_source_analyzer_has_checkpoint_script(self):
        sa_root = CLAUDE_CODE_SKILLS_ROOT / "source-analyzer"
        self.assertTrue((sa_root / "shared" / "scripts" / "checkpoint_manager.py").exists())

    def test_claude_code_skills_use_claude_skill_dir_not_codex_home(self):
        for skill_path in CLAUDE_CODE_SKILLS_ROOT.glob("**/SKILL.md"):
            content = skill_path.read_text(encoding="utf-8")
            self.assertNotIn(
                "CODEX_HOME",
                content,
                msg=f"claude-code skill {skill_path} should not reference CODEX_HOME",
            )

    def test_public_repo_readme_mentions_claude_code(self):
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("claude-code/skills/source-analyzer", readme)
        self.assertIn("claude-code/skills/implement", readme)
        self.assertIn("claude-code/skills/plan", readme)
        self.assertIn("claude-code/skills/refactor", readme)
        self.assertIn("claude-code/skills/review", readme)
        self.assertIn("scripts/install_claude_code_skill.sh", readme)

    # --- Plugin marketplace tests ---

    def test_plugin_manifest_exists_and_is_valid_json(self):
        manifest_path = CLAUDE_CODE_PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
        self.assertTrue(manifest_path.exists(), msg="missing plugin.json")
        import json
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "code-workflow")
        self.assertIn("version", manifest)
        self.assertIn("description", manifest)

    def test_marketplace_json_exists_and_is_valid(self):
        marketplace_path = MARKETPLACE_ROOT / "marketplace.json"
        self.assertTrue(marketplace_path.exists(), msg="missing marketplace.json")
        import json
        marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
        self.assertEqual(marketplace["name"], "ai-skills")
        self.assertIn("owner", marketplace)
        self.assertIn("plugins", marketplace)
        self.assertGreater(len(marketplace["plugins"]), 0)
        plugin_entry = marketplace["plugins"][0]
        self.assertEqual(plugin_entry["name"], "code-workflow")
        self.assertIn("source", plugin_entry)

    def test_plugin_skills_exist(self):
        skills_root = CLAUDE_CODE_PLUGIN_ROOT / "skills"
        actual = {path.name for path in skills_root.iterdir() if path.is_dir()}
        self.assertTrue(EXPECTED_PLUGIN_SKILLS.issubset(actual))
        for skill_name in EXPECTED_PLUGIN_SKILLS:
            skill_md = skills_root / skill_name / "SKILL.md"
            self.assertTrue(skill_md.exists(), msg=f"missing SKILL.md for plugin skill {skill_name}")

    def test_plugin_skills_are_bilingual(self):
        skills_root = CLAUDE_CODE_PLUGIN_ROOT / "skills"
        for skill_name in EXPECTED_PLUGIN_SKILLS:
            content = (skills_root / skill_name / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn(
                "Detect the user's language",
                content,
                msg=f"plugin skill {skill_name} should have bilingual language policy",
            )

    def test_plugin_skills_do_not_reference_codex_home(self):
        for skill_path in CLAUDE_CODE_PLUGIN_ROOT.glob("**/SKILL.md"):
            content = skill_path.read_text(encoding="utf-8")
            self.assertNotIn(
                "CODEX_HOME",
                content,
                msg=f"plugin skill {skill_path} should not reference CODEX_HOME",
            )

    def test_plugin_references_directory_exists(self):
        refs_dir = CLAUDE_CODE_PLUGIN_ROOT / "references"
        self.assertTrue(refs_dir.is_dir(), msg="missing references directory in plugin")
        expected_refs = [
            "work-order.md",
            "refactor-work-order.md",
            "review-checklist.md",
            "refactoring-checklist.md",
            "refactoring-patterns.md",
            "checkpoint-template.md",
            "refactor-template.md",
            "tidy-first-rules.md",
            "security-triage-checklist.md",
            "tutorial-template.md",
        ]
        for ref in expected_refs:
            self.assertTrue((refs_dir / ref).exists(), msg=f"missing reference {ref} in plugin")

    def test_plugin_checkpoint_script_exists(self):
        self.assertTrue(
            (CLAUDE_CODE_PLUGIN_ROOT / "scripts" / "checkpoint_manager.py").exists(),
            msg="missing checkpoint_manager.py in plugin",
        )

    def test_plugin_source_analyzer_uses_claude_plugin_root(self):
        content = (CLAUDE_CODE_PLUGIN_ROOT / "skills" / "source-analyzer" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("CLAUDE_PLUGIN_ROOT", content)


if __name__ == "__main__":
    unittest.main()
