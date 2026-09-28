# AI Skills — Development Guide

## Project overview

Reusable AI-agent skills for code workflow automation. Ships two distributions:
- **Codex**: `codex/skills/` — flat skill directories with `SKILL.md`, `agents/openai.yaml`, `shared/`
- **Claude Code plugin**: `claude-code/plugin/` — plugin with `skills/`, `references/`, `scripts/`

Both distributions share the same `checkpoint_manager.py` — always keep them identical.
Canonical MCP sources live under `servers/source-analyzer-mcp/` and should be copied into bundle/runtime locations with `scripts/sync_source_analyzer_mcp.sh`.

## Release workflow — MUST follow on every change

Every commit that changes skill behavior (SKILL.md, scripts, references, templates) MUST include a version bump in the same commit or as an immediately following commit.

### Version bump checklist

Update ALL of these files — they must stay in sync:

1. `VERSION.txt`
2. `.claude-plugin/marketplace.json` (two `"version"` fields)
3. `claude-code/plugin/.claude-plugin/plugin.json` (one `"version"` field)
4. `plugins/source-analyzer-tools/.codex-plugin/plugin.json` (one `"version"` field)
5. `plugins/code-workflow/.codex-plugin/plugin.json` (one `"version"` field)
6. `servers/source-analyzer-mcp/server.py` (`SERVER_VERSION`), then run `scripts/sync_source_analyzer_mcp.sh` to update its copies
7. `claude-code/plugin/servers/source-analyzer-mcp/pyproject.toml` (`version`)
8. `CHANGELOG.md` (add new entry at top with date and changes)

`tests/test_release_contract.py` enforces these versions.

### Versioning scheme

- **PATCH** (0.x.Y): bug fixes, wording changes, small improvements
- **MINOR** (0.X.0): new features, new outputs, new CLI commands, new skill sections
- **MAJOR** (X.0.0): breaking changes to skill interface or checkpoint format

### Commit convention

```
feat: ...   → minor bump
fix: ...    → patch bump
chore: ...  → version bump commit itself, docs-only changes
```

## Dual-distribution sync rules

When modifying source-analyzer or shared scripts:

- `checkpoint_manager.py` must be identical in both locations:
  - `codex/skills/source-analyzer/shared/scripts/checkpoint_manager.py`
  - `claude-code/plugin/scripts/checkpoint_manager.py`
- `source_analyzer_search.py` must be identical in both locations:
  - `codex/skills/source-analyzer/shared/scripts/source_analyzer_search.py`
  - `claude-code/plugin/scripts/source_analyzer_search.py`
- SKILL.md differs only in reference paths and checkpoint script path:
  - Codex: `shared/references/...`, `$CODEX_HOME` path
  - Claude: `../../references/...` relative links, `$CLAUDE_PLUGIN_ROOT` path
- Codex SKILL.md includes `Prefer rg, sed, head, tail, cat, find, ls` in constraints
- Claude SKILL.md omits that line (Claude Code has its own tool preferences)
- Fallback file creation when no instruction files exist:
  - Codex version creates `AGENTS.md`
  - Claude version creates `CLAUDE.md`

### Product-planning resources

`codex/skills/app-service-planning/` is canonical. Do not edit the Claude copy
by hand: `scripts/sync_codex_workflow_plugin.sh` refreshes the Codex bundle and
generates `claude-code/plugin/skills/app-service-planning/SKILL.md` and
`claude-code/plugin/references/app-service-planning/` (with `shared/` links
rewritten to `../../references/app-service-planning/`).
`tests/test_app_service_planning.py` checks every copy and installed references.

## Testing

```bash
python3 -m unittest discover tests -v
```

All tests must pass before committing. Test file for checkpoint_manager is `tests/test_checkpoint_manager.py`.

## File structure quick reference

```
VERSION.txt                              ← single source of version
CHANGELOG.md                             ← release notes
.claude-plugin/marketplace.json          ← plugin marketplace manifest
claude-code/plugin/.claude-plugin/plugin.json ← plugin manifest
claude-code/plugin/.mcp.json             ← Claude plugin MCP config
claude-code/plugin/skills/               ← Claude Code skills
claude-code/plugin/references/           ← shared references (Claude)
claude-code/plugin/scripts/              ← shared scripts (Claude)
plugins/source-analyzer-tools/           ← Codex MCP plugin bundle
.agents/plugins/marketplace.json         ← Codex local marketplace manifest
codex/skills/                            ← Codex skills
tests/                                   ← test suite
scripts/sync_source_analyzer_mcp.sh      ← sync MCP server copies
```

## Codebase Analysis

Architecture and module analysis available at `.analysis/AI_CONTEXT.md`.
Read it first when you need to understand the project structure, dependencies, or key data flows.
