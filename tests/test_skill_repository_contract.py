import unittest
from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ANALYZER_ROOT = REPO_ROOT / "codex" / "skills" / "source-analyzer"
SKILL_GENERATOR_ROOT = REPO_ROOT / ".codex" / "skills" / "skill-generator"
PUBLIC_SKILLS_ROOT = REPO_ROOT / "codex" / "skills"
EXPECTED_PUBLIC_SKILLS = {
    "source-analyzer",
    "implement",
    "plan-for-codex",
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
        self.assertTrue((SKILL_GENERATOR_ROOT / "ko" / "SKILL.md").exists())
        self.assertTrue((SKILL_GENERATOR_ROOT / "ko" / "agents" / "openai.yaml").exists())
        self.assertTrue((SKILL_GENERATOR_ROOT / "en" / "README.md").exists())
        self.assertTrue((SKILL_GENERATOR_ROOT / "en" / "SKILL.md").exists())
        self.assertTrue((SKILL_GENERATOR_ROOT / "en" / "agents" / "openai.yaml").exists())
        root_readme = (SKILL_GENERATOR_ROOT / "README.md").read_text(encoding="utf-8")
        ko_skill = (SKILL_GENERATOR_ROOT / "ko" / "SKILL.md").read_text(encoding="utf-8")
        en_skill = (SKILL_GENERATOR_ROOT / "en" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("./ko/README.md", root_readme)
        self.assertIn("./en/README.md", root_readme)
        self.assertIn("skill-creator", ko_skill)
        self.assertIn("skill-creator", en_skill)
        self.assertIn("wrapper", ko_skill.lower())
        self.assertIn("wrapper", en_skill.lower())

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


if __name__ == "__main__":
    unittest.main()
