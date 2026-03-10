---
name: skill-generator
description: "Wrapper around the upstream skill-creator guidance for generating Codex skills in this repository with a flat layout: single SKILL.md with auto-detect language policy plus optional shared/ directory."
---

# Skill Generator Wrapper

Use this wrapper when the user wants to create or update a Codex skill in this repository.

## Language policy

- Respond in the same language the user writes in.
- If the user explicitly requests a language, follow it.

## Upstream dependency

- First read `${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/SKILL.md` just enough to follow its workflow.
- Reuse the upstream process for naming, planning, initialization, and validation.
- This wrapper only adds repository-specific structure rules.

## Repository skill layout

Create skills with this shape:

```text
<skill-name>/
  SKILL.md             # single file — auto-detects user's language at runtime
  agents/
    openai.yaml
  shared/              # optional
    scripts/
    references/
    assets/
```

## Required rules

1. Write a single `SKILL.md` with this language policy:
   ```
   - Respond in the same language the user writes in.
   - If the user explicitly requests a language, follow it.
   ```
2. Put reusable scripts, references, and assets in `shared/` whenever possible.
3. Keep `SKILL.md` focused — reference shared files rather than inlining them.
4. Treat this skill as a wrapper around `skill-creator`; keep the wrapper focused and concise.

## Authoring flow

1. Confirm the skill name and trigger examples.
2. Follow `skill-creator` to decide what belongs in `SKILL.md`, `shared/references/`, `shared/scripts/`, and `shared/assets/`.
3. Write the single `SKILL.md` with the auto-detect language policy.
4. Add `agents/openai.yaml`.
5. Validate that the `SKILL.md` frontmatter `description` is quoted and contains no bare colons.

## Constraints

- Do not create `ko/` or `en/` language subdirectories.
- Do not create extra documentation files unless explicitly requested.
- If content is reusable across skills, put it in `shared/` and reference it.
