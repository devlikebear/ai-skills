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
COMMIT=$(git rev-parse HEAD)
python3 "$CHECKPOINT_SCRIPT" init --mode analyze --scope "src/main.ts" --commit "$COMMIT"
# 재개 시: 최신 HEAD와 동기화
python3 "$CHECKPOINT_SCRIPT" sync
python3 "$CHECKPOINT_SCRIPT" checkpoint --title "service layer analyzed" --status in_progress
```

## Language policy

- Detect the user's language from their message and respond in the same language.
- If the user explicitly requests a language, follow it.

## Required workflow

1. Decide the mode: `analyze` or `refactor-guide`.
2. Capture the current commit: `COMMIT=$(git rev-parse HEAD)`.
3. Start or resume a session: pass `--commit "$COMMIT"` to init.
4. If resuming, run `sync` to detect new commits and update the frontier.
5. Use `git ls-tree -r HEAD --name-only -- <scope>` to enumerate files (committed files only).
6. Traverse first-party source with BFS in small chunks.
7. Update `.analysis/sessions/<session-id>/outputs/` after each chunk.
8. Write a checkpoint after each chunk.
9. Pause safely with status `paused` when handing off.

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
3. Run `sync` to detect new commits.
   - `status=synced`: changed files added to frontier for re-analysis.
   - `status=unchanged`: continue BFS from existing frontier.
4. Continue from `frontier` and pending `next actions`.
5. Write the next checkpoint before ending.

## Constraints

- Never modify analyzed source files.
- Update only `.analysis/` outputs while running this skill.
- Only analyze files committed to git (`git ls-tree -r HEAD --name-only`). Ignore uncommitted/unstaged changes.
