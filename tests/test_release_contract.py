import json
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

    def test_all_distribution_versions_match_version_file(self):
        version = (REPO_ROOT / "VERSION.txt").read_text(encoding="utf-8").strip()
        manifests = [
            REPO_ROOT / ".claude-plugin" / "marketplace.json",
            REPO_ROOT / "claude-code" / "plugin" / ".claude-plugin" / "plugin.json",
            REPO_ROOT / "plugins" / "source-analyzer-tools" / ".codex-plugin" / "plugin.json",
            REPO_ROOT / "plugins" / "code-workflow" / ".codex-plugin" / "plugin.json",
        ]

        for path in manifests:
            payload = json.loads(path.read_text(encoding="utf-8"))
            versions = []
            if "version" in payload:
                versions.append(payload["version"])
            versions.extend(
                item["version"]
                for item in payload.get("plugins", [])
                if "version" in item
            )
            self.assertTrue(versions, msg=f"no version field found in {path}")
            self.assertEqual(set(versions), {version}, msg=f"version drift in {path}")

        server_source = (
            REPO_ROOT / "servers" / "source-analyzer-mcp" / "server.py"
        ).read_text(encoding="utf-8")
        self.assertIn(f'SERVER_VERSION = "{version}"', server_source)

    def test_mcp_configs_avoid_shell_and_platform_specific_paths(self):
        configs = [
            REPO_ROOT / "claude-code" / "plugin" / ".mcp.json",
            REPO_ROOT / "plugins" / "source-analyzer-tools" / ".mcp.json",
            REPO_ROOT / "plugins" / "code-workflow" / ".mcp.json",
        ]

        for path in configs:
            config = json.loads(path.read_text(encoding="utf-8"))
            server = config["mcpServers"]["source-analyzer-search"]
            serialized = json.dumps(server)
            self.assertEqual(server["command"], "python3", msg=f"portable launcher required in {path}")
            self.assertNotIn("bash", serialized)
            self.assertNotIn("/opt/homebrew", serialized)
            self.assertNotIn("/usr/local", serialized)
            self.assertRegex(serialized, r"\$\{(?:CLAUDE_)?PLUGIN_ROOT\}")

    def test_readme_documents_plugin_lifecycle_and_platform_matrix(self):
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        for heading in [
            "## Install for Codex",
            "### Update Codex plugin",
            "### Roll back Codex plugin",
            "## Install via Plugin Marketplace (Claude Code)",
            "### Update or roll back Claude Code plugin",
            "## Platform support",
        ]:
            self.assertIn(heading, readme)

        self.assertIn("macOS", readme)
        self.assertIn("Linux", readme)
        self.assertIn("Windows", readme)
        self.assertIn("legacy", readme.lower())

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
