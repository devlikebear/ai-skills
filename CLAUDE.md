# AI Skills — Development Guide

## Project overview

Reusable AI-agent skills for code workflow automation. Ships two distributions:
- **Codex**: `codex/skills/` — flat skill directories with `SKILL.md`, `agents/openai.yaml`, `shared/`
- **Claude Code plugin**: `claude-code/plugin/` — plugin with `skills/`, `references/`, `scripts/`

Both distributions share the same `checkpoint_manager.py` — always keep them identical.

## Release workflow — MUST follow on every change

Every commit that changes skill behavior (SKILL.md, scripts, references, templates) MUST include a version bump in the same commit or as an immediately following commit.

### Version bump checklist

Update ALL of these files — they must stay in sync:

1. `VERSION.txt`
2. `.claude-plugin/marketplace.json` (two `"version"` fields)
3. `claude-code/plugin/.claude-plugin/plugin.json` (one `"version"` field)
4. `CHANGELOG.md` (add new entry at top with date and changes)

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
- SKILL.md differs only in reference paths and checkpoint script path:
  - Codex: `shared/references/...`, `$CODEX_HOME` path
  - Claude: `../../references/...` relative links, `$CLAUDE_PLUGIN_ROOT` path
- Codex SKILL.md includes `Prefer rg, sed, head, tail, cat, find, ls` in constraints
- Claude SKILL.md omits that line (Claude Code has its own tool preferences)
- Fallback file creation when no instruction files exist:
  - Codex version creates `AGENTS.md`
  - Claude version creates `CLAUDE.md`

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
claude-code/plugin/skills/               ← Claude Code skills
claude-code/plugin/references/           ← shared references (Claude)
claude-code/plugin/scripts/              ← shared scripts (Claude)
codex/skills/                            ← Codex skills
tests/                                   ← test suite
```

## Codebase Analysis

Architecture and module analysis available at `.analysis/AI_CONTEXT.md`.
Read it first when you need to understand the project structure, dependencies, or key data flows.
