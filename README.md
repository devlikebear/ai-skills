# AI Skills Repository

Public repository for reusable AI-agent skills, supporting both Codex and Claude Code.

Current release: `0.10.2`

## Overview

- Supports both Codex runtime skills and a Claude Code plugin marketplace.
- Codex skills use a flat runtime layout: one `SKILL.md`, one `agents/openai.yaml`, and optional `shared/`.
- Claude Code skills are distributed through the `code-workflow` plugin with bilingual `SKILL.md` files and shared `references/`.
- `source-analyzer` produces resumable `.analysis/` outputs and now ships a wiki publisher alongside its checkpoint manager.
- `source-analyzer` also ships a local search MCP server for querying analysis outputs and checkpoints.
- A local authoring wrapper lives at `.codex/skills/skill-generator`.
- Public Codex skill roots:
  - `codex/skills/source-analyzer`
  - `codex/skills/implement`
  - `codex/skills/plan-for-codex`
  - `codex/skills/refactor`
  - `codex/skills/review`
  - `codex/skills/github-flow`

## Repository Layout

```text
codex/
  skills/
    source-analyzer/
      SKILL.md
      agents/
      shared/
    implement/
      SKILL.md
      agents/
      shared/
    plan-for-codex/
      SKILL.md
      agents/
      shared/
    refactor/
      SKILL.md
      agents/
      shared/
    review/
      SKILL.md
      agents/
      shared/
    github-flow/
      SKILL.md
      agents/
      shared/
claude-code/
  plugin/
    .claude-plugin/
      plugin.json
    .mcp.json
    skills/
      source-analyzer/
      implement/
      plan/
      refactor/
      review/
      github-flow/
    references/
    scripts/
.agents/
  plugins/
    marketplace.json
.claude-plugin/
  marketplace.json
plugins/
  source-analyzer-tools/
    .codex-plugin/
      plugin.json
    .mcp.json
    servers/
servers/
  source-analyzer-mcp/
.codex/
  skills/
    skill-generator/
      SKILL.md
      agents/
scripts/
  install_codex_skill.sh
  sync_source_analyzer_mcp.sh
  publish_wiki.sh
tests/
```

`codex/skills/<skill-name>` stores the Codex source layout with flat runtime files only.
`claude-code/plugin/` is the Claude Code plugin distribution with shared references and shared scripts.

## Included Skills

### `source-analyzer`

- Analyzes an existing codebase without modifying source files.
- Produces resumable outputs under `.analysis/sessions/` and published outputs under `.analysis/outputs/`.
- Supports `analyze`, `refactor-guide`, and `overhaul` modes.
- Ships `checkpoint_manager.py` and `publish_wiki.sh` in both Codex and Claude Code distributions.
- Can build a local search cache under `.analysis/cache/source-analyzer-search/`.
- Ships a local MCP server that exposes search, module lookup, dependency tracing, and checkpoint/session queries.

### `implement`

- Executes an approved work order directly.
- Keeps the scope small, explicit, and verification-driven.

### `plan-for-codex`

- Splits a request into executable work orders for Codex.
- Keeps tasks bounded, verifiable, and ready for `/implement`.

### `refactor`

- Performs safe, behavior-preserving refactoring.
- Uses shared checklists and refactoring patterns.

### `review`

- Performs diff-based review focused on regressions, security issues, and missing tests.
- Produces a fix work order when changes are required.

### `github-flow`

- Guides through the full GitHub Flow lifecycle: branch → develop → PR → merge → release.
- Phase 2 integrates `plan` → `implement` → `review` as an inner loop before each commit.
- Available for both Codex (`/github-flow`) and Claude Code (`/code-workflow:github-flow`).

### `skill-generator`

- Lives under `.codex/skills/skill-generator`.
- Wraps the upstream `skill-creator` workflow for this repository.
- Enforces the flat `SKILL.md` + `agents/openai.yaml` + optional `shared/` convention used by public Codex skills.

## Install for Codex

Clone this repository, then install one or more skills into your local Codex home.

```bash
scripts/install_codex_skill.sh --list
scripts/install_codex_skill.sh source-analyzer
scripts/install_codex_skill.sh source-analyzer --with-mcp
scripts/install_codex_skill.sh implement
scripts/install_codex_skill.sh --all
```

By default the installer copies skills into `${CODEX_HOME:-$HOME/.codex}/skills`.
Each skill is a single `SKILL.md` that responds in the user's language automatically.
For `source-analyzer`, `--with-mcp` also registers `source-analyzer-search` via `codex mcp add ...`.

### Codex quickstart for `source-analyzer-search`

```bash
scripts/install_codex_skill.sh source-analyzer --with-mcp
codex mcp list
python3 ~/.codex/skills/source-analyzer/shared/scripts/checkpoint_manager.py generate-search-index
```

After registration, Codex should list `source-analyzer-search` in `codex mcp list`.
Once `.analysis/outputs/` and `.analysis/cache/source-analyzer-search/` exist, the agent can call:

- `analysis.search` for natural-language retrieval across overview, architecture, module docs, issues, and checkpoints
- `analysis.get_module` for a direct module doc or module-map lookup
- `analysis.trace_dependencies` for dependency expansion from a file path

The repo also includes a Codex plugin bundle artifact:

- `.agents/plugins/marketplace.json`
- `plugins/source-analyzer-tools/`

Canonical MCP sources live under `servers/source-analyzer-mcp/`.
Use `scripts/sync_source_analyzer_mcp.sh` when bundle copies need to be refreshed.

## Install via Plugin Marketplace (Claude Code)

This repository is also a Claude Code plugin marketplace. Add it directly and install the `code-workflow` plugin:

```bash
# Add this repo as a marketplace
/plugin marketplace add devlikebear/ai-skills

# Install the plugin
/plugin install code-workflow@ai-skills
```

After installation the following skills are available:

- `/code-workflow:plan`
- `/code-workflow:implement`
- `/code-workflow:review`
- `/code-workflow:refactor`
- `/code-workflow:source-analyzer`
- `/code-workflow:github-flow`

Plugin skills are bilingual and detect the user's language automatically.
The plugin now also bundles `source-analyzer-search` through `claude-code/plugin/.mcp.json`.

### Claude Code quickstart for `source-analyzer-search`

1. Run `/code-workflow:source-analyzer` and let it publish `.analysis/outputs/`.
2. Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint_manager.py" generate-search-index` inside the analyzed project.
3. Ask Claude Code to use `analysis.search`, `analysis.get_module`, or `analysis.trace_dependencies` against that project.

## Build Search Cache

`source-analyzer` now auto-generates the search cache when outputs are published on `paused` or `completed` checkpoints.
If you already finished analysis earlier, you can still generate or rebuild the index manually:

```bash
python3 codex/skills/source-analyzer/shared/scripts/checkpoint_manager.py generate-search-index
```

If the cache is missing, the MCP server can still fall back to direct scanning of `.analysis/outputs/`.

Example retrieval prompts once the MCP server is available:

- `Use analysis.search to find the auth token validation flow.`
- `Use analysis.get_module for auth and summarize the responsibilities.`
- `Use analysis.trace_dependencies for src/auth.py with depth 2.`

## Publish Analysis to GitHub Wiki

For this repository itself, use the root helper:

```bash
scripts/publish_wiki.sh --session-id analyze-20260308-120027
scripts/publish_wiki.sh --dry-run
```

When `source-analyzer` is installed as a runtime skill, the distributed wiki publishers live at:

- `codex/skills/source-analyzer/shared/scripts/publish_wiki.sh`
- `claude-code/plugin/scripts/publish_wiki.sh`

Those distributed scripts support `--project-dir <path>` so they can publish analysis outputs from another checked-out project.

## Skill Root Convention

### Codex skills

```text
<skill-name>/
  SKILL.md
  agents/
    openai.yaml
  shared/
    scripts/
    references/
```

### Claude Code plugin skills

```text
<skill-name>/
  SKILL.md
```

Shared references live in `claude-code/plugin/references/` and are referenced by all plugin skills.

Use `.codex/skills/skill-generator` when you want to generate a new Codex skill that follows the repository convention.

## Notes

- Codex discovers runtime skills from `~/.codex/skills`.
- Codex MCP servers can be registered directly with `codex mcp add ...`.
- Claude Code installs skills via plugin marketplace.
- `.analysis/outputs/` contains publishable, git-trackable analysis outputs.
- `.analysis/cache/source-analyzer-search/` contains local search indexes for MCP retrieval.
- Release history is tracked in `CHANGELOG.md`.
- Licensing is provided in `LICENSE`.
