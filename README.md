# AI Skills Repository

Public repository for reusable AI-agent skills, supporting both Codex and Claude Code.

Current release: `0.11.0`

## Overview

- Supports both Codex runtime skills and a Claude Code plugin marketplace.
- Codex skills use a flat runtime layout: one `SKILL.md`, one `agents/openai.yaml`, and optional `shared/`.
- Claude Code skills are distributed through the `code-workflow` plugin with bilingual `SKILL.md` files and shared `references/`.
- `source-analyzer` produces resumable `.analysis/` outputs and ships a wiki publisher alongside its checkpoint manager.
- `source-analyzer` provides built-in CLI search commands for querying analysis outputs and checkpoints.
- A local MCP server is also available for agents that support MCP-based tool discovery.
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
    source-analyzer/       # BFS codebase analysis (3 modes)
    implement/             # Work order execution
    plan-for-codex/        # Request → work orders
    refactor/              # Behavior-preserving refactoring
    review/                # Diff-based code review
    github-flow/           # Full GitHub Flow lifecycle
claude-code/
  plugin/
    .claude-plugin/
      plugin.json          # code-workflow plugin manifest
    .mcp.json              # MCP server config (optional)
    skills/                # 6 Claude Code skills
    references/            # 14 shared reference templates
    scripts/               # checkpoint_manager.py (canonical), search, wiki
    servers/               # MCP server bundle (synced copy)
.agents/
  plugins/
    marketplace.json       # Codex local marketplace
.claude-plugin/
  marketplace.json         # Claude Code marketplace
plugins/
  source-analyzer-tools/   # Codex MCP plugin bundle
servers/
  source-analyzer-mcp/     # Canonical MCP server sources
.codex/
  skills/
    skill-generator/       # Skill authoring wrapper
scripts/
  install_codex_skill.sh   # Codex skill installer
  sync_source_analyzer_mcp.sh  # Sync canonical sources to all bundles
tests/                     # 6 test suites
```

`codex/skills/<skill-name>` stores the Codex source layout with flat runtime files only.
`claude-code/plugin/` is the Claude Code plugin distribution with shared references and shared scripts.

## Included Skills

### `source-analyzer`

- Analyzes an existing codebase without modifying source files.
- Produces resumable outputs under `.analysis/sessions/` and published outputs under `.analysis/outputs/`.
- Supports `analyze`, `refactor-guide`, and `overhaul` modes.
- Ships `checkpoint_manager.py` and `publish_wiki.sh` in both Codex and Claude Code distributions.
- Provides CLI search commands: `search`, `get-overview`, `get-module`, `trace-deps`, `get-issues`.
- Also ships a local MCP server under `servers/source-analyzer-mcp/` for MCP-capable agents.

### `implement`

- Executes an approved work order directly.
- Keeps the scope small, explicit, and verification-driven.

### `plan-for-codex`

- Splits a request into executable work orders for Codex.
- Keeps tasks bounded, verifiable, and ready for `/implement`.

### `refactor`

- Performs safe, behavior-preserving refactoring.
- Integrates with `source-analyzer` via `issue-candidates.md` for analysis-driven refactoring.
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
The plugin also bundles `source-analyzer-search` through `claude-code/plugin/.mcp.json`.

### Claude Code quickstart for `source-analyzer-search`

1. Run `/code-workflow:source-analyzer` and let it publish `.analysis/outputs/`.
2. The search index is generated automatically on publish. To rebuild manually:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint_manager.py" generate-search-index
   ```
3. Use the built-in CLI search commands or the MCP tools to query the analysis.

## CLI Search Commands

`checkpoint_manager.py` provides CLI subcommands for querying analysis outputs without requiring an MCP server:

```bash
CHECKPOINT_SCRIPT="path/to/checkpoint_manager.py"

# Keyword search across all analysis outputs
python3 "$CHECKPOINT_SCRIPT" search "auth middleware" --top-k 5

# Get the published overview document
python3 "$CHECKPOINT_SCRIPT" get-overview

# Get a specific module document by name
python3 "$CHECKPOINT_SCRIPT" get-module auth

# Trace dependency chain for a file
python3 "$CHECKPOINT_SCRIPT" trace-deps src/auth.py --depth 3

# List issue candidates (optionally filter by type)
python3 "$CHECKPOINT_SCRIPT" get-issues --type SEC
```

## Build Search Cache

`source-analyzer` auto-generates the search cache when outputs are published on `paused` or `completed` checkpoints.
If you already finished analysis earlier, you can still generate or rebuild the index manually:

```bash
python3 codex/skills/source-analyzer/shared/scripts/checkpoint_manager.py generate-search-index
```

If the cache is missing, the MCP server can still fall back to direct scanning of `.analysis/outputs/`.

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

## Dual-Distribution Sync

Shared scripts must stay identical across distributions. The canonical sources and their sync targets:

| Canonical Source | Sync Targets |
|-----------------|--------------|
| `claude-code/plugin/scripts/checkpoint_manager.py` | `codex/.../shared/scripts/checkpoint_manager.py` |
| `servers/source-analyzer-mcp/source_analyzer_search.py` | 5 locations (see sync script) |
| `servers/source-analyzer-mcp/server.py` | 3 locations (see sync script) |

Run the sync script after modifying any canonical source:

```bash
scripts/sync_source_analyzer_mcp.sh
```

Contract tests in `tests/test_skill_repository_contract.py` verify all copies stay in sync.

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
- `.analysis/cache/source-analyzer-search/` contains local search indexes (git-ignored).
- `.analysis/sessions/` contains transient working state (git-ignored).
- Release history is tracked in `CHANGELOG.md`.
- Licensing is provided in `LICENSE`.
