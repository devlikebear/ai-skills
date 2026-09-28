# AI Skills Repository

Public repository for reusable AI-agent skills, supporting both Codex and Claude Code.

Current release: `1.0.0`

### Search CLI: A/B tested for token efficiency

`source-analyzer` ships a built-in search CLI (`brief`, `search --snippet-only`) that was A/B tested against raw file reads with identical questions across sub-agents:

| Metric | v0.10 (full text) | v0.11 (brief + snippet) | Raw file reads |
|--------|-------------------|------------------------|----------------|
| **Tokens** | 36,110 | **26,251** | 26,600 |
| **Tool calls** | 11 | **9** | 10 |
| **Duration** | 46s | **42s** | 49s |

The `brief` + `search --snippet-only --snippet-len 600` pattern matches raw file efficiency on small projects and scales better on large codebases — the agent reads only what it needs instead of full documents.

## Overview

- Supports both Codex runtime skills and a Claude Code plugin marketplace.
- Codex skills use a flat runtime layout: one `SKILL.md`, one `agents/openai.yaml`, and optional `shared/`.
- Claude Code skills are distributed through the `code-workflow` plugin with bilingual `SKILL.md` files and shared `references/`.
- `source-analyzer` produces resumable `.analysis/` outputs and never changes files outside `.analysis/`.
- Instruction registration and GitHub Wiki publishing are explicit-only companion skills.
- `source-analyzer` provides built-in CLI search commands for querying analysis outputs and checkpoints.
- A local MCP server is also available for agents that support MCP-based tool discovery.
- A local authoring wrapper lives at `.codex/skills/skill-generator`.
- Public Codex skill roots:
  - `codex/skills/app-service-planning`
  - `codex/skills/source-analyzer`
  - `codex/skills/register-analysis-context`
  - `codex/skills/publish-analysis-wiki`
  - `codex/skills/implement`
  - `codex/skills/refactor`
  - `codex/skills/review`
  - `codex/skills/github-flow`

## Product planning

Use `$app-service-planning` (standalone), `$code-workflow:app-service-planning`
(Codex plugin), or `/code-workflow:app-service-planning` (Claude Code) to turn a
product idea into an MVP and development plan. For example:

> 독서 기록 앱의 대상 사용자와 핵심 가치를 정하고 MVP 개발계획서를 작성해줘.

The skill supports new products and existing-product extensions. It reuses
relevant analysis after checking source freshness, asks only about consequential
unknowns, and writes in the user's language. It produces a brief, one development
plan, or a roadmap with vertical phase plans in `docs/plans/` (or the project's
existing location). A PRD-only request stays PRD-only.

Ordinary bug fixes, implementing an approved feature, and generic engineering
task breakdowns stay with existing engineering workflows (`implement`, `review`,
or the host's built-in planning mode). The former `plan` / `plan-for-codex`
skills were removed in 1.0.0 because they overlapped with product planning. A repository path alone
does not trigger product planning. Plans contain acceptance checks rather than mandatory
approval after every task, and do not authorize implementation or deployment.
No MCP server is required for planning.

## Repository Layout

```text
codex/
  skills/
    app-service-planning/  # Product discovery, MVP, development plans
    source-analyzer/       # BFS codebase analysis (3 modes)
    register-analysis-context/ # Explicit instruction registration
    publish-analysis-wiki/ # Explicit Wiki preview and publishing
    implement/             # Work order execution
    refactor/              # Behavior-preserving refactoring
    review/                # Diff-based code review
    github-flow/           # Full GitHub Flow lifecycle
claude-code/
  plugin/
    .claude-plugin/
      plugin.json          # code-workflow plugin manifest
    .mcp.json              # MCP server config (optional)
    skills/                # 9 Claude Code skills
    references/            # Shared reference templates
    scripts/               # checkpoint_manager.py (canonical), search, wiki
    servers/               # MCP server bundle (synced copy)
.agents/
  plugins/
    marketplace.json       # Codex local marketplace
.claude-plugin/
  marketplace.json         # Claude Code marketplace
plugins/
  code-workflow/           # Codex workflow plugin (8 skills + MCP)
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
- Ships `checkpoint_manager.py`; publishing is owned by the explicit-only `publish-analysis-wiki` skill.
- Provides CLI search commands: `search`, `get-overview`, `get-module`, `trace-deps`, `get-issues`.
- Also ships a local MCP server under `servers/source-analyzer-mcp/` for MCP-capable agents.

### `register-analysis-context`

- Explicitly registers an existing `.analysis/AI_CONTEXT.md` pointer in project instruction files.
- Preserves existing guidance and never runs implicitly.

### `publish-analysis-wiki`

- Previews reviewed `.analysis/outputs/` and publishes them to GitHub Wiki only on explicit request.
- Requires a reviewed dry-run before any push.

### `implement`

- Executes an approved work order directly.
- Keeps the scope small, explicit, and verification-driven.

### `refactor`

- Performs safe, behavior-preserving refactoring.
- Integrates with `source-analyzer` via `issue-candidates.md` for analysis-driven refactoring.
- Uses shared checklists and refactoring patterns.

### `review`

- Performs diff-based review focused on regressions, security issues, and missing tests.
- Produces a fix work order when changes are required.

### `github-flow`

- Guides through the full GitHub Flow lifecycle: branch → develop → PR → merge → release.
- Phase 2 runs work-order scoping → `implement` → `review` as an inner loop before each commit.
- Available for both Codex (`/github-flow`) and Claude Code (`/code-workflow:github-flow`).

### `skill-generator`

- Lives under `.codex/skills/skill-generator`.
- Wraps the upstream `skill-creator` workflow for this repository.
- Enforces the flat `SKILL.md` + `agents/openai.yaml` + optional `shared/` convention used by public Codex skills.

## Install for Codex

The recommended distribution is the `code-workflow` plugin. Add the repository
marketplace, install the plugin, and verify the installed version:

```bash
codex plugin marketplace add devlikebear/ai-skills
codex plugin add code-workflow@ai-skills-local
codex plugin list
```

For local development, use `codex plugin marketplace add <absolute-repo-path>`.
The repo marketplace is `.agents/plugins/marketplace.json`, and the installed
bundle contains all eight skills plus `source-analyzer-search` MCP configuration.

Codex also discovers repo-local authoring skills from `.agents/skills/` and
personal skills from `$HOME/.agents/skills/`. Use those locations for a single
local workflow; use the plugin when distributing this full skill set.

### Update Codex plugin

Refresh a Git-backed marketplace and reinstall the plugin so its versioned cache
is rebuilt:

```bash
codex plugin marketplace upgrade ai-skills-local
codex plugin remove code-workflow@ai-skills-local
codex plugin add code-workflow@ai-skills-local
codex plugin list
```

For a local-path marketplace, update the checkout, remove and add the plugin,
then restart Codex or open a new task.

### Roll back Codex plugin

Pin the marketplace to a known Git tag or commit, then reinstall:

```bash
codex plugin remove code-workflow@ai-skills-local
codex plugin marketplace remove ai-skills-local
codex plugin marketplace add devlikebear/ai-skills --ref <known-good-tag>
codex plugin add code-workflow@ai-skills-local
```

Confirm the selected version with `codex plugin list` before resuming work.

### Legacy standalone installer

`scripts/install_codex_skill.sh` remains a legacy compatibility path for users
already installed under `${CODEX_HOME:-$HOME/.codex}/skills`. It supports the
existing `--with-mcp` flow, but new installs should use the plugin or modern
`.agents/skills` locations. It will not be removed before a future major release
with an announced migration window.

```bash
scripts/install_codex_skill.sh source-analyzer --with-mcp
scripts/install_codex_skill.sh --all
```

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

- `/code-workflow:implement`
- `/code-workflow:review`
- `/code-workflow:refactor`
- `/code-workflow:app-service-planning`
- `/code-workflow:source-analyzer`
- `/code-workflow:register-analysis-context`
- `/code-workflow:publish-analysis-wiki`
- `/code-workflow:github-flow`

Plugin skills are bilingual and detect the user's language automatically.
The plugin also bundles `source-analyzer-search` through `claude-code/plugin/.mcp.json`.

### Update or roll back Claude Code plugin

Use `/plugin` in Claude Code to refresh the marketplace and reinstall
`code-workflow@ai-skills`. For rollback, check out or register a marketplace ref
at the required tag, uninstall the current plugin, and install it again. Restart
Claude Code after changing a bundled MCP server and verify the available skills
before continuing.

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

The explicit `publish-analysis-wiki` workflow uses these distributed publishers:

- `codex/skills/publish-analysis-wiki/shared/scripts/publish_wiki.sh`
- `claude-code/plugin/scripts/publish_wiki.sh`

Those distributed scripts support `--project-dir <path>` so they can publish analysis outputs from another checked-out project.

## Platform support

The skill documents and Python MCP server are platform-neutral. The release
contract statically checks every MCP manifest and the full test suite performs
the runtime smoke test on the release host.

| Platform | Skills and plugin | MCP launcher | Notes |
|---|---|---|---|
| macOS | Supported | `python3` direct launch | Full tests and install smoke run on the release host. |
| Linux | Supported | `python3` direct launch | Requires Python 3 on `PATH`. |
| Windows | Supported through WSL or Git Bash | `python3` direct launch | Native environments must expose a `python3` command; WSL is the recommended compatibility route. |

No MCP manifest injects Homebrew paths or wraps the server with `bash -c`.
Platform-specific package managers and Python aliases remain the user's runtime
responsibility.

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

- Codex discovers authored skills from repo or user `.agents/skills` locations;
  `${CODEX_HOME:-$HOME/.codex}/skills` is supported here only by the legacy installer.
- Codex MCP servers can be registered directly with `codex mcp add ...`.
- Claude Code installs skills via plugin marketplace.
- `.analysis/outputs/` contains publishable, git-trackable analysis outputs.
- `.analysis/cache/source-analyzer-search/` contains local search indexes (git-ignored).
- `.analysis/sessions/` contains transient working state (git-ignored).
- Release history is tracked in `CHANGELOG.md`.
- Licensing is provided in `LICENSE`.
