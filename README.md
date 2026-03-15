# AI Skills Repository

Public repository for reusable AI-agent skills, supporting both Codex and Claude Code.

Current release: `0.9.0`

## Overview

- Supports both Codex runtime skills and a Claude Code plugin marketplace.
- Codex skills use a flat runtime layout: one `SKILL.md`, one `agents/openai.yaml`, and optional `shared/`.
- Claude Code skills are distributed through the `code-workflow` plugin with bilingual `SKILL.md` files and shared `references/`.
- `source-analyzer` produces resumable `.analysis/` outputs and now ships a wiki publisher alongside its checkpoint manager.
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
    skills/
      source-analyzer/
      implement/
      plan/
      refactor/
      review/
      github-flow/
    references/
    scripts/
.claude-plugin/
  marketplace.json
.codex/
  skills/
    skill-generator/
      SKILL.md
      agents/
scripts/
  install_codex_skill.sh
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
scripts/install_codex_skill.sh implement
scripts/install_codex_skill.sh --all
```

By default the installer copies skills into `${CODEX_HOME:-$HOME/.codex}/skills`.
Each skill is a single `SKILL.md` that responds in the user's language automatically.

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
- Claude Code installs skills via plugin marketplace.
- `.analysis/outputs/` contains publishable, git-trackable analysis outputs.
- Release history is tracked in `CHANGELOG.md`.
- Licensing is provided in `LICENSE`.
