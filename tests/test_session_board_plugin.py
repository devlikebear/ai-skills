import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = REPO_ROOT / "claude-code" / "session-board"
MARKETPLACE = REPO_ROOT / ".claude-plugin" / "marketplace.json"
CLAUDE = shutil.which("claude")


class SessionBoardPluginTests(unittest.TestCase):
    def test_manifest_names_the_plugin_and_its_state_contract(self):
        manifest = json.loads((PLUGIN_ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "session-board")
        self.assertIn("description", manifest)
        self.assertEqual(manifest["types"], "./types/index.d.ts")
        self.assertTrue((PLUGIN_ROOT / "types" / "index.d.ts").exists())

    def test_marketplace_lists_the_plugin_at_its_folder(self):
        marketplace = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
        entries = {item["name"]: item for item in marketplace["plugins"]}
        self.assertIn("session-board", entries)
        source = REPO_ROOT / entries["session-board"]["source"]
        self.assertEqual(source.resolve(), PLUGIN_ROOT.resolve())

    def test_hooks_json_names_an_existing_module(self):
        hooks = json.loads((PLUGIN_ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8"))
        self.assertEqual(len(hooks["modules"]), 1)
        module = PLUGIN_ROOT / "hooks" / hooks["modules"][0]
        self.assertTrue(module.exists(), msg=f"missing hooks module {module}")
        source = module.read_text(encoding="utf-8")
        self.assertIn("export const register", source)
        self.assertIn("name: 'board'", source)

    def test_state_keys_used_by_the_module_are_declared(self):
        contract = (PLUGIN_ROOT / "types" / "index.d.ts").read_text(encoding="utf-8")
        source = (PLUGIN_ROOT / "hooks" / "register.tsx").read_text(encoding="utf-8")
        keys = set(re.findall(r"\{ plugin: 'session-board', key: '(\w+)' \}", source))
        self.assertEqual(keys, {"board", "ui"})
        for key in keys:
            self.assertRegex(contract, rf"\b{key}: Shaped<")

    def test_engine_laid_types_are_ignored(self):
        ignore = (PLUGIN_ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn(".claude-plugin/types/", ignore)

    @unittest.skipUnless(CLAUDE, "claude CLI not on PATH")
    def test_claude_plugin_validate_passes(self):
        result = subprocess.run(
            [CLAUDE, "plugin", "validate", str(PLUGIN_ROOT)],
            capture_output=True,
            text=True,
            timeout=120,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("Validation passed", result.stdout + result.stderr)

    @unittest.skipUnless(CLAUDE, "claude CLI not on PATH")
    def test_claude_plugin_test_passes(self):
        result = subprocess.run(
            [CLAUDE, "plugin", "test", str(PLUGIN_ROOT)],
            capture_output=True,
            text=True,
            timeout=300,
        )
        output = result.stdout + result.stderr
        self.assertEqual(result.returncode, 0, msg=output)
        self.assertRegex(output, r"\b0 fail\b")


if __name__ == "__main__":
    unittest.main()
