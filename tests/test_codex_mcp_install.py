import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
INSTALLER = REPO_ROOT / "scripts" / "install_codex_skill.sh"


class CodexMcpInstallTests(unittest.TestCase):
    def test_source_analyzer_install_includes_mcp_assets(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = subprocess.run(
                [str(INSTALLER), "source-analyzer"],
                cwd=REPO_ROOT,
                env={**os.environ, "CODEX_HOME": tmp_dir},
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            install_root = Path(tmp_dir) / "skills" / "source-analyzer"
            self.assertTrue(
                (install_root / "shared" / "mcp" / "source-analyzer-mcp" / "server.py").exists()
            )
            self.assertTrue(
                (install_root / "shared" / "scripts" / "source_analyzer_search.py").exists()
            )

    def test_source_analyzer_install_with_mcp_registers_server(self):
        with tempfile.TemporaryDirectory() as tmp_dir, tempfile.TemporaryDirectory() as bin_dir:
            log_path = Path(tmp_dir) / "codex.log"
            fake_codex = Path(bin_dir) / "codex"
            fake_codex.write_text(
                "#!/usr/bin/env bash\n"
                "printf '%s\\n' \"$*\" >> \"$CODEX_MCP_LOG\"\n",
                encoding="utf-8",
            )
            fake_codex.chmod(0o755)

            env = {
                **os.environ,
                "CODEX_HOME": tmp_dir,
                "CODEX_MCP_LOG": str(log_path),
                "PATH": f"{bin_dir}:{os.environ['PATH']}",
            }
            result = subprocess.run(
                [str(INSTALLER), "source-analyzer", "--with-mcp"],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            log = log_path.read_text(encoding="utf-8")
            self.assertIn("mcp add source-analyzer-search -- python3", log)
            self.assertIn("shared/mcp/source-analyzer-mcp/server.py", log)


if __name__ == "__main__":
    unittest.main()
