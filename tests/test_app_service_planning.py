import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME = "app-service-planning"
SOURCE = ROOT / "codex/skills" / NAME
CLAUDE = ROOT / "claude-code/plugin/skills" / NAME
BUNDLE = ROOT / "plugins/code-workflow/skills" / NAME


def linked_documents(entry):
    """Follow shipped relative Markdown links, including nested references."""
    pending, visited = [entry], set()
    while pending:
        path = pending.pop().resolve()
        if path in visited:
            continue
        visited.add(path)
        content = path.read_text(encoding="utf-8")
        for target in re.findall(r'\[[^\]]+\]\(([^)]+\.md)(?:#[^)]*)?\)', content):
            if "://" not in target:
                pending.append(path.parent / target)
    return visited


class AppServicePlanningTests(unittest.TestCase):
    def test_all_distributions_have_complete_reference_graph(self):
        # Links must stay inside what each distribution actually ships.
        shipped_roots = {
            SOURCE: SOURCE,
            CLAUDE: ROOT / "claude-code/plugin",
            BUNDLE: BUNDLE,
        }
        for root, shipped in shipped_roots.items():
            with self.subTest(root=root):
                documents = linked_documents(root / "SKILL.md")
                self.assertGreaterEqual(len(documents), 5)
                for path in documents:
                    self.assertTrue(path.is_relative_to(shipped.resolve()), path)

    def test_standalone_install_is_self_contained_and_preserves_other_skills(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            sentinel = home / "skills/custom/SKILL.md"
            sentinel.parent.mkdir(parents=True)
            sentinel.write_text("user skill\n")
            result = subprocess.run(
                [str(ROOT / "scripts/install_codex_skill.sh"), NAME],
                env={**os.environ, "CODEX_HOME": tmp}, cwd=ROOT,
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            installed = home / "skills" / NAME
            for path in linked_documents(installed / "SKILL.md"):
                self.assertTrue(path.is_relative_to(installed.resolve()))
            self.assertTrue((installed / "agents/openai.yaml").is_file())
            self.assertEqual(sentinel.read_text(), "user skill\n")

    def test_codex_bundle_contains_identical_skill_and_resources(self):
        source_files = {p.relative_to(SOURCE) for p in SOURCE.rglob("*") if p.is_file()}
        bundle_files = {p.relative_to(BUNDLE) for p in BUNDLE.rglob("*") if p.is_file()}
        self.assertEqual(source_files, bundle_files)
        for relative in source_files:
            self.assertEqual((SOURCE / relative).read_bytes(), (BUNDLE / relative).read_bytes())

    def test_claude_content_matches_canonical_after_path_translation(self):
        canonical = (SOURCE / "SKILL.md").read_text()
        translated = canonical.replace("shared/", "../../references/app-service-planning/")
        self.assertEqual(translated, (CLAUDE / "SKILL.md").read_text())
        claude_resources = ROOT / "claude-code/plugin/references/app-service-planning"
        source_files = {p.relative_to(SOURCE / "shared") for p in (SOURCE / "shared").rglob("*") if p.is_file()}
        target_files = {p.relative_to(claude_resources) for p in claude_resources.rglob("*") if p.is_file()}
        self.assertEqual(source_files, target_files)
        for relative in source_files:
            self.assertEqual((SOURCE / "shared" / relative).read_bytes(), (claude_resources / relative).read_bytes())


if __name__ == "__main__":
    unittest.main()
