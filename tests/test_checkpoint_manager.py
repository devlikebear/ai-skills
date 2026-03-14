import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "codex"
    / "skills"
    / "source-analyzer"
    / "shared"
    / "scripts"
    / "checkpoint_manager.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("checkpoint_manager", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load checkpoint_manager module spec")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CheckpointManagerTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module()

    def test_init_session_creates_expected_structure(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            analysis_dir = Path(tmp_dir) / ".analysis"
            with patch.object(self.module, "get_head_commit", return_value="abc123def456"):
                result = self.module.init_session(
                    analysis_dir=analysis_dir,
                    mode="analyze",
                    scope="src/main.py",
                    session_id="analyze-20260308-120000",
                    resume_if_exists=False,
                )

            session_dir = result["session_dir"]
            self.assertTrue((session_dir / "index.md").exists())
            self.assertTrue((session_dir / "state.json").exists())
            self.assertTrue((session_dir / "checkpoints").is_dir())
            self.assertTrue((session_dir / "outputs").is_dir())
            self.assertTrue((analysis_dir / "RESUME.md").exists())

            state = json.loads((session_dir / "state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["next_checkpoint"], 1)
            self.assertEqual(state["status"], "in_progress")
            self.assertEqual(state["version"], 2)
            self.assertEqual(state["commit_hash"], "abc123def456")

    def test_add_checkpoint_updates_state_and_writes_markdown(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            analysis_dir = Path(tmp_dir) / ".analysis"
            with patch.object(self.module, "get_head_commit", return_value="abc123"):
                self.module.init_session(
                    analysis_dir=analysis_dir,
                    mode="refactor-guide",
                    scope="src/service/user.ts",
                    session_id="refactor-guide-20260308-120000",
                    resume_if_exists=False,
                )

            result = self.module.add_checkpoint(
                analysis_dir=analysis_dir,
                session_id="refactor-guide-20260308-120000",
                title="핵심 흐름 1차 분석 / First-pass flow analysis",
                summary="엔트리 파일과 서비스 계층 호출 관계를 정리함 / Documented entrypoint-to-service flow.",
                visited_add=["src/service/user.ts"],
                queue_add=["src/repo/user_repo.ts"],
                queue_done=[],
                outputs=["outputs/refactor-user.md"],
                status="paused",
                next_actions=["repo 계층 책임 분리 후보 확인 / Inspect repository layer split candidates"],
            )

            checkpoint_path = result["checkpoint_path"]
            self.assertTrue(checkpoint_path.exists())
            content = checkpoint_path.read_text(encoding="utf-8")
            self.assertIn("# Checkpoint 001", content)
            self.assertIn("핵심 흐름 1차 분석 / First-pass flow analysis", content)
            self.assertIn("Commit: `abc123`", content)

            state = self.module.load_state(analysis_dir, "refactor-guide-20260308-120000")
            self.assertEqual(state["next_checkpoint"], 2)
            self.assertEqual(state["status"], "paused")
            self.assertIn("src/service/user.ts", state["visited"])
            self.assertIn("src/repo/user_repo.ts", state["frontier"])

    def test_init_session_resumes_existing_in_progress_session(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            analysis_dir = Path(tmp_dir) / ".analysis"
            with patch.object(self.module, "get_head_commit", return_value="abc123"):
                first = self.module.init_session(
                    analysis_dir=analysis_dir,
                    mode="analyze",
                    scope="src/main.go",
                    session_id="analyze-20260308-120000",
                    resume_if_exists=False,
                )

                resumed = self.module.init_session(
                    analysis_dir=analysis_dir,
                    mode="analyze",
                    scope="src/main.go",
                    session_id=None,
                    resume_if_exists=True,
                )

            self.assertEqual(first["session_id"], resumed["session_id"])
            self.assertTrue(resumed["resumed"])


class GitHelperTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module()

    def test_get_head_commit(self):
        mock_result = MagicMock()
        mock_result.stdout = "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2\n"
        with patch.object(self.module.subprocess, "run", return_value=mock_result) as mock_run:
            sha = self.module.get_head_commit()
            self.assertEqual(sha, "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2")
            mock_run.assert_called_once_with(
                ["git", "rev-parse", "HEAD"],
                capture_output=True, text=True, check=True,
            )

    def test_get_changed_files(self):
        mock_result = MagicMock()
        mock_result.stdout = "src/a.py\nsrc/b.py\n"
        with patch.object(self.module.subprocess, "run", return_value=mock_result):
            files = self.module.get_changed_files("aaa", "bbb")
            self.assertEqual(files, ["src/a.py", "src/b.py"])

    def test_commit_hash_valid_true(self):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "commit\n"
        with patch.object(self.module.subprocess, "run", return_value=mock_result):
            self.assertTrue(self.module.commit_hash_valid("abc123"))

    def test_commit_hash_valid_false(self):
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        with patch.object(self.module.subprocess, "run", return_value=mock_result):
            self.assertFalse(self.module.commit_hash_valid("nonexistent"))


class MigrateStateTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module()

    def test_migrate_state_v1_to_v2(self):
        state = {"version": 1, "session_id": "test", "visited": [], "frontier": []}
        result = self.module.migrate_state(state)
        self.assertEqual(result["version"], 2)
        self.assertIsNone(result["commit_hash"])

    def test_migrate_state_v2_noop(self):
        state = {"version": 2, "commit_hash": "abc123", "visited": [], "frontier": []}
        result = self.module.migrate_state(state)
        self.assertEqual(result["version"], 2)
        self.assertEqual(result["commit_hash"], "abc123")


class SyncSessionTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module()

    def _create_session(self, analysis_dir, session_id="test-session", commit="aaa111", scope="src"):
        with patch.object(self.module, "get_head_commit", return_value=commit):
            return self.module.init_session(
                analysis_dir=analysis_dir,
                mode="analyze",
                scope=scope,
                session_id=session_id,
                resume_if_exists=False,
            )

    def test_sync_session_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            analysis_dir = Path(tmp_dir) / ".analysis"
            self._create_session(analysis_dir, commit="aaa111")

            with patch.object(self.module, "get_head_commit", return_value="aaa111"):
                result = self.module.sync_session(analysis_dir, "test-session")

            self.assertEqual(result["status"], "unchanged")
            self.assertEqual(result["commit_hash"], "aaa111")
            self.assertEqual(result["changed_files"], [])

    def test_sync_session_new_commits(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            analysis_dir = Path(tmp_dir) / ".analysis"
            self._create_session(analysis_dir, commit="aaa111", scope="src")

            # Mark src/old.py as visited
            state = self.module.load_state(analysis_dir, "test-session")
            state["visited"] = ["src/old.py", "src/other.py"]
            state["frontier"] = ["src/todo.py"]
            self.module.save_state(analysis_dir, "test-session", state)

            with patch.object(self.module, "get_head_commit", return_value="bbb222"), \
                 patch.object(self.module, "commit_hash_valid", return_value=True), \
                 patch.object(self.module, "get_changed_files", return_value=["src/old.py", "src/new.py", "lib/unrelated.py"]):
                result = self.module.sync_session(analysis_dir, "test-session")

            self.assertEqual(result["status"], "synced")
            self.assertEqual(result["commit_hash"], "bbb222")
            # Only src/ files should be included (scope filter)
            self.assertEqual(result["changed_files"], ["src/old.py", "src/new.py"])

            # src/old.py should be removed from visited (needs re-analysis)
            state = self.module.load_state(analysis_dir, "test-session")
            self.assertNotIn("src/old.py", state["visited"])
            self.assertIn("src/other.py", state["visited"])
            # Changed files added to frontier
            self.assertIn("src/old.py", state["frontier"])
            self.assertIn("src/new.py", state["frontier"])
            # Original frontier items preserved
            self.assertIn("src/todo.py", state["frontier"])

    def test_sync_session_invalid_old_commit(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            analysis_dir = Path(tmp_dir) / ".analysis"
            self._create_session(analysis_dir, commit="aaa111", scope="src")

            with patch.object(self.module, "get_head_commit", return_value="ccc333"), \
                 patch.object(self.module, "commit_hash_valid", return_value=False), \
                 patch.object(self.module, "get_committed_files", return_value=["src/a.py", "src/b.py"]):
                result = self.module.sync_session(analysis_dir, "test-session")

            self.assertEqual(result["status"], "synced")
            self.assertEqual(result["changed_files"], ["src/a.py", "src/b.py"])

            state = self.module.load_state(analysis_dir, "test-session")
            self.assertIn("src/a.py", state["frontier"])
            self.assertIn("src/b.py", state["frontier"])


class InitSessionWithCommitTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module()

    def test_init_session_with_commit(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            analysis_dir = Path(tmp_dir) / ".analysis"
            result = self.module.init_session(
                analysis_dir=analysis_dir,
                mode="analyze",
                scope="src",
                session_id="test-commit",
                resume_if_exists=False,
                commit_hash="explicit_commit_hash",
            )

            self.assertEqual(result["commit_hash"], "explicit_commit_hash")
            state = self.module.load_state(analysis_dir, "test-commit")
            self.assertEqual(state["commit_hash"], "explicit_commit_hash")
            self.assertEqual(state["version"], 2)


class CLISyncTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module()

    def test_cli_sync(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            analysis_dir = Path(tmp_dir) / ".analysis"
            with patch.object(self.module, "get_head_commit", return_value="aaa111"):
                self.module.init_session(
                    analysis_dir=analysis_dir,
                    mode="analyze",
                    scope="src",
                    session_id="cli-test",
                    resume_if_exists=False,
                )

            with patch.object(self.module, "get_head_commit", return_value="aaa111"):
                exit_code = self.module.cli([
                    "sync",
                    "--analysis-dir", str(analysis_dir),
                    "--session-id", "cli-test",
                ])
            self.assertEqual(exit_code, 0)


class ExcludePatternTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module()

    def test_should_exclude_default_patterns(self):
        self.assertTrue(self.module.should_exclude(".analysis/sessions/foo"))
        self.assertTrue(self.module.should_exclude(".codex/skills/bar"))
        self.assertTrue(self.module.should_exclude(".claude/CLAUDE.md"))
        self.assertTrue(self.module.should_exclude("vendor/github.com/foo"))
        self.assertTrue(self.module.should_exclude("node_modules/lodash/index.js"))
        self.assertFalse(self.module.should_exclude("src/main.go"))
        self.assertFalse(self.module.should_exclude("internal/config/types.go"))

    def test_should_exclude_custom_patterns(self):
        patterns = ["test_data/", ".env"]
        self.assertTrue(self.module.should_exclude("test_data/fixtures/a.json", patterns))
        self.assertFalse(self.module.should_exclude("src/main.go", patterns))

    def test_init_session_stores_exclude_patterns(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            analysis_dir = Path(tmp_dir) / ".analysis"
            with patch.object(self.module, "get_head_commit", return_value="abc123"):
                self.module.init_session(
                    analysis_dir=analysis_dir,
                    mode="analyze",
                    scope="src",
                    session_id="exclude-test",
                    resume_if_exists=False,
                    exclude_patterns=["docs/"],
                )
            state = self.module.load_state(analysis_dir, "exclude-test")
            self.assertIn("docs/", state["exclude_patterns"])
            self.assertIn(".analysis/", state["exclude_patterns"])


class EmptyCheckpointTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module()

    def test_empty_checkpoint_rejected(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            analysis_dir = Path(tmp_dir) / ".analysis"
            with patch.object(self.module, "get_head_commit", return_value="abc123"):
                self.module.init_session(
                    analysis_dir=analysis_dir,
                    mode="analyze",
                    scope="src",
                    session_id="empty-cp-test",
                    resume_if_exists=False,
                )

            with self.assertRaises(ValueError) as ctx:
                self.module.add_checkpoint(
                    analysis_dir=analysis_dir,
                    session_id="empty-cp-test",
                    title="empty checkpoint",
                    summary="",
                    visited_add=[],
                    outputs=[],
                    next_actions=[],
                )
            self.assertIn("empty checkpoint", str(ctx.exception))

    def test_checkpoint_with_summary_accepted(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            analysis_dir = Path(tmp_dir) / ".analysis"
            with patch.object(self.module, "get_head_commit", return_value="abc123"):
                self.module.init_session(
                    analysis_dir=analysis_dir,
                    mode="analyze",
                    scope="src",
                    session_id="summary-cp-test",
                    resume_if_exists=False,
                )

            result = self.module.add_checkpoint(
                analysis_dir=analysis_dir,
                session_id="summary-cp-test",
                title="has summary",
                summary="analyzed the service layer",
            )
            self.assertEqual(result["checkpoint_no"], 1)


class GenerateSummaryTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module()

    def test_generate_summary_produces_json(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            analysis_dir = Path(tmp_dir) / ".analysis"
            with patch.object(self.module, "get_head_commit", return_value="abc123"):
                self.module.init_session(
                    analysis_dir=analysis_dir,
                    mode="analyze",
                    scope="src",
                    session_id="summary-test",
                    resume_if_exists=False,
                )

            # Create a module doc
            modules_dir = analysis_dir / "sessions" / "summary-test" / "outputs" / "modules"
            modules_dir.mkdir(parents=True, exist_ok=True)
            (modules_dir / "auth.md").write_text(
                "# Auth Module\n\nHandles authentication and token validation.\n",
                encoding="utf-8",
            )

            summary = self.module.generate_summary(analysis_dir, "summary-test")
            self.assertEqual(summary["session_id"], "summary-test")
            self.assertEqual(summary["mode"], "analyze")
            self.assertEqual(len(summary["modules"]), 1)
            self.assertEqual(summary["modules"][0]["name"], "auth")
            self.assertIn("authentication", summary["modules"][0]["summary"])

            # Verify file was written
            summary_path = analysis_dir / "sessions" / "summary-test" / "outputs" / "SUMMARY.json"
            self.assertTrue(summary_path.exists())


if __name__ == "__main__":
    unittest.main()
