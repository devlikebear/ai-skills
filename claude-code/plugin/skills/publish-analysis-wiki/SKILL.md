---
name: publish-analysis-wiki
description: "Preview and publish reviewed .analysis outputs to a repository's GitHub Wiki. Use only when the user explicitly asks to publish analysis documentation or invokes this skill by name."
disable-model-invocation: true
---

# Publish Analysis Wiki

Use this skill only after explicit user invocation. Publishing changes external GitHub state and is intentionally separate from source analysis.

## Language policy

- Detect the user's language from their request.
- Respond in Korean for Korean input and English for English input.

## Workflow

1. Confirm the intended repository and inspect `git status --short --branch`.
2. Confirm `.analysis/outputs/` contains reviewed Markdown output.
3. Confirm the GitHub Wiki is enabled and already has at least one page.
4. Run a local preview and inspect its `Home.md`, `_Sidebar.md`, document pages, and module pages:

```bash
PUBLISH_SCRIPT="${CLAUDE_PLUGIN_ROOT}/scripts/publish_wiki.sh"
bash "$PUBLISH_SCRIPT" --dry-run
```

5. Stop after preview when the user asked for dry-run only. For an explicit publish request, run `bash "$PUBLISH_SCRIPT"` after confirming the remote target.
6. Pass `--session-id <id>` or `--project-dir <path>` when the user chose a non-default source.

## Constraints

- Never run without explicit invocation.
- Never publish without inspecting a dry-run first.
- Stop when outputs are unreviewed or the Wiki remote is ambiguous.
- Do not modify application source.
