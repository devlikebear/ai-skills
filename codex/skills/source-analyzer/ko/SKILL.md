---
name: source-analyzer
description: "Analyze existing source code and generate beginner-friendly architecture documents or actionable refactoring work orders without modifying source files. Use this Korean-default variant when users ask for codebase analysis, clone-coding guides, BFS-style architecture/data-flow summaries, or refactor proposals with DUP/SEC/TIDY issue codes."
---

# Source Analyzer Wrapper

This is the Korean-default variant of `source-analyzer`.

## Load only what you need

- `shared/references/tutorial-template.md`: tutorial and clone-coding structure.
- `shared/references/refactor-template.md`: refactor work-order structure.
- `shared/references/tidy-first-rules.md`: TIDY rule mapping.
- `shared/references/security-triage-checklist.md`: security fallback checks.
- `shared/references/checkpoint-template.md`: manual checkpoint fallback.
- `shared/scripts/checkpoint_manager.py`: resumable checkpoint session manager.

## Language policy

- Write responses and generated outputs in Korean by default.
- If the user explicitly requests another language policy, follow it.

## Required workflow

1. Decide the mode: `analyze` or `refactor-guide`.
2. Start or resume a session before reading many files.
3. Traverse first-party source with BFS in small chunks.
4. Update `.analysis/sessions/<session-id>/outputs/` after each chunk.
5. Write a checkpoint after each chunk.
6. Pause safely with status `paused` when handing off.

Use the shared checkpoint script:

```bash
CHECKPOINT_SCRIPT="${CODEX_HOME:-$HOME/.codex}/skills/source-analyzer/shared/scripts/checkpoint_manager.py"
python3 "$CHECKPOINT_SCRIPT" init --mode analyze --scope "src/main.ts"
python3 "$CHECKPOINT_SCRIPT" checkpoint --title "service layer analyzed" --status in_progress
```

## Analyze mode

- Goal: produce newcomer-friendly architecture and clone-coding material.
- Outputs:
  - `.analysis/sessions/<session-id>/outputs/overview.md`
  - `.analysis/sessions/<session-id>/outputs/architecture.md`
  - `.analysis/sessions/<session-id>/outputs/technologies.md`
  - `.analysis/sessions/<session-id>/outputs/modules/<name>.md`
  - `.analysis/sessions/<session-id>/outputs/glossary.md`
  - `.analysis/sessions/<session-id>/outputs/tutorial.md`
  - `.analysis/sessions/<session-id>/outputs/clone-coding.md`
  - `.analysis/sessions/<session-id>/outputs/implementation-checklist.md`
- Use real file paths, short paragraphs, and plain Korean.

## Refactor-guide mode

- Goal: produce actionable work orders with `DUP-*`, `SEC-*`, and `TIDY-*` codes.
- Follow `shared/references/refactor-template.md` exactly.
- For each issue include evidence, completion criteria, and test criteria.
- Check security references first, then fall back to `shared/references/security-triage-checklist.md`.

## Resume protocol

1. Open `.analysis/RESUME.md`.
2. Open the referenced `index.md`, latest checkpoint, and `state.json`.
3. Continue from `frontier` and pending `next actions`.
4. Write the next checkpoint before ending.

## Constraints

- Never modify analyzed source files.
- Update only `.analysis/` outputs while running this skill.
- Prefer `rg --files`, `rg`, `sed -n`, `head`, `tail`, `cat`, `find`, and `ls` for inspection.
