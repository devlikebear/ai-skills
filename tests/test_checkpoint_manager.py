import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


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

    def test_add_checkpoint_updates_state_and_writes_markdown(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            analysis_dir = Path(tmp_dir) / ".analysis"
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

            state = self.module.load_state(analysis_dir, "refactor-guide-20260308-120000")
            self.assertEqual(state["next_checkpoint"], 2)
            self.assertEqual(state["status"], "paused")
            self.assertIn("src/service/user.ts", state["visited"])
            self.assertIn("src/repo/user_repo.ts", state["frontier"])

    def test_init_session_resumes_existing_in_progress_session(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            analysis_dir = Path(tmp_dir) / ".analysis"
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


if __name__ == "__main__":
    unittest.main()
