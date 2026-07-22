---
name: register-analysis-context
description: "Register an existing .analysis/AI_CONTEXT.md in project instruction files after source analysis. Use only when the user explicitly asks to expose generated analysis to Codex, Claude Code, or other project agents; this skill modifies instruction files and must not be selected implicitly."
---

# Register Analysis Context

Use this skill only after explicit user invocation. It connects an existing analysis artifact to project instructions without changing the analysis or source code.

## Language policy

- Respond in the same language the user writes in.
- If the user explicitly requests a language, follow it.

## Preflight

1. Confirm `.analysis/AI_CONTEXT.md` exists and is readable.
2. Run `git status --short --branch` and preserve unrelated changes.
3. Inspect these instruction files when present:
   - `AGENTS.md`
   - `CLAUDE.md`
   - `codex.md`
   - `.claude/CLAUDE.md`
4. Never replace an existing instruction file or rewrite unrelated guidance.

## Registration workflow

Append the following block to each existing instruction file only when it has no `## Codebase Analysis` section:

```markdown
## Codebase Analysis

Architecture and module analysis available at `.analysis/AI_CONTEXT.md`.
Read it first when you need to understand the project structure, dependencies, or key data flows.
```

If none of the supported instruction files exist, create `AGENTS.md` containing only the block. Report every file created or updated and every file skipped because it was already registered.

## Constraints

- Require explicit invocation; never infer permission from a source-analysis request.
- Modify only supported instruction files.
- Keep the operation idempotent.
- Do not edit `.analysis/`, application source, or unrelated project documentation.
