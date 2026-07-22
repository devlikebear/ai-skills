---
name: publish-analysis-wiki
description: "Preview and publish reviewed .analysis outputs to a repository's GitHub Wiki. Use only when the user explicitly asks to publish analysis documentation or requests this skill by name; publishing pushes external state and must never be selected implicitly."
---

# Publish Analysis Wiki

Use this skill only after explicit user invocation. Always prepare and inspect a local preview before pushing Wiki content.

## Language policy

- Respond in the same language the user writes in.
- If the user explicitly requests a language, follow it.

## Preconditions

1. Confirm the current directory is the intended Git repository.
2. Confirm `.analysis/outputs/` exists and contains reviewed Markdown output.
3. Run `git status --short --branch`; publishing must not modify or discard project changes.
4. Confirm the GitHub Wiki is enabled and already has at least one page.

## Workflow

```bash
PUBLISH_SCRIPT="${PLUGIN_ROOT}/skills/publish-analysis-wiki/shared/scripts/publish_wiki.sh"
bash "$PUBLISH_SCRIPT" --dry-run
```

Inspect the generated `Home.md`, `_Sidebar.md`, document pages, and module pages. If the user requested preview only, stop and report the preview location.

For an explicit publish request, run:

```bash
bash "$PUBLISH_SCRIPT"
```

To select a specific analysis session or repository root, pass `--session-id <id>` or `--project-dir <path>`. Report the target Wiki remote and pushed commit after success.

## Constraints

- Require explicit invocation; never infer permission from analysis completion.
- Always run and inspect `--dry-run` before publishing.
- Do not publish when outputs are missing, unreviewed, or the remote target is ambiguous.
- Do not modify application source files.
