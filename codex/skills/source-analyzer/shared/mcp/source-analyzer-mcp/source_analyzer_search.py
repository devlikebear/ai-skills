from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


INDEX_VERSION = 1
CACHE_DIRNAME = "source-analyzer-search"
SEARCH_DOCS_FILENAME = "search-documents.jsonl"
CHUNK_MANIFEST_FILENAME = "chunk-manifest.json"
FILE_TO_CHUNKS_FILENAME = "file-to-chunks.json"
OUTPUT_TO_CHUNKS_FILENAME = "output-to-chunks.json"
INDEX_METADATA_FILENAME = "index-metadata.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def parse_resume_session_id(resume_path: Path) -> str | None:
    if not resume_path.exists():
        return None
    matched = re.search(r"Session:\s*`([^`]+)`", resume_path.read_text(encoding="utf-8"))
    if matched:
        return matched.group(1)
    return None


def tokenize(text: str) -> list[str]:
    return re.findall(r"[\w_./-]+", text.lower(), re.UNICODE)


def first_heading(text: str, fallback: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return fallback


def session_dir(analysis_dir: Path, session_id: str) -> Path:
    return analysis_dir / "sessions" / session_id


def load_state(analysis_dir: Path, session_id: str) -> dict[str, Any]:
    path = session_dir(analysis_dir, session_id) / "state.json"
    return load_json(path)


def list_sessions(analysis_dir: Path) -> list[dict[str, Any]]:
    sessions_root = analysis_dir / "sessions"
    if not sessions_root.exists():
        return []

    sessions: list[dict[str, Any]] = []
    for state_path in sorted(sessions_root.glob("*/state.json")):
        state = load_json(state_path)
        sessions.append(
            {
                "session_id": state.get("session_id", state_path.parent.name),
                "mode": state.get("mode", ""),
                "scope": state.get("scope", ""),
                "status": state.get("status", ""),
                "commit_hash": state.get("commit_hash", ""),
                "updated_at": state.get("updated_at", ""),
                "dirty_files": state.get("dirty_files", []),
                "last_indexed_commit": state.get("last_indexed_commit"),
            }
        )
    sessions.sort(key=lambda item: (item.get("updated_at", ""), item["session_id"]), reverse=True)
    return sessions


def resolve_session_id(analysis_dir: Path, session_id: str | None = None) -> str | None:
    if session_id:
        return session_id

    from_resume = parse_resume_session_id(analysis_dir / "RESUME.md")
    if from_resume:
        return from_resume

    sessions = list_sessions(analysis_dir)
    if sessions:
        return str(sessions[0]["session_id"])
    return None


def resolve_index_dir(analysis_dir: Path) -> Path:
    return analysis_dir / "cache" / CACHE_DIRNAME


def extract_markdown_sections(rel_path: str, text: str, kind: str) -> list[dict[str, Any]]:
    heading_matches = list(re.finditer(r"^##\s+(.+)$", text, re.MULTILINE))
    docs: list[dict[str, Any]] = []
    doc_title = first_heading(text, Path(rel_path).stem.replace("-", " ").title())
    if not heading_matches:
        docs.append(
            {
                "kind": kind,
                "title": doc_title,
                "text": text.strip(),
                "source_path": rel_path,
                "related_files": [],
            }
        )
        return docs

    for index, match in enumerate(heading_matches):
        start = match.start()
        end = heading_matches[index + 1].start() if index + 1 < len(heading_matches) else len(text)
        section_heading = match.group(1).strip()
        section_text = text[start:end].strip()
        docs.append(
            {
                "kind": kind,
                "title": f"{doc_title} / {section_heading}",
                "text": section_text,
                "source_path": rel_path,
                "related_files": [],
            }
        )
    return docs


def parse_issue_candidates(rel_path: str, text: str) -> list[dict[str, Any]]:
    sections = list(re.finditer(r"^###\s+(.+)$", text, re.MULTILINE))
    if not sections:
        return []

    docs: list[dict[str, Any]] = []
    for index, match in enumerate(sections):
        start = match.start()
        end = sections[index + 1].start() if index + 1 < len(sections) else len(text)
        section_text = text[start:end].strip()
        module_match = re.search(r"- Module:\s+`([^`]+)`", section_text)
        type_match = re.search(r"- Type:\s+`([^`]+)`", section_text)
        related_files = [module_match.group(1)] if module_match else []
        docs.append(
            {
                "kind": "issue-candidate",
                "title": match.group(1).strip(),
                "text": section_text,
                "source_path": rel_path,
                "issue_type": type_match.group(1) if type_match else "",
                "related_files": related_files,
            }
        )
    return docs


def build_documents(analysis_dir: Path, session_id: str | None = None) -> list[dict[str, Any]]:
    analysis_dir = analysis_dir.resolve()
    resolved_session_id = resolve_session_id(analysis_dir, session_id)
    state = load_state(analysis_dir, resolved_session_id) if resolved_session_id else {}
    outputs_dir = analysis_dir / "outputs"
    documents: list[dict[str, Any]] = []
    module_key_files: dict[str, list[str]] = {}

    module_map_path = outputs_dir / "module-map.json"
    if module_map_path.exists():
        module_map = load_json(module_map_path)
        for name, payload in sorted(module_map.items()):
            key_files = list(payload.get("key_files", []))
            module_key_files[name] = key_files
            documents.append(
                {
                    "kind": "module-map",
                    "title": f"Module Map / {name}",
                    "text": (
                        f"Module {name}\n"
                        f"Path: {payload.get('path', '')}\n"
                        f"Responsibility: {payload.get('responsibility', '')}\n"
                        f"Key files: {', '.join(key_files)}"
                    ).strip(),
                    "source_path": "outputs/module-map.json",
                    "module": name,
                    "related_files": key_files or [payload.get("path", "")],
                }
            )

    summary_path = outputs_dir / "SUMMARY.json"
    if summary_path.exists():
        summary = load_json(summary_path)
        for module in summary.get("modules", []):
            documents.append(
                {
                    "kind": "module-summary",
                    "title": f"Summary / {module.get('name', '')}",
                    "text": module.get("summary", ""),
                    "source_path": "outputs/SUMMARY.json",
                    "module": module.get("name", ""),
                    "related_files": module_key_files.get(module.get("name", ""), []),
                }
            )

    dependency_path = outputs_dir / "dependency-graph.json"
    if dependency_path.exists():
        dependency_graph = load_json(dependency_path)
        for source_file, dependencies in sorted(dependency_graph.items()):
            dep_list = list(dependencies)
            documents.append(
                {
                    "kind": "dependency-edges",
                    "title": f"Dependencies / {source_file}",
                    "text": f"{source_file} depends on: {', '.join(dep_list)}",
                    "source_path": "outputs/dependency-graph.json",
                    "related_files": [source_file, *dep_list],
                }
            )

    for markdown_path in sorted(outputs_dir.glob("*.md")):
        rel_path = str(markdown_path.relative_to(analysis_dir))
        text = markdown_path.read_text(encoding="utf-8")
        if markdown_path.name == "issue-candidates.md":
            documents.extend(parse_issue_candidates(rel_path, text))
            continue
        documents.extend(extract_markdown_sections(rel_path, text, "output-doc"))

    modules_dir = outputs_dir / "modules"
    if modules_dir.exists():
        for module_path in sorted(modules_dir.glob("*.md")):
            rel_path = str(module_path.relative_to(analysis_dir))
            module_name = module_path.stem
            documents.append(
                {
                    "kind": "module-doc",
                    "title": first_heading(module_path.read_text(encoding="utf-8"), module_name),
                    "text": module_path.read_text(encoding="utf-8").strip(),
                    "source_path": rel_path,
                    "module": module_name,
                    "related_files": module_key_files.get(module_name, []),
                }
            )

    if resolved_session_id:
        checkpoints_dir = session_dir(analysis_dir, resolved_session_id) / "checkpoints"
        if checkpoints_dir.exists():
            for checkpoint_path in sorted(checkpoints_dir.glob("checkpoint-*.md")):
                rel_path = str(checkpoint_path.relative_to(analysis_dir))
                documents.append(
                    {
                        "kind": "checkpoint-summary",
                        "title": first_heading(checkpoint_path.read_text(encoding="utf-8"), checkpoint_path.stem),
                        "text": checkpoint_path.read_text(encoding="utf-8").strip(),
                        "source_path": rel_path,
                        "related_files": list(state.get("dirty_files", [])),
                    }
                )

    for index, document in enumerate(documents, start=1):
        document["id"] = f"chunk-{index:04d}"
        document["session_id"] = resolved_session_id
        document["commit"] = state.get("commit_hash", "")
        document["aliases"] = dedupe(
            [
                document.get("title", ""),
                document.get("module", ""),
                document.get("issue_type", ""),
                document.get("source_path", ""),
                *document.get("related_files", []),
            ]
        )
        document["snippet"] = document.get("text", "")[:240]
    return documents


def dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        value = item.strip()
        if not value or value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def generate_search_index(analysis_dir: Path, session_id: str | None = None) -> dict[str, Any]:
    analysis_dir = analysis_dir.resolve()
    documents = build_documents(analysis_dir, session_id=session_id)
    resolved_session_id = resolve_session_id(analysis_dir, session_id)
    state = load_state(analysis_dir, resolved_session_id) if resolved_session_id else {}
    index_dir = resolve_index_dir(analysis_dir)
    index_dir.mkdir(parents=True, exist_ok=True)

    file_to_chunks: dict[str, list[str]] = {}
    output_to_chunks: dict[str, list[str]] = {}
    manifest: list[dict[str, Any]] = []
    for doc in documents:
        manifest.append(
            {
                "id": doc["id"],
                "kind": doc["kind"],
                "title": doc["title"],
                "source_path": doc["source_path"],
                "session_id": doc.get("session_id"),
                "related_files": doc.get("related_files", []),
            }
        )
        output_to_chunks.setdefault(doc["source_path"], []).append(doc["id"])
        for related_file in doc.get("related_files", []):
            file_to_chunks.setdefault(related_file, []).append(doc["id"])

    metadata = {
        "index_version": INDEX_VERSION,
        "generated_at": now_iso(),
        "session_id": resolved_session_id,
        "commit_hash": state.get("commit_hash", ""),
        "chunk_count": len(documents),
        "output_count": len(output_to_chunks),
    }

    write_jsonl(index_dir / SEARCH_DOCS_FILENAME, documents)
    save_json(index_dir / CHUNK_MANIFEST_FILENAME, manifest)
    save_json(index_dir / FILE_TO_CHUNKS_FILENAME, file_to_chunks)
    save_json(index_dir / OUTPUT_TO_CHUNKS_FILENAME, output_to_chunks)
    save_json(index_dir / INDEX_METADATA_FILENAME, metadata)
    return metadata


def load_index_documents(analysis_dir: Path) -> list[dict[str, Any]] | None:
    docs_path = resolve_index_dir(analysis_dir) / SEARCH_DOCS_FILENAME
    if not docs_path.exists():
        return None
    documents: list[dict[str, Any]] = []
    for line in docs_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            documents.append(json.loads(line))
    return documents


def score_document(doc: dict[str, Any], query: str, query_tokens: list[str]) -> int:
    haystacks = {
        "title": doc.get("title", "").lower(),
        "text": doc.get("text", "").lower(),
        "source_path": doc.get("source_path", "").lower(),
        "aliases": " ".join(item.lower() for item in doc.get("aliases", [])),
        "related_files": " ".join(item.lower() for item in doc.get("related_files", [])),
        "kind": doc.get("kind", "").lower(),
    }
    score = 0
    for token in query_tokens:
        if token in haystacks["title"]:
            score += 10
        if token in haystacks["aliases"]:
            score += 8
        if token in haystacks["related_files"]:
            score += 7
        if token in haystacks["source_path"]:
            score += 6
        if token in haystacks["kind"]:
            score += 4
        if token in haystacks["text"]:
            score += 2

    if query and query in haystacks["title"]:
        score += 12
    if query and query in haystacks["text"]:
        score += 6
    if query_tokens and all(token in haystacks["text"] for token in query_tokens):
        score += 10
    return score


def _slim_result(doc: dict[str, Any], snippet_len: int = 240, module_context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return a lightweight result with snippet instead of full text."""
    text = doc.get("text", "")
    result: dict[str, Any] = {
        "id": doc.get("id", ""),
        "kind": doc.get("kind", ""),
        "title": doc.get("title", ""),
        "snippet": text[:snippet_len],
        "source_path": doc.get("source_path", ""),
        "score": doc.get("score", 0),
    }
    if module_context:
        result["module_context"] = module_context
    return result


def _build_module_context_map(analysis_dir: Path) -> dict[str, dict[str, Any]]:
    """Build a map from module name to its summary for enriching search results."""
    context_map: dict[str, dict[str, Any]] = {}
    module_map_path = analysis_dir / "outputs" / "module-map.json"
    if not module_map_path.exists():
        return context_map
    module_map = load_json(module_map_path)
    for name, payload in module_map.items():
        context_map[name] = {
            "module": name,
            "path": payload.get("path", ""),
            "responsibility": payload.get("responsibility", ""),
            "key_files": payload.get("key_files", []),
        }
    return context_map


def _find_module_context(doc: dict[str, Any], context_map: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    """Find the module context entry that best matches a document."""
    module_name = doc.get("module", "")
    if module_name and module_name in context_map:
        return context_map[module_name]
    source_path = doc.get("source_path", "")
    for name, ctx in context_map.items():
        module_path = ctx.get("path", "")
        if module_path and source_path.startswith(module_path):
            return ctx
    return None


def search_analysis(
    analysis_dir: Path,
    query: str,
    top_k: int = 5,
    kinds: list[str] | None = None,
    session_id: str | None = None,
    snippet_only: bool = False,
    snippet_len: int = 240,
) -> list[dict[str, Any]]:
    analysis_dir = analysis_dir.resolve()
    documents = load_index_documents(analysis_dir)
    if documents is None:
        documents = build_documents(analysis_dir, session_id=session_id)

    requested_kinds = {kind.lower() for kind in (kinds or [])}
    query_normalized = query.strip().lower()
    query_tokens = tokenize(query_normalized)
    scored: list[tuple[int, dict[str, Any]]] = []
    for doc in documents:
        if session_id and doc.get("session_id") not in {None, session_id}:
            continue
        if requested_kinds and doc.get("kind", "").lower() not in requested_kinds:
            continue
        score = score_document(doc, query_normalized, query_tokens)
        if score <= 0:
            continue
        scored.append((score, doc))

    scored.sort(key=lambda item: (-item[0], item[1].get("title", "")))

    module_context_map: dict[str, dict[str, Any]] | None = None
    if snippet_only:
        module_context_map = _build_module_context_map(analysis_dir)

    results: list[dict[str, Any]] = []
    for score, doc in scored[:top_k]:
        result = dict(doc)
        result["score"] = score
        if snippet_only and module_context_map is not None:
            ctx = _find_module_context(doc, module_context_map)
            result = _slim_result(result, snippet_len=snippet_len, module_context=ctx)
        results.append(result)
    return results


def get_brief(analysis_dir: Path) -> dict[str, Any]:
    """Return a compact project context in a single call."""
    analysis_dir = analysis_dir.resolve()
    result: dict[str, Any] = {}

    overview_path = analysis_dir / "outputs" / "overview.md"
    if overview_path.exists():
        text = overview_path.read_text(encoding="utf-8")
        result["overview_snippet"] = text[:600]

    module_map_path = analysis_dir / "outputs" / "module-map.json"
    if module_map_path.exists():
        module_map = load_json(module_map_path)
        result["modules"] = {
            name: {
                "path": payload.get("path", ""),
                "responsibility": payload.get("responsibility", ""),
                "key_files": payload.get("key_files", []),
            }
            for name, payload in module_map.items()
        }

    issue_path = analysis_dir / "outputs" / "issue-candidates.md"
    if issue_path.exists():
        issues = parse_issue_candidates("outputs/issue-candidates.md", issue_path.read_text(encoding="utf-8"))
        result["issue_count"] = len(issues)
        result["issue_titles"] = [issue.get("title", "") for issue in issues[:10]]

    summary_path = analysis_dir / "outputs" / "SUMMARY.json"
    if summary_path.exists():
        summary = load_json(summary_path)
        result["status"] = summary.get("status", "")
        result["commit"] = summary.get("commit", "")
        result["visited_count"] = summary.get("visited_count", 0)

    return result


def trace_dependencies(
    analysis_dir: Path,
    path: str,
    depth: int = 1,
    session_id: str | None = None,
) -> dict[str, Any]:
    _ = session_id
    dependency_path = analysis_dir / "outputs" / "dependency-graph.json"
    if not dependency_path.exists():
        return {"path": path, "dependencies": [], "depth": depth}

    dependency_graph = load_json(dependency_path)
    frontier = [path]
    seen = {path}
    dependencies: list[str] = []
    for _level in range(max(depth, 0)):
        next_frontier: list[str] = []
        for node in frontier:
            for dependency in dependency_graph.get(node, []):
                if dependency in seen:
                    continue
                seen.add(dependency)
                dependencies.append(dependency)
                next_frontier.append(dependency)
        frontier = next_frontier
        if not frontier:
            break

    return {"path": path, "dependencies": dependencies, "depth": depth}


def get_overview(analysis_dir: Path) -> dict[str, Any]:
    overview_path = analysis_dir / "outputs" / "overview.md"
    if not overview_path.exists():
        raise FileNotFoundError("overview.md not found")
    return {
        "path": "outputs/overview.md",
        "content": overview_path.read_text(encoding="utf-8"),
    }


def get_module(analysis_dir: Path, name_or_path: str) -> dict[str, Any]:
    modules_dir = analysis_dir / "outputs" / "modules"
    if modules_dir.exists():
        for module_path in sorted(modules_dir.glob("*.md")):
            if module_path.stem == name_or_path or str(module_path) == name_or_path or f"outputs/modules/{module_path.name}" == name_or_path:
                return {
                    "path": str(module_path.relative_to(analysis_dir)),
                    "content": module_path.read_text(encoding="utf-8"),
                }

    module_map_path = analysis_dir / "outputs" / "module-map.json"
    if module_map_path.exists():
        module_map = load_json(module_map_path)
        for module_name, payload in module_map.items():
            if name_or_path in {module_name, payload.get("path", "")}:
                return {
                    "path": "outputs/module-map.json",
                    "content": json.dumps(payload, indent=2, ensure_ascii=False),
                }
    raise FileNotFoundError(f"module not found: {name_or_path}")


def get_issue_candidates(analysis_dir: Path, issue_type: str | None = None) -> list[dict[str, Any]]:
    issue_path = analysis_dir / "outputs" / "issue-candidates.md"
    if not issue_path.exists():
        return []
    issues = parse_issue_candidates("outputs/issue-candidates.md", issue_path.read_text(encoding="utf-8"))
    if issue_type:
        return [issue for issue in issues if issue.get("issue_type", "").lower() == issue_type.lower()]
    return issues


def get_resume_state(analysis_dir: Path, session_id: str | None = None) -> dict[str, Any]:
    resolved_session_id = resolve_session_id(analysis_dir, session_id)
    return {
        "resume_path": "RESUME.md",
        "resume": (analysis_dir / "RESUME.md").read_text(encoding="utf-8") if (analysis_dir / "RESUME.md").exists() else "",
        "session_id": resolved_session_id,
        "state": load_state(analysis_dir, resolved_session_id) if resolved_session_id else {},
    }


def get_changed_context(
    analysis_dir: Path,
    from_commit: str | None = None,
    to_commit: str | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    resolved_session_id = resolve_session_id(analysis_dir, session_id)
    state = load_state(analysis_dir, resolved_session_id) if resolved_session_id else {}
    return {
        "session_id": resolved_session_id,
        "requested_from_commit": from_commit,
        "requested_to_commit": to_commit,
        "commit_hash": state.get("commit_hash", ""),
        "last_indexed_commit": state.get("last_indexed_commit"),
        "dirty_files": state.get("dirty_files", []),
    }


def get_checkpoint(analysis_dir: Path, session_id: str | None = None, checkpoint_id: int | None = None) -> dict[str, Any]:
    resolved_session_id = resolve_session_id(analysis_dir, session_id)
    if not resolved_session_id:
        raise FileNotFoundError("no session found")
    state = load_state(analysis_dir, resolved_session_id)
    checkpoints = list(state.get("checkpoints", []))
    if not checkpoints:
        raise FileNotFoundError("no checkpoints found")
    if checkpoint_id is None:
        checkpoint = checkpoints[-1]
    else:
        matching = [item for item in checkpoints if int(item.get("id", -1)) == checkpoint_id]
        if not matching:
            raise FileNotFoundError(f"checkpoint not found: {checkpoint_id}")
        checkpoint = matching[0]
    checkpoint_path = analysis_dir / "sessions" / resolved_session_id / checkpoint["file"]
    return {
        "session_id": resolved_session_id,
        "checkpoint": checkpoint,
        "content": checkpoint_path.read_text(encoding="utf-8"),
    }


def list_resources(analysis_dir: Path, session_id: str | None = None) -> list[dict[str, Any]]:
    resources: list[dict[str, Any]] = []
    base_files = [
        ("analysis://overview", "outputs/overview.md", "Overview", "text/markdown"),
        ("analysis://architecture", "outputs/architecture.md", "Architecture", "text/markdown"),
        ("analysis://module-map", "outputs/module-map.json", "Module Map", "application/json"),
        ("analysis://dependency-graph", "outputs/dependency-graph.json", "Dependency Graph", "application/json"),
        ("analysis://issues", "outputs/issue-candidates.md", "Issue Candidates", "text/markdown"),
        ("analysis://resume", "RESUME.md", "Resume Pointer", "text/markdown"),
    ]
    for uri, rel_path, name, mime_type in base_files:
        path = analysis_dir / rel_path
        if path.exists():
            resources.append({"uri": uri, "name": name, "mimeType": mime_type})

    modules_dir = analysis_dir / "outputs" / "modules"
    if modules_dir.exists():
        for module_path in sorted(modules_dir.glob("*.md")):
            resources.append(
                {
                    "uri": f"analysis://modules/{module_path.stem}",
                    "name": f"Module / {module_path.stem}",
                    "mimeType": "text/markdown",
                }
            )

    for item in list_sessions(analysis_dir):
        resources.append(
            {
                "uri": f"analysis://sessions/{item['session_id']}/state",
                "name": f"Session State / {item['session_id']}",
                "mimeType": "application/json",
            }
        )
    return resources


def read_resource(analysis_dir: Path, uri: str, session_id: str | None = None) -> dict[str, Any]:
    resolved_session_id = resolve_session_id(analysis_dir, session_id)
    if uri == "analysis://overview":
        path = analysis_dir / "outputs" / "overview.md"
        return {"uri": uri, "mimeType": "text/markdown", "text": path.read_text(encoding="utf-8")}
    if uri == "analysis://architecture":
        path = analysis_dir / "outputs" / "architecture.md"
        return {"uri": uri, "mimeType": "text/markdown", "text": path.read_text(encoding="utf-8")}
    if uri == "analysis://module-map":
        path = analysis_dir / "outputs" / "module-map.json"
        return {"uri": uri, "mimeType": "application/json", "text": path.read_text(encoding="utf-8")}
    if uri == "analysis://dependency-graph":
        path = analysis_dir / "outputs" / "dependency-graph.json"
        return {"uri": uri, "mimeType": "application/json", "text": path.read_text(encoding="utf-8")}
    if uri == "analysis://issues":
        path = analysis_dir / "outputs" / "issue-candidates.md"
        return {"uri": uri, "mimeType": "text/markdown", "text": path.read_text(encoding="utf-8")}
    if uri == "analysis://resume":
        path = analysis_dir / "RESUME.md"
        return {"uri": uri, "mimeType": "text/markdown", "text": path.read_text(encoding="utf-8")}
    if uri.startswith("analysis://modules/"):
        module_name = uri.split("/", 3)[-1]
        module_path = analysis_dir / "outputs" / "modules" / f"{module_name}.md"
        return {"uri": uri, "mimeType": "text/markdown", "text": module_path.read_text(encoding="utf-8")}
    if uri.startswith("analysis://sessions/") and uri.endswith("/state"):
        target_session = uri.split("/")[3]
        state = load_state(analysis_dir, target_session)
        return {
            "uri": uri,
            "mimeType": "application/json",
            "text": json.dumps(state, indent=2, ensure_ascii=False),
        }
    raise FileNotFoundError(f"resource not found: {uri} (session={resolved_session_id})")
