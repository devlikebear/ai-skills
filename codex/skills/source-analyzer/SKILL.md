---
name: source-analyzer
description: "Analyze existing source code and generate beginner-friendly architecture documents, actionable refactoring work orders, or system overhaul proposals without modifying source files. Use for codebase analysis, clone-coding guides, BFS architecture and data-flow summaries, refactor proposals with DUP/SEC/TIDY codes, or overhaul proposals with ARCH/DEAD/OVER/DEBT codes."
---

# Source Analyzer

Analyze committed source and write only under `.analysis/`. Project instruction registration and GitHub Wiki publishing are separate, explicit-only skills.

## Load only what you need

- `shared/references/operations.md`: layout, migration, checkpoint, resume, and search operations.
- `shared/references/tutorial-template.md`: tutorial and clone-coding outputs.
- `shared/references/refactor-template.md`: refactor work orders.
- `shared/references/tidy-first-rules.md`: TIDY classification.
- `shared/references/security-triage-checklist.md`: security fallback checks.
- `shared/references/overhaul-template.md`: overhaul proposals.
- `shared/references/checkpoint-template.md`: manual checkpoint fallback.

## Language policy

- Respond in the same language the user writes in.
- If the user explicitly requests a language, follow it.

## Required workflow

1. Choose `analyze`, `refactor-guide`, or `overhaul` mode.
2. Read `shared/references/operations.md` and set:

```bash
CHECKPOINT_SCRIPT="${CODEX_HOME:-$HOME/.codex}/skills/source-analyzer/shared/scripts/checkpoint_manager.py"
COMMIT=$(git rev-parse HEAD)
```

3. Run `brief` when prior analysis exists, then initialize or resume a checkpoint session.
4. Enumerate committed files with `git ls-tree -r HEAD --name-only -- <scope>` and traverse first-party source with BFS.
5. Update session outputs and checkpoint after each bounded chunk.
6. On pause or completion, publish stable outputs inside `.analysis/outputs/`, generate the summary and search index, and update `.analysis/AI_CONTEXT.md`.
7. Do not register the context in project instructions and do not publish it externally. Those actions require explicit invocation of `register-analysis-context` or `publish-analysis-wiki`.

## Analyze mode

Produce newcomer-friendly architecture and clone-coding material:

- `overview.md`, `architecture.md`, `technologies.md`, `glossary.md`
- `tutorial.md`, `clone-coding.md`, `implementation-checklist.md`
- `modules/<name>.md`, `issue-candidates.md`
- `SUMMARY.json`, `dependency-graph.json`, `module-map.json`

Record relative source paths and plain-language responsibilities. Update structured JSON incrementally after each module chunk. Generate `SUMMARY.json` through the checkpoint manager at pause and completion.

### Analyze-to-refactor bridge

Write issue candidates in this form:

```markdown
### <CODE>-<NNN>: <short title>

- Module: `<module path>`
- Type: `DUP` | `SEC` | `TIDY`
- Evidence: <verified observation>
- Suggested action: <brief action>
```

## Refactor-guide mode

- Follow `shared/references/refactor-template.md` exactly.
- Produce actionable work orders with `DUP-*`, `SEC-*`, and `TIDY-*` codes.
- Include evidence, completion criteria, and test criteria.
- Start from verified `issue-candidates.md` when available; remove false positives with a reason.
- Write `.analysis/sessions/<session-id>/outputs/refactor-<scope>.md`.

## Overhaul mode

- Follow `shared/references/overhaul-template.md` exactly.
- Classify architecture flaws as `ARCH-*`, unnecessary code as `DEAD-*`, over-engineering as `OVER-*`, and accumulated debt as `DEBT-*`.
- Each work order must include current state, target state, migration path, instructions, completion criteria, and test criteria.
- Remove unnecessary scope first, rebuild foundations second, and verify each phase.
- Write `.analysis/sessions/<session-id>/outputs/overhaul-<scope>.md`.

## Post-analysis context

After publishing the session inside `.analysis/`, write `.analysis/AI_CONTEXT.md` with the session, commit, status, output pointers, module summary, and known issues. This file is an analysis output; do not modify `AGENTS.md`, `CLAUDE.md`, `codex.md`, or `.claude/CLAUDE.md`.

## Search CLI

Use CLI search instead of opening large analysis files. Commands output JSON.

```bash
python3 "$CHECKPOINT_SCRIPT" brief
python3 "$CHECKPOINT_SCRIPT" search "query text" --top-k 5
python3 "$CHECKPOINT_SCRIPT" search "auth middleware" --top-k 3 --snippet-only --snippet-len 600
python3 "$CHECKPOINT_SCRIPT" get-module server-chat-pipeline
python3 "$CHECKPOINT_SCRIPT" get-overview
python3 "$CHECKPOINT_SCRIPT" trace-deps internal/llm/router.go --depth 3
python3 "$CHECKPOINT_SCRIPT" get-issues --type SEC
python3 "$CHECKPOINT_SCRIPT" generate-search-index
```

Prefer `brief` plus snippet search. Use full documents only when snippets are insufficient.

## Search MCP integration

When the `source-analyzer-search` MCP server is available, prefer its resources and tools:

- Resources: `analysis://overview`, `analysis://architecture`, `analysis://module-map`, `analysis://modules/<name>`
- Tools: `analysis.search`, `analysis.get_module`, `analysis.trace_dependencies`, `analysis.get_issue_candidates`

Refresh missing or stale cache data with `python3 "$CHECKPOINT_SCRIPT" generate-search-index`.

## Constraints

- Never modify analyzed source files or project instruction files.
- Update only `.analysis/` outputs and `.analysis/cache/` while running this skill.
- Analyze only committed files and ignore unstaged content.
- Exclude `.analysis/`, `.codex/`, `.claude/`, `.git/`, `vendor/`, `node_modules/`, `.venv/`, `__pycache__/`, `dist/`, and `build/` by default.
- Every checkpoint must record visited files, output files, summary text, or next actions.
- Prefer `rg --files`, `rg`, `sed -n`, `head`, `tail`, `cat`, `find`, and `ls` for inspection.
