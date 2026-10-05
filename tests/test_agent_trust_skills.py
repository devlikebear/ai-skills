import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("verify-own-work", "correction-ladder", "garden-antipatterns")
CREDIT_URL = "https://x.com/poteto/status/2102050467505430555"


def linked_documents(entry):
    """Follow relative Markdown links from a SKILL.md, including nested ones."""
    pending, visited = [entry], set()
    while pending:
        path = pending.pop().resolve()
        if path in visited:
            continue
        visited.add(path)
        content = path.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+\.md)(?:#[^)]*)?\)", content):
            if "://" not in target:
                pending.append(path.parent / target)
    return visited


class AgentTrustSkillTests(unittest.TestCase):
    def test_skills_have_trigger_sections_exit_criteria_and_credit(self):
        for name in SKILLS:
            with self.subTest(skill=name):
                content = (ROOT / "codex/skills" / name / "SKILL.md").read_text(encoding="utf-8")
                frontmatter = content.split("---", 2)[1]
                self.assertRegex(frontmatter, rf"(?m)^name: {name}$")
                self.assertRegex(frontmatter, r'(?m)^description: ".*Use when .*"$')
                self.assertIn("## Done when", content)
                self.assertIn(CREDIT_URL, content)
                line_count = len(content.splitlines())
                self.assertGreaterEqual(line_count, 60)
                self.assertLessEqual(line_count, 150)

    def test_every_distribution_ships_a_complete_reference_graph(self):
        for name in SKILLS:
            source = ROOT / "codex/skills" / name
            claude = ROOT / "claude-code/plugin/skills" / name
            bundle = ROOT / "plugins/code-workflow/skills" / name
            shipped_roots = {
                source: source,
                claude: ROOT / "claude-code/plugin",
                bundle: bundle,
            }
            for root, shipped in shipped_roots.items():
                with self.subTest(skill=name, root=root):
                    documents = linked_documents(root / "SKILL.md")
                    self.assertGreaterEqual(len(documents), 2)
                    for path in documents:
                        self.assertTrue(path.exists(), path)
                        self.assertTrue(path.is_relative_to(shipped.resolve()), path)

    def test_claude_copy_matches_canonical_after_path_translation(self):
        for name in SKILLS:
            with self.subTest(skill=name):
                source = ROOT / "codex/skills" / name
                canonical = (source / "SKILL.md").read_text(encoding="utf-8")
                translated = canonical.replace("shared/", f"../../references/{name}/")
                claude_skill = ROOT / "claude-code/plugin/skills" / name / "SKILL.md"
                self.assertEqual(translated, claude_skill.read_text(encoding="utf-8"))

                references = ROOT / "claude-code/plugin/references" / name
                source_files = {
                    p.relative_to(source / "shared")
                    for p in (source / "shared").rglob("*")
                    if p.is_file()
                }
                target_files = {p.relative_to(references) for p in references.rglob("*") if p.is_file()}
                self.assertEqual(source_files, target_files)
                for relative in source_files:
                    self.assertEqual(
                        (source / "shared" / relative).read_bytes(),
                        (references / relative).read_bytes(),
                    )

    def test_skills_allow_implicit_invocation(self):
        for name in SKILLS:
            with self.subTest(skill=name):
                agent = (ROOT / "codex/skills" / name / "agents/openai.yaml").read_text(encoding="utf-8")
                claude = (ROOT / "claude-code/plugin/skills" / name / "SKILL.md").read_text(encoding="utf-8")
                self.assertIn(f"${name}", agent)
                self.assertNotIn("allow_implicit_invocation: false", agent)
                self.assertNotRegex(claude, r"(?m)^disable-model-invocation:\s*true$")


if __name__ == "__main__":
    unittest.main()
