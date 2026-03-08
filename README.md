# AI Skills Repository

Public repository for reusable AI-agent skills, supporting both Codex and Claude Code.

Current release: `0.2.3`

## Overview

- Supports Codex and Claude Code distributions.
- Public skill layout uses language-specific variants under `ko/` and `en/`.
- Each skill root keeps an English `README.md` that links to the language-specific READMEs.
- Codex skills live under:
  - `codex/skills/source-analyzer`
  - `codex/skills/implement`
  - `codex/skills/plan-for-codex`
  - `codex/skills/refactor`
  - `codex/skills/review`
- Claude Code skills live under:
  - `claude-code/skills/source-analyzer`
  - `claude-code/skills/implement`
  - `claude-code/skills/plan`
  - `claude-code/skills/refactor`
  - `claude-code/skills/review`
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
  skills/
    source-analyzer/
    implement/
    plan/
    refactor/
    review/
      README.md
      ko/
      en/
      shared/
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
  install_claude_code_skill.sh
tests/
```

`codex/skills/<skill-name>` stores the Codex source layout.
`claude-code/skills/<skill-name>` stores the Claude Code source layout.
Installers select a language-specific variant and materialize the runtime root `SKILL.md` in the appropriate home directory.

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

## Install for Claude Code

Clone this repository, then install a language-specific skill variant into your Claude Code skills directory.

```bash
scripts/install_claude_code_skill.sh --list
scripts/install_claude_code_skill.sh --list-languages source-analyzer
scripts/install_claude_code_skill.sh source-analyzer ko
scripts/install_claude_code_skill.sh source-analyzer en
scripts/install_claude_code_skill.sh implement en
```

By default the installer copies skills into `${CLAUDE_HOME:-$HOME/.claude}/skills`.
It copies the full source skill directory, then promotes the selected language variant to the root `SKILL.md`.

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

Each skill root should look like this:

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

Use `.codex/skills/skill-generator` when you want to generate a new skill that follows this convention.

## Notes

- Codex discovers runtime skills from `~/.codex/skills`.
- Claude Code discovers runtime skills from `~/.claude/skills`.
- This repository keeps authoring-time structure separate from install-time structure.
- The `.codex/skills/skill-generator` helper is repository-specific and intended for skill authors.
- Release history is tracked in `CHANGELOG.md`.
- Licensing is provided in `LICENSE`.
