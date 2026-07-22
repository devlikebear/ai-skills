---
name: register-analysis-context
description: "Register an existing .analysis/AI_CONTEXT.md in project instruction files after source analysis. Use only when the user explicitly asks to expose generated analysis to Codex, Claude Code, or other project agents."
disable-model-invocation: true
---

# Register Analysis Context

Use this skill only after explicit user invocation. It modifies project instruction files, so it is intentionally separate from source analysis.

## Language policy

- Detect the user's language from their request.
- Respond in Korean for Korean input and English for English input.

## Workflow

1. Confirm `.analysis/AI_CONTEXT.md` exists.
2. Inspect `git status --short --branch` and preserve unrelated changes.
3. Inspect `CLAUDE.md`, `AGENTS.md`, `codex.md`, and `.claude/CLAUDE.md` when present.
4. Append this block only when `## Codebase Analysis` is absent:

```markdown
## Codebase Analysis

Architecture and module analysis available at `.analysis/AI_CONTEXT.md`.
Read it first when you need to understand the project structure, dependencies, or key data flows.
```

If none of the supported files exist, create `CLAUDE.md` with only this block. Report updated, created, and already-registered files.

## Constraints

- Never run without explicit invocation.
- Keep changes idempotent and preserve existing guidance.
- Modify only supported instruction files.
- Do not edit `.analysis/` or application source.
