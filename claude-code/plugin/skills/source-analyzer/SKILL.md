---
name: source-analyzer
description: "Analyze existing source code and generate beginner-friendly architecture documents, actionable refactoring work orders, or system overhaul proposals without modifying source files. Use for codebase analysis, clone-coding guides, BFS architecture and data-flow summaries, refactor proposals, or overhaul proposals."
context: fork
agent: general-purpose
---

# Source Analyzer

Analyze `$ARGUMENTS` in an isolated context. Write only under `.analysis/`; instruction registration and GitHub Wiki publishing are separate explicit-only skills.

## References

- [source-analyzer-operations.md](../../references/source-analyzer-operations.md): layout, migration, checkpoints, resume, and search.
- [tutorial-template.md](../../references/tutorial-template.md): tutorials and clone coding.
- [refactor-template.md](../../references/refactor-template.md): refactor work orders.
- [tidy-first-rules.md](../../references/tidy-first-rules.md): TIDY classification.
- [security-triage-checklist.md](../../references/security-triage-checklist.md): security fallback checks.
- [overhaul-template.md](../../references/overhaul-template.md): overhaul proposals.

## Language policy

- Detect the user's language from their request.
- Respond in Korean for Korean input and English for English input.

## Required workflow

1. Choose `analyze`, `refactor-guide`, or `overhaul` mode.
2. Read [source-analyzer-operations.md](../../references/source-analyzer-operations.md) and set:

```bash
CHECKPOINT_SCRIPT="${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint_manager.py"
COMMIT=$(git rev-parse HEAD)
```

3. Run `brief` when prior analysis exists, then initialize or resume a session.
4. Enumerate committed files with `git ls-tree -r HEAD --name-only -- <scope>` and traverse first-party source with BFS.
5. Update session outputs and checkpoint after every bounded chunk.
6. On pause or completion, publish stable outputs inside `.analysis/outputs/`, generate the summary and search index, and update `.analysis/AI_CONTEXT.md`.
7. Do not register project instructions or publish externally. Those require explicit invocation of `register-analysis-context` or `publish-analysis-wiki`.

## Analyze mode

Produce newcomer-friendly `overview.md`, `architecture.md`, technology and glossary documents, tutorials, clone-coding guidance, module documents, and implementation checklists. Maintain `SUMMARY.json`, `dependency-graph.json`, `module-map.json`, and verified `issue-candidates.md` incrementally.

Issue candidates use `DUP`, `SEC`, or `TIDY` codes and include module, evidence, and suggested action.

## Refactor-guide mode

- Follow [refactor-template.md](../../references/refactor-template.md) exactly.
- Produce `DUP-*`, `SEC-*`, and `TIDY-*` work orders with evidence, completion criteria, and test criteria.
- Verify prior issue candidates against source and document false-positive removal.
- Write `.analysis/sessions/<session-id>/outputs/refactor-<scope>.md`.

## Overhaul mode

- Follow [overhaul-template.md](../../references/overhaul-template.md) exactly.
- Use `ARCH-*`, `DEAD-*`, `OVER-*`, and `DEBT-*` classifications.
- Document current state, target state, migration path, instructions, completion criteria, and tests for every work order.
- Remove unnecessary scope first, rebuild foundations second, and verify each phase.

## Post-analysis context

Write `.analysis/AI_CONTEXT.md` with session metadata, output pointers, module summaries, and known issues. Do not edit `AGENTS.md`, `CLAUDE.md`, `codex.md`, or `.claude/CLAUDE.md`.

## Search CLI

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

Prefer installed MCP resources such as `analysis://overview` and tools including `analysis.search`, `analysis.get_module`, `analysis.trace_dependencies`, and `analysis.get_issue_candidates`. Rebuild a stale cache with the checkpoint manager.

## Constraints

- Never modify analyzed source files or project instruction files.
- Update only `.analysis/` while running this skill.
- Analyze only committed files and ignore unstaged content.
- Exclude `.analysis/`, `.codex/`, `.claude/`, `.git/`, `vendor/`, `node_modules/`, `.venv/`, `__pycache__/`, `dist/`, and `build/` by default.
- Every checkpoint must record visited files, output files, summary text, or next actions.
