---
name: skill-generator
description: "Wrapper around the upstream skill-creator guidance for generating Codex skills in this repository with a language-specific layout: root English README plus `ko/`, `en/`, and optional `shared/` directories."
---

# Skill Generator Wrapper

Use this wrapper when the user wants to create or update a Codex skill in this repository.

## Upstream dependency

- First read `${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/SKILL.md` just enough to follow its workflow.
- Reuse the upstream process for naming, planning, initialization, and validation.
- This wrapper only adds repository-specific structure and language rules.

## Repository skill layout

Create skills with this shape:

```text
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

## Required rules

1. Write the root `README.md` in English.
2. The root `README.md` must link to `./ko/README.md` and `./en/README.md`.
3. Put language-specific trigger logic in `ko/SKILL.md` and `en/SKILL.md`.
4. Put reusable scripts, references, and assets in `shared/` whenever possible.
5. Keep the Korean variant Korean-default and the English variant English-default.
6. Treat this skill as a wrapper around `skill-creator`; keep the wrapper focused and concise.

## Authoring flow

1. Confirm the skill name and trigger examples.
2. Follow `skill-creator` to decide what belongs in `SKILL.md`, `shared/references/`, `shared/scripts/`, and `shared/assets/`.
3. Create the English root README and both language READMEs.
4. Write `ko/SKILL.md` and `en/SKILL.md` with the same workflow but language-specific defaults.
5. Add `ko/agents/openai.yaml` and `en/agents/openai.yaml`.
6. Validate that links, names, and paths match exactly.

## Constraints

- Do not create extra documentation beyond the required READMEs unless the user asks for it.
- Keep shared content out of the language-specific SKILL bodies.
- If a language-specific difference is unnecessary, put it in `shared/` and reference it.
