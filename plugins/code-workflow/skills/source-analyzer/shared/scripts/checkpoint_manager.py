#!/usr/bin/env python3
"""Checkpoint manager for resumable source-analyzer runs."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_FILENAME = "state.json"
INDEX_FILENAME = "index.md"
RESUME_FILENAME = "RESUME.md"
SUMMARY_FILENAME = "SUMMARY.json"

DEFAULT_EXCLUDE_PATTERNS: list[str] = [
    ".analysis/",
    ".codex/",
    ".claude/",
    ".git/",
    "vendor/",
    "node_modules/",
    ".venv/",
    "__pycache__/",
    "dist/",
    "build/",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def now_for_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def ensure_layout(analysis_dir: Path) -> None:
    (analysis_dir / "sessions").mkdir(parents=True, exist_ok=True)
    (analysis_dir / "outputs").mkdir(parents=True, exist_ok=True)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def dedupe_keep_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        value = item.strip()
        if not value or value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def get_head_commit() -> str:
    """현재 HEAD 커밋 해시(full SHA) 반환."""
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


def should_exclude(filepath: str, exclude_patterns: list[str] | None = None) -> bool:
    """Check if a file path matches any exclude pattern."""
    patterns = exclude_patterns or DEFAULT_EXCLUDE_PATTERNS
    for pattern in patterns:
        if pattern.endswith("/"):
            if filepath.startswith(pattern) or f"/{pattern}" in f"/{filepath}":
                return True
        elif filepath.endswith(pattern) or filepath == pattern:
            return True
    return False


def get_committed_files(scope: str, exclude_patterns: list[str] | None = None) -> list[str]:
    """HEAD에서 scope 경로 아래 추적 파일 목록 반환 (exclude 패턴 적용)."""
    result = subprocess.run(
        ["git", "ls-tree", "-r", "HEAD", "--name-only", "--", scope],
        capture_output=True, text=True, check=True,
    )
    files = [f for f in result.stdout.strip().splitlines() if f]
    return [f for f in files if not should_exclude(f, exclude_patterns)]


def get_changed_files(old_commit: str, new_commit: str) -> list[str]:
    """두 커밋 사이 변경된 파일 목록 반환 (삭제 제외)."""
    result = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=ACMR", old_commit, new_commit],
        capture_output=True, text=True, check=True,
    )
    return [f for f in result.stdout.strip().splitlines() if f]


def commit_hash_valid(commit: str) -> bool:
    """커밋 해시가 리포지토리에 존재하는지 확인."""
    result = subprocess.run(
        ["git", "cat-file", "-t", commit],
        capture_output=True, text=True,
    )
    return result.returncode == 0 and "commit" in result.stdout


def migrate_state(state: dict[str, Any]) -> dict[str, Any]:
    """v1 → v2 마이그레이션: commit_hash 필드 추가."""
    if state.get("version", 1) >= 2:
        state.setdefault("dirty_files", [])
        state.setdefault("last_indexed_commit", None)
        return state
    state["version"] = 2
    state["commit_hash"] = None
    state["dirty_files"] = []
    state["last_indexed_commit"] = None
    return state


def generate_session_id(mode: str) -> str:
    return f"{mode}-{now_for_id()}"


def session_path(analysis_dir: Path, session_id: str) -> Path:
    return analysis_dir / "sessions" / session_id


def state_path(analysis_dir: Path, session_id: str) -> Path:
    return session_path(analysis_dir, session_id) / STATE_FILENAME


def load_state(analysis_dir: Path, session_id: str) -> dict[str, Any]:
    path = state_path(analysis_dir, session_id)
    if not path.exists():
        raise FileNotFoundError(f"state file not found: {path}")
    return load_json(path)


def save_state(analysis_dir: Path, session_id: str, state: dict[str, Any]) -> None:
    save_json(state_path(analysis_dir, session_id), state)


def parse_resume_session_id(resume_path: Path) -> str | None:
    if not resume_path.exists():
        return None

    content = resume_path.read_text(encoding="utf-8")
    matched = re.search(r"Session:\s*`([^`]+)`", content)
    if matched:
        return matched.group(1)
    return None


def find_latest_resumable_session(analysis_dir: Path, mode: str | None = None) -> str | None:
    sessions_dir = analysis_dir / "sessions"
    if not sessions_dir.exists():
        return None

    candidates: list[tuple[str, str]] = []
    for state_file in sessions_dir.glob(f"*/{STATE_FILENAME}"):
        state = load_json(state_file)
        if state.get("status") == "completed":
            continue
        if mode and state.get("mode") != mode:
            continue
        updated_at = str(state.get("updated_at", ""))
        candidates.append((updated_at, str(state.get("session_id", state_file.parent.name))))

    if not candidates:
        return None

    candidates.sort(reverse=True)
    return candidates[0][1]


def latest_checkpoint_file(state: dict[str, Any]) -> str | None:
    checkpoints = state.get("checkpoints", [])
    if not checkpoints:
        return None
    latest = checkpoints[-1]
    return str(latest.get("file", "")).strip() or None


def write_resume_file(analysis_dir: Path, session_id: str) -> None:
    state = load_state(analysis_dir, session_id)
    checkpoint_file = latest_checkpoint_file(state)
    checkpoint_ref = checkpoint_file if checkpoint_file else "(no checkpoints yet)"
    resume_path = analysis_dir / RESUME_FILENAME
    commit = state.get("commit_hash", "(unknown)")
    resume_path.write_text(
        (
            "# Source Analyzer Resume Pointer\n\n"
            f"- Session: `{session_id}`\n"
            f"- Mode: `{state.get('mode', '')}`\n"
            f"- Scope: `{state.get('scope', '')}`\n"
            f"- State: `{state.get('status', '')}`\n"
            f"- Commit: `{commit}`\n"
            f"- Next Checkpoint Number: `{state.get('next_checkpoint', 1):03d}`\n"
            f"- Last Checkpoint File: `{checkpoint_ref}`\n"
            f"- Updated At (UTC): `{state.get('updated_at', '')}`\n\n"
            "Resume steps:\n"
            "1. Open this session's `index.md`.\n"
            "2. Run `sync` to detect new commits.\n"
            "3. Open `state.json` and continue from `frontier`.\n"
            "4. Write the next `checkpoints/checkpoint-XXX.md`.\n"
        ),
        encoding="utf-8",
    )


def initialize_index_markdown(session_id: str, mode: str, scope: str) -> str:
    return (
        "# Source Analyzer Session Index\n\n"
        f"- Session ID: `{session_id}`\n"
        f"- Mode: `{mode}`\n"
        f"- Scope: `{scope}`\n"
        f"- Created At (UTC): `{now_iso()}`\n\n"
        "## Checkpoints\n\n"
        "| ID | File | Title | Status | Created At (UTC) |\n"
        "|----|------|-------|--------|------------------|\n"
    )


def append_checkpoint_index_row(
    analysis_dir: Path,
    session_id: str,
    checkpoint_no: int,
    checkpoint_file: str,
    title: str,
    status: str,
    created_at: str,
) -> None:
    index_path = session_path(analysis_dir, session_id) / INDEX_FILENAME
    row = f"| {checkpoint_no:03d} | `{checkpoint_file}` | {title} | `{status}` | `{created_at}` |\n"
    with index_path.open("a", encoding="utf-8") as fh:
        fh.write(row)


def init_session(
    analysis_dir: Path,
    mode: str,
    scope: str,
    session_id: str | None = None,
    resume_if_exists: bool = True,
    commit_hash: str | None = None,
    exclude_patterns: list[str] | None = None,
) -> dict[str, Any]:
    ensure_layout(analysis_dir)

    if session_id is None and resume_if_exists:
        existing = find_latest_resumable_session(analysis_dir, mode=mode)
        if existing:
            state = migrate_state(load_state(analysis_dir, existing))
            save_state(analysis_dir, existing, state)
            write_resume_file(analysis_dir, existing)
            return {
                "session_id": existing,
                "session_dir": session_path(analysis_dir, existing),
                "resumed": True,
                "commit_hash": state.get("commit_hash"),
            }

    final_session_id = session_id or generate_session_id(mode)
    session_dir = session_path(analysis_dir, final_session_id)
    if session_dir.exists():
        raise FileExistsError(f"session already exists: {session_dir}")

    (session_dir / "checkpoints").mkdir(parents=True, exist_ok=False)
    (session_dir / "outputs").mkdir(parents=True, exist_ok=False)

    effective_commit = commit_hash or get_head_commit()
    effective_excludes = list(DEFAULT_EXCLUDE_PATTERNS) + (exclude_patterns or [])
    now = now_iso()
    state: dict[str, Any] = {
        "version": 2,
        "session_id": final_session_id,
        "mode": mode,
        "scope": scope,
        "status": "in_progress",
        "created_at": now,
        "updated_at": now,
        "commit_hash": effective_commit,
        "exclude_patterns": effective_excludes,
        "next_checkpoint": 1,
        "visited": [],
        "frontier": [],
        "outputs": [],
        "checkpoints": [],
        "dirty_files": [],
        "last_indexed_commit": None,
    }

    save_state(analysis_dir, final_session_id, state)
    (session_dir / INDEX_FILENAME).write_text(
        initialize_index_markdown(final_session_id, mode, scope),
        encoding="utf-8",
    )
    write_resume_file(analysis_dir, final_session_id)
    return {
        "session_id": final_session_id,
        "session_dir": session_dir,
        "resumed": False,
        "commit_hash": effective_commit,
    }


def render_list(items: list[str]) -> str:
    if not items:
        return "- (none)"
    return "\n".join(f"- `{item}`" for item in items)


def add_checkpoint(
    analysis_dir: Path,
    session_id: str,
    title: str,
    summary: str = "",
    visited_add: list[str] | None = None,
    queue_add: list[str] | None = None,
    queue_done: list[str] | None = None,
    outputs: list[str] | None = None,
    status: str = "in_progress",
    next_actions: list[str] | None = None,
) -> dict[str, Any]:
    if status not in {"in_progress", "paused", "completed"}:
        raise ValueError("status must be one of: in_progress, paused, completed")

    state = load_state(analysis_dir, session_id)
    visited_add = visited_add or []
    queue_add = queue_add or []
    queue_done = queue_done or []
    outputs = outputs or []
    next_actions = next_actions or []

    if not visited_add and not outputs and not summary.strip() and not next_actions:
        raise ValueError(
            "empty checkpoint: provide at least one of --visited-add, --outputs, --summary, or --next-actions"
        )

    visited = dedupe_keep_order(list(state.get("visited", [])) + visited_add)

    done_set = {entry.strip() for entry in queue_done if entry.strip()}
    frontier = [entry for entry in list(state.get("frontier", [])) if entry not in done_set]
    frontier = dedupe_keep_order(frontier + queue_add)

    output_files = dedupe_keep_order(list(state.get("outputs", [])) + outputs)

    checkpoint_no = int(state.get("next_checkpoint", 1))
    checkpoint_filename = f"checkpoint-{checkpoint_no:03d}.md"
    checkpoint_path = session_path(analysis_dir, session_id) / "checkpoints" / checkpoint_filename
    now = now_iso()

    commit = state.get("commit_hash", "(unknown)")
    checkpoint_md = (
        f"# Checkpoint {checkpoint_no:03d}: {title}\n\n"
        f"> Session: `{session_id}`\n"
        f"> Mode: `{state.get('mode', '')}`\n"
        f"> Scope: `{state.get('scope', '')}`\n"
        f"> Status: `{status}`\n"
        f"> Commit: `{commit}`\n"
        f"> Created At (UTC): `{now}`\n\n"
        "## Summary\n\n"
        f"{summary.strip() or '(no summary provided)'}\n\n"
        "## Newly Visited Nodes\n\n"
        f"{render_list(dedupe_keep_order(visited_add))}\n\n"
        "## Remaining Frontier\n\n"
        f"{render_list(frontier)}\n\n"
        "## Produced or Updated Documents\n\n"
        f"{render_list(dedupe_keep_order(outputs))}\n\n"
        "## Next Actions\n\n"
        f"{render_list(dedupe_keep_order(next_actions))}\n\n"
        "## Resume Instructions\n\n"
        "1. Open this checkpoint file first.\n"
        "2. Continue from `state.json.frontier`.\n"
        "3. Record the next progress as the next checkpoint.\n"
    )
    checkpoint_path.write_text(checkpoint_md, encoding="utf-8")

    state["visited"] = visited
    state["frontier"] = frontier
    state["outputs"] = output_files
    state["status"] = status
    state["updated_at"] = now
    state["next_checkpoint"] = checkpoint_no + 1
    state_checkpoints = list(state.get("checkpoints", []))
    state_checkpoints.append(
        {
            "id": checkpoint_no,
            "file": f"checkpoints/{checkpoint_filename}",
            "title": title,
            "status": status,
            "created_at": now,
        }
    )
    state["checkpoints"] = state_checkpoints
    save_state(analysis_dir, session_id, state)

    append_checkpoint_index_row(
        analysis_dir=analysis_dir,
        session_id=session_id,
        checkpoint_no=checkpoint_no,
        checkpoint_file=f"checkpoints/{checkpoint_filename}",
        title=title,
        status=status,
        created_at=now,
    )
    write_resume_file(analysis_dir, session_id)

    publish_result = None
    if status in {"paused", "completed"}:
        publish_result = publish_outputs(analysis_dir, session_id)

    return {
        "session_id": session_id,
        "checkpoint_no": checkpoint_no,
        "checkpoint_path": checkpoint_path,
        "published": publish_result,
    }


def sync_session(
    analysis_dir: Path,
    session_id: str,
    scope: str | None = None,
) -> dict[str, Any]:
    """HEAD와 체크포인트 커밋을 비교하여 변경 파일을 frontier에 추가."""
    state = migrate_state(load_state(analysis_dir, session_id))
    old_commit = state.get("commit_hash")
    new_commit = get_head_commit()

    if old_commit and old_commit == new_commit:
        save_state(analysis_dir, session_id, state)
        return {
            "session_id": session_id,
            "status": "unchanged",
            "commit_hash": new_commit,
            "changed_files": [],
        }

    effective_scope = scope or state.get("scope", ".")

    excludes = state.get("exclude_patterns", DEFAULT_EXCLUDE_PATTERNS)

    if old_commit and commit_hash_valid(old_commit):
        changed = get_changed_files(old_commit, new_commit)
        changed = [f for f in changed if f.startswith(effective_scope) and not should_exclude(f, excludes)]
    else:
        changed = get_committed_files(effective_scope, exclude_patterns=excludes)

    visited_set = set(state.get("visited", []))
    for f in changed:
        visited_set.discard(f)
    state["visited"] = [v for v in state.get("visited", []) if v in visited_set]

    state["frontier"] = dedupe_keep_order(list(state.get("frontier", [])) + changed)
    state["dirty_files"] = dedupe_keep_order(list(state.get("dirty_files", [])) + changed)
    state["commit_hash"] = new_commit
    state["updated_at"] = now_iso()
    save_state(analysis_dir, session_id, state)
    write_resume_file(analysis_dir, session_id)

    return {
        "session_id": session_id,
        "status": "synced",
        "old_commit": old_commit,
        "commit_hash": new_commit,
        "changed_files": changed,
    }


def resolve_session_id(
    analysis_dir: Path,
    session_id: str | None,
    mode: str | None = None,
) -> str:
    if session_id:
        return session_id

    from_resume = parse_resume_session_id(analysis_dir / RESUME_FILENAME)
    if from_resume:
        return from_resume

    latest = find_latest_resumable_session(analysis_dir, mode=mode)
    if latest:
        return latest
    raise RuntimeError("no resumable session found; create one with `init` first")


def status_summary(analysis_dir: Path, session_id: str) -> str:
    state = load_state(analysis_dir, session_id)
    latest_cp = latest_checkpoint_file(state) or "(no checkpoints yet)"
    commit = state.get("commit_hash", "(unknown)")
    return (
        f"session_id={session_id}\n"
        f"mode={state.get('mode', '')}\n"
        f"scope={state.get('scope', '')}\n"
        f"status={state.get('status', '')}\n"
        f"commit_hash={commit}\n"
        f"next_checkpoint={int(state.get('next_checkpoint', 1)):03d}\n"
        f"visited={len(state.get('visited', []))}\n"
        f"frontier={len(state.get('frontier', []))}\n"
        f"latest_checkpoint={latest_cp}\n"
    )


def publish_outputs(analysis_dir: Path, session_id: str) -> dict[str, Any]:
    """Copy session outputs to .analysis/outputs/ for git tracking.

    Only the published outputs directory is meant to be committed to git.
    Session working state (checkpoints, state.json, etc.) stays git-ignored.
    """
    state = load_state(analysis_dir, session_id)
    sdir = session_path(analysis_dir, session_id)
    session_outputs = sdir / "outputs"
    published_dir = analysis_dir / "outputs"

    if not session_outputs.exists():
        return {"session_id": session_id, "published": [], "target": str(published_dir), "search_index": None}

    published_dir.mkdir(parents=True, exist_ok=True)

    published: list[str] = []
    for item in sorted(session_outputs.rglob("*")):
        if item.is_dir():
            continue
        rel = item.relative_to(session_outputs)
        dest = published_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, dest)
        published.append(str(rel))

    search_index = generate_search_index_for_session(analysis_dir, session_id)

    return {
        "session_id": session_id,
        "published": published,
        "target": str(published_dir),
        "search_index": search_index,
    }


def generate_summary(analysis_dir: Path, session_id: str) -> dict[str, Any]:
    """Generate SUMMARY.json from session outputs for AI consumption."""
    state = load_state(analysis_dir, session_id)
    sdir = session_path(analysis_dir, session_id)
    outputs_dir = sdir / "outputs"

    modules: list[dict[str, str]] = []
    modules_dir = outputs_dir / "modules"
    if modules_dir.exists():
        for md_file in sorted(modules_dir.glob("*.md")):
            first_line = ""
            for line in md_file.read_text(encoding="utf-8").splitlines():
                stripped = line.strip()
                if stripped and not stripped.startswith("#"):
                    first_line = stripped
                    break
            modules.append({
                "name": md_file.stem,
                "file": f"outputs/modules/{md_file.name}",
                "summary": first_line[:200],
            })

    summary: dict[str, Any] = {
        "session_id": session_id,
        "mode": state.get("mode", ""),
        "scope": state.get("scope", ""),
        "status": state.get("status", ""),
        "commit": state.get("commit_hash", ""),
        "visited_count": len(state.get("visited", [])),
        "frontier_count": len(state.get("frontier", [])),
        "modules": modules,
        "outputs": [f"outputs/{o.split('outputs/')[-1]}" if "outputs/" in o else o for o in state.get("outputs", [])],
        "checkpoints_count": len(state.get("checkpoints", [])),
    }

    summary_path = sdir / "outputs" / SUMMARY_FILENAME
    save_json(summary_path, summary)
    return summary


def load_search_module() -> Any:
    module_path = Path(__file__).with_name("source_analyzer_search.py")
    spec = importlib.util.spec_from_file_location("source_analyzer_search", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load search module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def generate_search_index_for_session(analysis_dir: Path, session_id: str) -> dict[str, Any]:
    search_module = load_search_module()
    result = search_module.generate_search_index(analysis_dir, session_id=session_id)
    state = migrate_state(load_state(analysis_dir, session_id))
    state["dirty_files"] = []
    state["last_indexed_commit"] = state.get("commit_hash")
    state["updated_at"] = now_iso()
    save_state(analysis_dir, session_id, state)
    return result


def migrate_layout(analysis_dir: Path) -> dict[str, Any]:
    """Migrate from old layout (outputs inside sessions) to new layout.

    1. Find the latest session with outputs.
    2. Publish those outputs to .analysis/outputs/.
    3. Return migration details.
    """
    sessions_dir = analysis_dir / "sessions"
    published_dir = analysis_dir / "outputs"

    if not sessions_dir.exists():
        return {"migrated": False, "reason": "no sessions directory"}

    # Find all sessions ordered by updated_at (latest first)
    candidates: list[tuple[str, str, Path]] = []
    for state_file in sessions_dir.glob(f"*/{STATE_FILENAME}"):
        state = load_json(state_file)
        updated_at = str(state.get("updated_at", ""))
        sid = str(state.get("session_id", state_file.parent.name))
        outputs_dir = state_file.parent / "outputs"
        if outputs_dir.exists() and any(outputs_dir.iterdir()):
            candidates.append((updated_at, sid, outputs_dir))

    if not candidates:
        return {"migrated": False, "reason": "no sessions with outputs found"}

    candidates.sort(reverse=True)
    published_dir.mkdir(parents=True, exist_ok=True)

    all_published: list[str] = []
    source_session = candidates[0][1]

    # Publish from latest session
    session_outputs = candidates[0][2]
    for item in sorted(session_outputs.rglob("*")):
        if item.is_dir():
            continue
        rel = item.relative_to(session_outputs)
        dest = published_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, dest)
        all_published.append(str(rel))

    return {
        "migrated": True,
        "source_session": source_session,
        "published": all_published,
        "target": str(published_dir),
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage source-analyzer incremental checkpoints.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create or resume a session.")
    init_parser.add_argument("--analysis-dir", default=".analysis")
    init_parser.add_argument("--mode", required=True, choices=["analyze", "refactor-guide", "overhaul"])
    init_parser.add_argument("--scope", required=True)
    init_parser.add_argument("--session-id")
    init_parser.add_argument("--no-resume", action="store_true")
    init_parser.add_argument("--commit", help="Initial commit hash to record.")
    init_parser.add_argument("--exclude", nargs="*", default=[], help="Additional exclude patterns.")

    sync_parser = subparsers.add_parser("sync", help="Sync session with latest HEAD commit.")
    sync_parser.add_argument("--analysis-dir", default=".analysis")
    sync_parser.add_argument("--session-id")
    sync_parser.add_argument("--mode", choices=["analyze", "refactor-guide", "overhaul"])
    sync_parser.add_argument("--scope")
    sync_parser.add_argument("--exclude", nargs="*", default=[], help="Additional exclude patterns.")

    checkpoint_parser = subparsers.add_parser("checkpoint", help="Write a checkpoint markdown and update state.")
    checkpoint_parser.add_argument("--analysis-dir", default=".analysis")
    checkpoint_parser.add_argument("--session-id")
    checkpoint_parser.add_argument("--mode", choices=["analyze", "refactor-guide", "overhaul"])
    checkpoint_parser.add_argument("--title", required=True)
    checkpoint_parser.add_argument("--summary", default="")
    checkpoint_parser.add_argument("--visited-add", nargs="*", default=[])
    checkpoint_parser.add_argument("--queue-add", nargs="*", default=[])
    checkpoint_parser.add_argument("--queue-done", nargs="*", default=[])
    checkpoint_parser.add_argument("--outputs", nargs="*", default=[])
    checkpoint_parser.add_argument("--next-actions", nargs="*", default=[])
    checkpoint_parser.add_argument(
        "--status",
        default="in_progress",
        choices=["in_progress", "paused", "completed"],
    )

    status_parser = subparsers.add_parser("status", help="Print session status.")
    status_parser.add_argument("--analysis-dir", default=".analysis")
    status_parser.add_argument("--session-id")
    status_parser.add_argument("--mode", choices=["analyze", "refactor-guide", "overhaul"])

    summary_parser = subparsers.add_parser("generate-summary", help="Generate SUMMARY.json for AI consumption.")
    summary_parser.add_argument("--analysis-dir", default=".analysis")
    summary_parser.add_argument("--session-id")
    summary_parser.add_argument("--mode", choices=["analyze", "refactor-guide", "overhaul"])

    search_index_parser = subparsers.add_parser("generate-search-index", help="Generate search index artifacts for MCP retrieval.")
    search_index_parser.add_argument("--analysis-dir", default=".analysis")
    search_index_parser.add_argument("--session-id")
    search_index_parser.add_argument("--mode", choices=["analyze", "refactor-guide", "overhaul"])

    publish_parser = subparsers.add_parser("publish", help="Copy session outputs to .analysis/outputs/ for git tracking.")
    publish_parser.add_argument("--analysis-dir", default=".analysis")
    publish_parser.add_argument("--session-id")
    publish_parser.add_argument("--mode", choices=["analyze", "refactor-guide", "overhaul"])

    migrate_parser = subparsers.add_parser("migrate", help="Migrate old layout: publish latest session outputs to .analysis/outputs/.")
    migrate_parser.add_argument("--analysis-dir", default=".analysis")

    # --- CLI search commands (replaces MCP server) ---
    search_parser = subparsers.add_parser("search", help="Search analysis outputs by keyword query.")
    search_parser.add_argument("query", help="Search query text.")
    search_parser.add_argument("--top-k", type=int, default=5)
    search_parser.add_argument("--kinds", nargs="*", help="Filter by chunk kind (e.g. section, issue, module).")
    search_parser.add_argument("--snippet-only", action="store_true", help="Return lightweight results with snippet instead of full text.")
    search_parser.add_argument("--snippet-len", type=int, default=240, help="Snippet length in characters (default: 240).")
    search_parser.add_argument("--analysis-dir", default=".analysis")
    search_parser.add_argument("--session-id")

    overview_parser = subparsers.add_parser("get-overview", help="Print published overview document.")
    overview_parser.add_argument("--analysis-dir", default=".analysis")

    get_module_parser = subparsers.add_parser("get-module", help="Print a specific module document.")
    get_module_parser.add_argument("name", help="Module name or file path.")
    get_module_parser.add_argument("--analysis-dir", default=".analysis")

    trace_parser = subparsers.add_parser("trace-deps", help="Trace dependency chain for a file.")
    trace_parser.add_argument("file", help="File path to trace.")
    trace_parser.add_argument("--depth", type=int, default=2)
    trace_parser.add_argument("--analysis-dir", default=".analysis")

    issues_parser = subparsers.add_parser("get-issues", help="List published issue candidates.")
    issues_parser.add_argument("--type", dest="issue_type", help="Filter by type: DUP, SEC, TIDY.")
    issues_parser.add_argument("--analysis-dir", default=".analysis")

    brief_parser = subparsers.add_parser("brief", help="Print compact project context (overview + modules + issues) in a single call.")
    brief_parser.add_argument("--analysis-dir", default=".analysis")

    return parser.parse_args(argv)


def cli(argv: list[str]) -> int:
    args = parse_args(argv)
    analysis_dir = Path(args.analysis_dir).resolve()

    if args.command == "init":
        result = init_session(
            analysis_dir=analysis_dir,
            mode=args.mode,
            scope=args.scope,
            session_id=args.session_id,
            resume_if_exists=not args.no_resume,
            commit_hash=args.commit,
            exclude_patterns=args.exclude or None,
        )
        print(f"session_id={result['session_id']}")
        print(f"session_dir={result['session_dir']}")
        print(f"resumed={str(result['resumed']).lower()}")
        print(f"commit_hash={result.get('commit_hash', '')}")
        return 0

    if args.command == "sync":
        resolved_session_id = resolve_session_id(analysis_dir, args.session_id, mode=getattr(args, "mode", None))
        result = sync_session(
            analysis_dir=analysis_dir,
            session_id=resolved_session_id,
            scope=args.scope,
        )
        print(f"session_id={result['session_id']}")
        print(f"status={result['status']}")
        print(f"commit_hash={result['commit_hash']}")
        print(f"changed_files={len(result['changed_files'])}")
        return 0

    if args.command == "checkpoint":
        resolved_session_id = resolve_session_id(analysis_dir, args.session_id, mode=args.mode)
        result = add_checkpoint(
            analysis_dir=analysis_dir,
            session_id=resolved_session_id,
            title=args.title,
            summary=args.summary,
            visited_add=args.visited_add,
            queue_add=args.queue_add,
            queue_done=args.queue_done,
            outputs=args.outputs,
            status=args.status,
            next_actions=args.next_actions,
        )
        print(f"session_id={result['session_id']}")
        print(f"checkpoint_no={result['checkpoint_no']:03d}")
        print(f"checkpoint_path={result['checkpoint_path']}")
        return 0

    if args.command == "status":
        resolved_session_id = resolve_session_id(analysis_dir, args.session_id, mode=args.mode)
        print(status_summary(analysis_dir, resolved_session_id), end="")
        return 0

    if args.command == "generate-summary":
        resolved_session_id = resolve_session_id(analysis_dir, args.session_id, mode=args.mode)
        summary = generate_summary(analysis_dir, resolved_session_id)
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 0

    if args.command == "generate-search-index":
        resolved_session_id = resolve_session_id(analysis_dir, args.session_id, mode=args.mode)
        result = generate_search_index_for_session(analysis_dir, resolved_session_id)
        print(f"session_id={resolved_session_id}")
        print(f"chunk_count={result['chunk_count']}")
        print(f"output_count={result['output_count']}")
        print(f"generated_at={result['generated_at']}")
        return 0

    if args.command == "publish":
        resolved_session_id = resolve_session_id(analysis_dir, args.session_id, mode=args.mode)
        result = publish_outputs(analysis_dir, resolved_session_id)
        print(f"session_id={result['session_id']}")
        print(f"target={result['target']}")
        print(f"published_files={len(result['published'])}")
        for f in result["published"]:
            print(f"  {f}")
        return 0

    if args.command == "migrate":
        result = migrate_layout(analysis_dir)
        if not result["migrated"]:
            print(f"nothing to migrate: {result['reason']}")
            return 0
        print(f"source_session={result['source_session']}")
        print(f"target={result['target']}")
        print(f"published_files={len(result['published'])}")
        for f in result["published"]:
            print(f"  {f}")
        print("\nAdd to .gitignore:  .analysis/sessions/")
        return 0

    # --- CLI search commands ---
    search_mod = None

    def _search():
        nonlocal search_mod
        if search_mod is None:
            search_mod = load_search_module()
        return search_mod

    if args.command == "search":
        results = _search().search_analysis(
            analysis_dir, query=args.query, top_k=args.top_k,
            kinds=args.kinds, session_id=getattr(args, "session_id", None),
            snippet_only=getattr(args, "snippet_only", False),
            snippet_len=getattr(args, "snippet_len", 240),
        )
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return 0

    if args.command == "get-overview":
        result = _search().get_overview(analysis_dir)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    if args.command == "get-module":
        result = _search().get_module(analysis_dir, args.name)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    if args.command == "trace-deps":
        result = _search().trace_dependencies(analysis_dir, args.file, depth=args.depth)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    if args.command == "get-issues":
        result = _search().get_issue_candidates(analysis_dir, issue_type=args.issue_type)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    if args.command == "brief":
        result = _search().get_brief(analysis_dir)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    return 1


def main() -> None:
    try:
        raise SystemExit(cli(sys.argv[1:]))
    except Exception as exc:  # pragma: no cover - top-level defensive handling
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
