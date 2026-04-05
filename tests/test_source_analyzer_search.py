import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT_MODULE_PATH = (
    REPO_ROOT
    / "codex"
    / "skills"
    / "source-analyzer"
    / "shared"
    / "scripts"
    / "checkpoint_manager.py"
)
SEARCH_MODULE_PATH = (
    REPO_ROOT
    / "codex"
    / "skills"
    / "source-analyzer"
    / "shared"
    / "scripts"
    / "source_analyzer_search.py"
)
SERVER_MODULE_PATH = REPO_ROOT / "servers" / "source-analyzer-mcp" / "server.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load module spec for {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SourceAnalyzerSearchTests(unittest.TestCase):
    def setUp(self):
        self.checkpoint = load_module(CHECKPOINT_MODULE_PATH, "checkpoint_manager")
        self.search = load_module(SEARCH_MODULE_PATH, "source_analyzer_search")
        self.server_module = load_module(SERVER_MODULE_PATH, "source_analyzer_mcp_server")

    def _create_analysis_fixture(self, root: Path) -> tuple[Path, str]:
        analysis_dir = root / ".analysis"
        session_id = "analyze-20260405-120000"
        with patch.object(self.checkpoint, "get_head_commit", return_value="abc123"):
            self.checkpoint.init_session(
                analysis_dir=analysis_dir,
                mode="analyze",
                scope="src",
                session_id=session_id,
                resume_if_exists=False,
            )

        outputs_dir = analysis_dir / "outputs"
        outputs_dir.mkdir(parents=True, exist_ok=True)
        (outputs_dir / "overview.md").write_text(
            "# Overview\n\n## Runtime\n\nThe runtime coordinates authentication and request handling.\n",
            encoding="utf-8",
        )
        (outputs_dir / "architecture.md").write_text(
            "# Architecture\n\n## Auth Flow\n\nClient -> API -> Service -> Repository\n",
            encoding="utf-8",
        )
        modules_dir = outputs_dir / "modules"
        modules_dir.mkdir(parents=True, exist_ok=True)
        (modules_dir / "auth.md").write_text(
            "# Auth Module\n\nHandles authentication token validation and session lookups.\n",
            encoding="utf-8",
        )
        (outputs_dir / "issue-candidates.md").write_text(
            "### SEC-001: Missing auth validation\n\n"
            "- Module: `src/auth.py`\n"
            "- Type: `SEC`\n"
            "- Evidence: Request tokens are accepted without validation.\n"
            "- Suggested action: Enforce token verification before handler execution.\n",
            encoding="utf-8",
        )
        (outputs_dir / "module-map.json").write_text(
            json.dumps(
                {
                    "auth": {
                        "path": "src/auth.py",
                        "responsibility": "Validate tokens and load sessions.",
                        "key_files": ["src/auth.py", "src/session_store.py"],
                    }
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        (outputs_dir / "dependency-graph.json").write_text(
            json.dumps({"src/auth.py": ["src/session_store.py"]}, indent=2) + "\n",
            encoding="utf-8",
        )

        summary = self.checkpoint.generate_summary(analysis_dir, session_id)
        self.assertEqual(summary["session_id"], session_id)

        checkpoints_dir = analysis_dir / "sessions" / session_id / "checkpoints"
        checkpoints_dir.mkdir(parents=True, exist_ok=True)
        (checkpoints_dir / "checkpoint-001.md").write_text(
            "# Checkpoint 001: Auth analyzed\n\n"
            "## Summary\n\nDocumented auth flow and security risks.\n",
            encoding="utf-8",
        )

        state = self.checkpoint.load_state(analysis_dir, session_id)
        state["checkpoints"] = [
            {
                "id": 1,
                "file": "checkpoints/checkpoint-001.md",
                "title": "Auth analyzed",
                "status": "paused",
                "created_at": "2026-04-05T12:00:00+00:00",
            }
        ]
        self.checkpoint.save_state(analysis_dir, session_id, state)
        return analysis_dir, session_id

    def test_generate_search_index_writes_expected_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            analysis_dir, session_id = self._create_analysis_fixture(Path(tmp_dir))

            result = self.search.generate_search_index(analysis_dir, session_id=session_id)

            self.assertEqual(result["session_id"], session_id)
            self.assertGreaterEqual(result["chunk_count"], 5)
            cache_dir = analysis_dir / "cache" / "source-analyzer-search"
            self.assertTrue((cache_dir / "search-documents.jsonl").exists())
            self.assertTrue((cache_dir / "chunk-manifest.json").exists())
            self.assertTrue((cache_dir / "file-to-chunks.json").exists())
            self.assertTrue((cache_dir / "output-to-chunks.json").exists())
            self.assertTrue((cache_dir / "index-metadata.json").exists())

    def test_search_analysis_uses_generated_index(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            analysis_dir, session_id = self._create_analysis_fixture(Path(tmp_dir))
            self.search.generate_search_index(analysis_dir, session_id=session_id)

            hits = self.search.search_analysis(
                analysis_dir,
                query="authentication token validation",
                top_k=3,
                session_id=session_id,
            )

            self.assertGreaterEqual(len(hits), 1)
            self.assertEqual(hits[0]["kind"], "module-doc")
            self.assertIn("auth", hits[0]["title"].lower())

    def test_search_analysis_falls_back_without_index(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            analysis_dir, session_id = self._create_analysis_fixture(Path(tmp_dir))

            hits = self.search.search_analysis(
                analysis_dir,
                query="missing auth validation",
                top_k=3,
                session_id=session_id,
            )

            self.assertGreaterEqual(len(hits), 1)
            self.assertEqual(hits[0]["kind"], "issue-candidate")

    def test_trace_dependencies_returns_related_nodes(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            analysis_dir, session_id = self._create_analysis_fixture(Path(tmp_dir))

            trace = self.search.trace_dependencies(
                analysis_dir,
                path="src/auth.py",
                depth=2,
                session_id=session_id,
            )

            self.assertEqual(trace["path"], "src/auth.py")
            self.assertIn("src/session_store.py", trace["dependencies"])

    def test_mcp_server_handles_search_tool_call(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir)
            analysis_dir, session_id = self._create_analysis_fixture(project_root)
            self.search.generate_search_index(analysis_dir, session_id=session_id)

            server = self.server_module.SourceAnalyzerMcpServer(
                project_root=project_root,
                analysis_dir=analysis_dir,
            )
            response = server.handle_request(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "analysis.search",
                        "arguments": {"query": "session lookups", "top_k": 2},
                    },
                }
            )

            self.assertEqual(response["id"], 1)
            content = response["result"]["content"][0]["text"]
            self.assertIn("auth", content.lower())

    def test_mcp_server_lists_resources(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir)
            analysis_dir, _session_id = self._create_analysis_fixture(project_root)
            server = self.server_module.SourceAnalyzerMcpServer(
                project_root=project_root,
                analysis_dir=analysis_dir,
            )

            response = server.handle_request(
                {"jsonrpc": "2.0", "id": 2, "method": "resources/list", "params": {}}
            )

            uris = {item["uri"] for item in response["result"]["resources"]}
            self.assertIn("analysis://overview", uris)
            self.assertIn("analysis://module-map", uris)


if __name__ == "__main__":
    unittest.main()
