from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any


CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

import source_analyzer_search as search  # noqa: E402


SERVER_NAME = "source-analyzer-search"
SERVER_VERSION = "0.10.3"


class SourceAnalyzerMcpServer:
    def __init__(self, project_root: Path | None = None, analysis_dir: Path | None = None):
        default_root = Path(os.environ.get("SOURCE_ANALYZER_PROJECT_ROOT", os.getcwd())).resolve()
        self.project_root = (project_root or default_root).resolve()
        default_analysis_dir = Path(os.environ.get("SOURCE_ANALYZER_ANALYSIS_DIR", self.project_root / ".analysis"))
        self.analysis_dir = (analysis_dir or default_analysis_dir).resolve()

    def initialize_result(self) -> dict[str, Any]:
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
                "resources": {},
            },
            "serverInfo": {
                "name": SERVER_NAME,
                "version": SERVER_VERSION,
            },
        }

    def tool_descriptors(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "analysis.get_overview",
                "description": "Read the published overview for the current analysis.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "analysis_dir": {"type": "string"},
                    },
                },
            },
            {
                "name": "analysis.get_module",
                "description": "Read a module document or module-map entry by module name or path.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name_or_path": {"type": "string"},
                        "analysis_dir": {"type": "string"},
                    },
                    "required": ["name_or_path"],
                },
            },
            {
                "name": "analysis.search",
                "description": "Search source-analyzer outputs and checkpoints.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "top_k": {"type": "integer", "minimum": 1, "default": 5},
                        "kinds": {"type": "array", "items": {"type": "string"}},
                        "session_id": {"type": "string"},
                        "analysis_dir": {"type": "string"},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "analysis.trace_dependencies",
                "description": "Trace dependency graph edges for a source file.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "depth": {"type": "integer", "minimum": 1, "default": 1},
                        "session_id": {"type": "string"},
                        "analysis_dir": {"type": "string"},
                    },
                    "required": ["path"],
                },
            },
            {
                "name": "analysis.get_issue_candidates",
                "description": "List published DUP/SEC/TIDY issue candidates.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string"},
                        "analysis_dir": {"type": "string"},
                    },
                },
            },
            {
                "name": "analysis.get_resume_state",
                "description": "Return the current resume pointer and active session state.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string"},
                        "analysis_dir": {"type": "string"},
                    },
                },
            },
            {
                "name": "analysis.get_changed_context",
                "description": "Return dirty files and indexing context for the current session.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "from_commit": {"type": "string"},
                        "to_commit": {"type": "string"},
                        "session_id": {"type": "string"},
                        "analysis_dir": {"type": "string"},
                    },
                },
            },
            {
                "name": "analysis.list_sessions",
                "description": "List available source-analyzer sessions.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "analysis_dir": {"type": "string"},
                    },
                },
            },
            {
                "name": "analysis.get_checkpoint",
                "description": "Read a checkpoint from a source-analyzer session.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string"},
                        "checkpoint_id": {"type": "integer", "minimum": 1},
                        "analysis_dir": {"type": "string"},
                    },
                },
            },
        ]

    def _resolve_analysis_dir(self, arguments: dict[str, Any]) -> Path:
        candidate = arguments.get("analysis_dir")
        if candidate:
            return Path(candidate).resolve()
        return self.analysis_dir

    def _call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        analysis_dir = self._resolve_analysis_dir(arguments)
        if name == "analysis.get_overview":
            return search.get_overview(analysis_dir)
        if name == "analysis.get_module":
            return search.get_module(analysis_dir, arguments["name_or_path"])
        if name == "analysis.search":
            return search.search_analysis(
                analysis_dir,
                query=arguments["query"],
                top_k=int(arguments.get("top_k", 5)),
                kinds=arguments.get("kinds"),
                session_id=arguments.get("session_id"),
            )
        if name == "analysis.trace_dependencies":
            return search.trace_dependencies(
                analysis_dir,
                path=arguments["path"],
                depth=int(arguments.get("depth", 1)),
                session_id=arguments.get("session_id"),
            )
        if name == "analysis.get_issue_candidates":
            return search.get_issue_candidates(analysis_dir, issue_type=arguments.get("type"))
        if name == "analysis.get_resume_state":
            return search.get_resume_state(analysis_dir, session_id=arguments.get("session_id"))
        if name == "analysis.get_changed_context":
            return search.get_changed_context(
                analysis_dir,
                from_commit=arguments.get("from_commit"),
                to_commit=arguments.get("to_commit"),
                session_id=arguments.get("session_id"),
            )
        if name == "analysis.list_sessions":
            return search.list_sessions(analysis_dir)
        if name == "analysis.get_checkpoint":
            return search.get_checkpoint(
                analysis_dir,
                session_id=arguments.get("session_id"),
                checkpoint_id=arguments.get("checkpoint_id"),
            )
        raise KeyError(f"unknown tool: {name}")

    def handle_request(self, request: dict[str, Any]) -> dict[str, Any] | None:
        method = request.get("method")
        request_id = request.get("id")
        params = request.get("params", {})
        try:
            if method == "initialize":
                return {"jsonrpc": "2.0", "id": request_id, "result": self.initialize_result()}
            if method == "notifications/initialized":
                return None
            if method == "ping":
                return {"jsonrpc": "2.0", "id": request_id, "result": {}}
            if method == "tools/list":
                return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": self.tool_descriptors()}}
            if method == "tools/call":
                result = self._call_tool(params["name"], params.get("arguments", {}))
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2, ensure_ascii=False),
                            }
                        ]
                    },
                }
            if method == "resources/list":
                resources = search.list_resources(self.analysis_dir)
                return {"jsonrpc": "2.0", "id": request_id, "result": {"resources": resources}}
            if method == "resources/read":
                resource = search.read_resource(self.analysis_dir, params["uri"])
                return {"jsonrpc": "2.0", "id": request_id, "result": {"contents": [resource]}}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            }
        except Exception as exc:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32000, "message": str(exc)},
            }


def read_message() -> dict[str, Any] | None:
    headers: dict[str, str] = {}
    while True:
        line = sys.stdin.buffer.readline()
        if not line:
            return None
        if line in (b"\r\n", b"\n"):
            break
        key, value = line.decode("utf-8").split(":", 1)
        headers[key.strip().lower()] = value.strip()

    content_length = int(headers.get("content-length", "0"))
    if content_length <= 0:
        return None
    body = sys.stdin.buffer.read(content_length)
    return json.loads(body.decode("utf-8"))


def write_message(message: dict[str, Any]) -> None:
    encoded = json.dumps(message, ensure_ascii=False).encode("utf-8")
    sys.stdout.buffer.write(f"Content-Length: {len(encoded)}\r\n\r\n".encode("utf-8"))
    sys.stdout.buffer.write(encoded)
    sys.stdout.buffer.flush()


def serve_stdio() -> None:
    server = SourceAnalyzerMcpServer()
    while True:
        request = read_message()
        if request is None:
            break
        response = server.handle_request(request)
        if response is not None:
            write_message(response)


if __name__ == "__main__":
    serve_stdio()
