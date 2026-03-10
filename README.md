# AI Skills Repository

Public repository for reusable AI-agent skills, supporting both Codex and Claude Code.

Current release: `0.3.0`

## Overview

- Supports Codex and Claude Code distributions.
- Codex skills use language-specific variants under `ko/` and `en/`.
- Claude Code skills are distributed as a plugin marketplace with bilingual auto-detection.
- Codex skills live under:
  - `codex/skills/source-analyzer`
  - `codex/skills/implement`
  - `codex/skills/plan-for-codex`
  - `codex/skills/refactor`
  - `codex/skills/review`
- Claude Code skills live under `claude-code/plugin/` as a plugin marketplace.
- A local authoring wrapper lives at `.codex/skills/skill-generator`.

## Repository Layout

```text
codex/
  skills/
    source-analyzer/
    implement/
    plan-for-codex/
    refactor/
    review/
      README.md
      ko/
      en/
      shared/
claude-code/
  plugin/
    .claude-plugin/
      plugin.json
    skills/
      review/
      implement/
      plan/
      refactor/
      source-analyzer/
    references/
    scripts/
.claude-plugin/
  marketplace.json
.codex/
  skills/
    skill-generator/
      README.md
      ko/
      en/
scripts/
  install_codex_skill.sh
tests/
```

`codex/skills/<skill-name>` stores the Codex source layout with language-specific variants.
`claude-code/plugin/` is the Claude Code plugin distribution — each skill is a single bilingual `SKILL.md` with shared references.

## Included Skills

### `source-analyzer`

- Analyzes an existing codebase without modifying source files.
- Produces resumable checkpointed outputs under `.analysis/`.
- Supports `analyze` and `refactor-guide` modes.
- Ships as language-specific variants with shared scripts and references.

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

### `skill-generator`

- Lives under `.codex/skills/skill-generator`.
- Wraps the upstream `skill-creator` workflow for this repository.
- Enforces the root-English-README plus `ko/`, `en/`, and `shared/` convention.

## Install for Codex

Clone this repository, then install a language-specific skill variant into your local Codex home.

```bash
scripts/install_codex_skill.sh --list
scripts/install_codex_skill.sh --list-languages source-analyzer
scripts/install_codex_skill.sh source-analyzer ko
scripts/install_codex_skill.sh source-analyzer en
scripts/install_codex_skill.sh implement en
```

By default the installer copies skills into `${CODEX_HOME:-$HOME/.codex}/skills`.
It copies the full source skill directory, then promotes the selected language variant to the root `SKILL.md` and `agents/openai.yaml`.

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

Plugin skills are bilingual — they detect the user's language and respond accordingly.

## Skill Root Convention

### Codex skills

```bash
<skill-name>/
  README.md
  ko/
    README.md
    SKILL.md
    agents/openai.yaml
  en/
    README.md
    SKILL.md
    agents/openai.yaml
  shared/
    scripts/
    references/
    assets/
```

### Claude Code plugin skills

```bash
<skill-name>/
  SKILL.md       # bilingual — detects user's language automatically
```

Shared references live in `claude-code/plugin/references/` and are referenced by all plugin skills.

Use `.codex/skills/skill-generator` when you want to generate a new Codex skill that follows the language-variant convention.

## Notes

- Codex discovers runtime skills from `~/.codex/skills`.
- Claude Code installs skills via plugin marketplace.
- The `.codex/skills/skill-generator` helper is repository-specific and intended for skill authors.
- Release history is tracked in `CHANGELOG.md`.
- Licensing is provided in `LICENSE`.
