#!/usr/bin/env python3
"""Checkpoint manager for resumable source-analyzer runs."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_FILENAME = "state.json"
INDEX_FILENAME = "index.md"
RESUME_FILENAME = "RESUME.md"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def now_for_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def ensure_layout(analysis_dir: Path) -> None:
    (analysis_dir / "sessions").mkdir(parents=True, exist_ok=True)


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
    resume_path.write_text(
        (
            "# Source Analyzer Resume Pointer\n\n"
            f"- Session: `{session_id}`\n"
            f"- Mode: `{state.get('mode', '')}`\n"
            f"- Scope: `{state.get('scope', '')}`\n"
            f"- State: `{state.get('status', '')}`\n"
            f"- Next Checkpoint Number: `{state.get('next_checkpoint', 1):03d}`\n"
            f"- Last Checkpoint File: `{checkpoint_ref}`\n"
            f"- Updated At (UTC): `{state.get('updated_at', '')}`\n\n"
            "Resume steps:\n"
            "1. Open this session's `index.md`.\n"
            "2. Open `state.json` and continue from `frontier`.\n"
            "3. Write the next `checkpoints/checkpoint-XXX.md`.\n"
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
) -> dict[str, Any]:
    ensure_layout(analysis_dir)

    if session_id is None and resume_if_exists:
        existing = find_latest_resumable_session(analysis_dir, mode=mode)
        if existing:
            write_resume_file(analysis_dir, existing)
            return {
                "session_id": existing,
                "session_dir": session_path(analysis_dir, existing),
                "resumed": True,
            }

    final_session_id = session_id or generate_session_id(mode)
    session_dir = session_path(analysis_dir, final_session_id)
    if session_dir.exists():
        raise FileExistsError(f"session already exists: {session_dir}")

    (session_dir / "checkpoints").mkdir(parents=True, exist_ok=False)
    (session_dir / "outputs").mkdir(parents=True, exist_ok=False)

    now = now_iso()
    state: dict[str, Any] = {
        "version": 1,
        "session_id": final_session_id,
        "mode": mode,
        "scope": scope,
        "status": "in_progress",
        "created_at": now,
        "updated_at": now,
        "next_checkpoint": 1,
        "visited": [],
        "frontier": [],
        "outputs": [],
        "checkpoints": [],
    }

    save_state(analysis_dir, final_session_id, state)
    (session_dir / INDEX_FILENAME).write_text(
        initialize_index_markdown(final_session_id, mode, scope),
        encoding="utf-8",
    )
    write_resume_file(analysis_dir, final_session_id)
    return {"session_id": final_session_id, "session_dir": session_dir, "resumed": False}


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

    visited = dedupe_keep_order(list(state.get("visited", [])) + visited_add)

    done_set = {entry.strip() for entry in queue_done if entry.strip()}
    frontier = [entry for entry in list(state.get("frontier", [])) if entry not in done_set]
    frontier = dedupe_keep_order(frontier + queue_add)

    output_files = dedupe_keep_order(list(state.get("outputs", [])) + outputs)

    checkpoint_no = int(state.get("next_checkpoint", 1))
    checkpoint_filename = f"checkpoint-{checkpoint_no:03d}.md"
    checkpoint_path = session_path(analysis_dir, session_id) / "checkpoints" / checkpoint_filename
    now = now_iso()

    checkpoint_md = (
        f"# Checkpoint {checkpoint_no:03d}: {title}\n\n"
        f"> Session: `{session_id}`\n"
        f"> Mode: `{state.get('mode', '')}`\n"
        f"> Scope: `{state.get('scope', '')}`\n"
        f"> Status: `{status}`\n"
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

    return {
        "session_id": session_id,
        "checkpoint_no": checkpoint_no,
        "checkpoint_path": checkpoint_path,
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
    return (
        f"session_id={session_id}\n"
        f"mode={state.get('mode', '')}\n"
        f"scope={state.get('scope', '')}\n"
        f"status={state.get('status', '')}\n"
        f"next_checkpoint={int(state.get('next_checkpoint', 1)):03d}\n"
        f"visited={len(state.get('visited', []))}\n"
        f"frontier={len(state.get('frontier', []))}\n"
        f"latest_checkpoint={latest_cp}\n"
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage source-analyzer incremental checkpoints.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create or resume a session.")
    init_parser.add_argument("--analysis-dir", default=".analysis")
    init_parser.add_argument("--mode", required=True, choices=["analyze", "refactor-guide"])
    init_parser.add_argument("--scope", required=True)
    init_parser.add_argument("--session-id")
    init_parser.add_argument("--no-resume", action="store_true")

    checkpoint_parser = subparsers.add_parser("checkpoint", help="Write a checkpoint markdown and update state.")
    checkpoint_parser.add_argument("--analysis-dir", default=".analysis")
    checkpoint_parser.add_argument("--session-id")
    checkpoint_parser.add_argument("--mode", choices=["analyze", "refactor-guide"])
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
    status_parser.add_argument("--mode", choices=["analyze", "refactor-guide"])

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
        )
        print(f"session_id={result['session_id']}")
        print(f"session_dir={result['session_dir']}")
        print(f"resumed={str(result['resumed']).lower()}")
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

    return 1


def main() -> None:
    try:
        raise SystemExit(cli(sys.argv[1:]))
    except Exception as exc:  # pragma: no cover - top-level defensive handling
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
