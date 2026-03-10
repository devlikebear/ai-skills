import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
INSTALLER = REPO_ROOT / "scripts" / "install_codex_skill.sh"


class ReleaseContractTests(unittest.TestCase):
    def test_release_metadata_exists(self):
        version = (REPO_ROOT / "VERSION.txt").read_text(encoding="utf-8").strip()
        changelog = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        license_text = (REPO_ROOT / "LICENSE").read_text(encoding="utf-8")

        self.assertRegex(version, r"^\d+\.\d+\.\d+$")
        self.assertIn("# Changelog", changelog)
        self.assertIn(version, changelog)
        self.assertIn("source-analyzer", changelog)
        self.assertIn("MIT License", license_text)

    def test_gitignore_excludes_local_install_artifacts(self):
        content = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn(".install_test_home", content)
        self.assertIn("security_best_practices_report.md", content)
        self.assertIn(".drafts/", content)

    def test_installer_rejects_path_traversal_skill_names(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = subprocess.run(
                [str(INSTALLER), "../.."],
                cwd=REPO_ROOT,
                env={**os.environ, "CODEX_HOME": tmp_dir},
                capture_output=True,
                text=True,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid skill name", result.stderr)

    def test_installer_installs_skill_with_flat_structure(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = subprocess.run(
                [str(INSTALLER), "implement"],
                cwd=REPO_ROOT,
                env={**os.environ, "CODEX_HOME": tmp_dir},
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)

            install_root = Path(tmp_dir) / "skills" / "implement"
            self.assertTrue((install_root / "SKILL.md").exists())
            self.assertTrue((install_root / "agents" / "openai.yaml").exists())
            self.assertTrue((install_root / "shared").is_dir())
            self.assertFalse((install_root / "ko").exists())
            self.assertFalse((install_root / "en").exists())

            content = (install_root / "agents" / "openai.yaml").read_text(encoding="utf-8")
            self.assertIn('display_name: "Implement"', content)


if __name__ == "__main__":
    unittest.main()
