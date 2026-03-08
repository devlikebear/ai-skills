# AI Skills Repository

Public repository for reusable AI-agent skills, starting with Codex-compatible packages.

Current release: `0.1.2`

## Overview

- Current scope: Codex-only distribution.
- Public skill layout uses language-specific variants under `ko/` and `en/`.
- Each skill root keeps an English `README.md` that links to the language-specific READMEs.
- The first public skill is `codex/skills/source-analyzer`.
- A local authoring wrapper lives at `.codex/skills/skill-generator`.

## Repository Layout

```text
codex/
  skills/
    source-analyzer/
      README.md
      ko/
      en/
      shared/
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

`codex/skills/<skill-name>` stores the source layout for the repository.
The installer selects a language-specific variant and materializes the runtime root `SKILL.md` in `~/.codex/skills/<skill-name>`.

## Included Skills

### `source-analyzer`

- Analyzes an existing codebase without modifying source files.
- Produces resumable checkpointed outputs under `.analysis/`.
- Supports `analyze` and `refactor-guide` modes.
- Ships as language-specific variants with shared scripts and references.

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
```

By default the installer copies skills into `${CODEX_HOME:-$HOME/.codex}/skills`.
It copies the full source skill directory, then promotes the selected language variant to the root `SKILL.md` and `agents/openai.yaml`.

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
- This repository keeps authoring-time structure separate from install-time structure.
- The `.codex/skills/skill-generator` helper is repository-specific and intended for skill authors.
- Release history is tracked in `CHANGELOG.md`.
- Licensing is provided in `LICENSE`.
