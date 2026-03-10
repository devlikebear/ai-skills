import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLISH_WIKI = REPO_ROOT / "scripts" / "publish_wiki.sh"


class PublishWikiScriptTests(unittest.TestCase):
    def _run(self, cmd, cwd=None, env=None):
        return subprocess.run(
            cmd,
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            check=True,
        )

    def _write(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def _module_doc(self, title: str, role: str) -> str:
        return f"# 모듈: {title}\n\n## 역할\n\n{role}\n"

    def test_publish_wiki_loads_module_links_from_outputs(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir)
            repo_root = tmp_root / "repo"
            repo_root.mkdir()

            scripts_dir = repo_root / "scripts"
            scripts_dir.mkdir()
            shutil.copy2(PUBLISH_WIKI, scripts_dir / "publish_wiki.sh")

            session_id = "analyze-20260310-133920"
            outputs_dir = repo_root / ".analysis" / "sessions" / session_id / "outputs"
            self._write(outputs_dir / "overview.md", "# 프로젝트 개요\n")
            self._write(outputs_dir / "architecture.md", "# 아키텍처\n")
            self._write(
                outputs_dir / "modules" / "source-analyzer.md",
                self._module_doc("source-analyzer", "기존 코드베이스를 분석한다."),
            )
            self._write(
                outputs_dir / "modules" / "github-flow.md",
                self._module_doc("github-flow", "브랜치부터 릴리스까지 관리한다."),
            )
            self._write(
                outputs_dir / "modules" / "tests.md",
                self._module_doc("tests", "33개 계약 테스트를 검증한다."),
            )

            origin_repo = tmp_root / "origin.git"
            wiki_repo = tmp_root / "origin.wiki.git"
            self._run(["git", "init", "--bare", str(origin_repo)])
            self._run(["git", "init", "--bare", str(wiki_repo)])
            self._run(["git", "init"], cwd=repo_root)
            self._run(["git", "remote", "add", "origin", str(origin_repo)], cwd=repo_root)

            env = {
                **os.environ,
                "GIT_AUTHOR_NAME": "Codex Test",
                "GIT_AUTHOR_EMAIL": "codex@example.com",
                "GIT_COMMITTER_NAME": "Codex Test",
                "GIT_COMMITTER_EMAIL": "codex@example.com",
            }
            result = subprocess.run(
                ["bash", str(scripts_dir / "publish_wiki.sh"), "--session-id", session_id],
                cwd=repo_root,
                env=env,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, msg=result.stdout + "\n" + result.stderr)

            sidebar = self._run(
                ["git", "--git-dir", str(wiki_repo), "show", "HEAD:_Sidebar.md"],
            ).stdout
            home = self._run(
                ["git", "--git-dir", str(wiki_repo), "show", "HEAD:Home.md"],
            ).stdout
            pages = self._run(
                ["git", "--git-dir", str(wiki_repo), "ls-tree", "--name-only", "-r", "HEAD"],
            ).stdout

            self.assertIn("module-github-flow.md", pages)
            self.assertIn("[[github-flow|module-github-flow]]", sidebar)
            self.assertIn("[[github-flow\\|module-github-flow]]", home)
            self.assertIn("브랜치부터 릴리스까지 관리한다.", home)


if __name__ == "__main__":
    unittest.main()
