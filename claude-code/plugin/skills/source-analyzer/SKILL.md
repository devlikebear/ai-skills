---
name: source-analyzer
description: "Analyze existing source code and generate beginner-friendly architecture documents or actionable refactoring work orders without modifying source files. Use when users ask for codebase analysis, clone-coding guides, BFS-style architecture/data-flow summaries, or refactor proposals with DUP/SEC/TIDY issue codes."
---

# Source Analyzer

## References

- [tutorial-template.md](../../references/tutorial-template.md): tutorial and clone-coding structure.
- [refactor-template.md](../../references/refactor-template.md): refactor work-order structure.
- [tidy-first-rules.md](../../references/tidy-first-rules.md): TIDY rule mapping.
- [security-triage-checklist.md](../../references/security-triage-checklist.md): security fallback checks.
- [checkpoint-template.md](../../references/checkpoint-template.md): manual checkpoint fallback.

Checkpoint session manager script:

```bash
CHECKPOINT_SCRIPT="${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint_manager.py"
python3 "$CHECKPOINT_SCRIPT" init --mode analyze --scope "src/main.ts"
python3 "$CHECKPOINT_SCRIPT" checkpoint --title "service layer analyzed" --status in_progress
```

## Language policy

- Detect the user's language from their message and respond in the same language.
- If the user explicitly requests a language, follow it.

## Required workflow

1. Decide the mode: `analyze` or `refactor-guide`.
2. Start or resume a session before reading many files.
3. Traverse first-party source with BFS in small chunks.
4. Update `.analysis/sessions/<session-id>/outputs/` after each chunk.
5. Write a checkpoint after each chunk.
6. Pause safely with status `paused` when handing off.

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
- Use real file paths and short paragraphs.

## Refactor-guide mode

- Goal: produce actionable work orders with `DUP-*`, `SEC-*`, and `TIDY-*` codes.
- Follow [refactor-template.md](../../references/refactor-template.md) exactly.
- For each issue include evidence, completion criteria, and test criteria.
- Check security references first, then fall back to [security-triage-checklist.md](../../references/security-triage-checklist.md).

## Resume protocol

1. Open `.analysis/RESUME.md`.
2. Open the referenced `index.md`, latest checkpoint, and `state.json`.
3. Continue from `frontier` and pending `next actions`.
4. Write the next checkpoint before ending.

## Constraints

- Never modify analyzed source files.
- Update only `.analysis/` outputs while running this skill.
