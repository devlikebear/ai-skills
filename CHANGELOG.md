# Changelog

All notable changes to this repository will be documented in this file.

## 0.3.3 - 2026-03-10

### Changed

- Simplified `.codex/skills/skill-generator` to match the flat skill structure.
  - Removed `ko/`, `en/`, and `README.md`.
  - Updated `SKILL.md` to use auto-detect language policy and document the new flat layout convention.
  - Updated `agents/openai.yaml` default_prompt accordingly.

## 0.3.2 - 2026-03-10

### Changed

- Simplified Codex skill structure: removed `ko/` and `en/` language directories from all `codex/skills/`.
  - Each skill now ships as a single root `SKILL.md` that auto-detects the user's language.
  - `agents/openai.yaml` promoted to the skill root; `shared/` remains unchanged.
- Simplified `scripts/install_codex_skill.sh`: removed the `<language>` argument and `--list-languages` command.
  - New usage: `install_codex_skill.sh <skill-name>` or `install_codex_skill.sh --all`.

### Removed

- Removed language-specific `ko/` and `en/` variants from all Codex skills.
- Removed `--list-languages` and language-validation logic from the installer.

## 0.3.1 - 2026-03-10

### Added

- Added `github-flow` skill for both Codex and Claude Code.
  - Covers the full GitHub Flow lifecycle: branch → develop → PR → merge → release.
  - Phase 2 integrates `plan` → `implement` → `review` as a structured inner loop before each commit.
  - Codex: `codex/skills/github-flow/` with `ko/`, `en/`, and `shared/` variants.
  - Claude Code plugin: `claude-code/plugin/skills/github-flow/SKILL.md` (bilingual auto-detect).
- Added `github-flow-checklist.md` to both `claude-code/plugin/references/` and `codex/skills/github-flow/shared/references/`.

## 0.3.0 - 2026-03-10

### Changed

- Consolidated Claude Code skill distribution to use the `claude-code/plugin/` structure exclusively.
- Removed the redundant `claude-code/skills/` directory (multi-language `ko/`/`en/`/`shared/` layout). Plugin skills handle bilingual output via automatic language detection in a single `SKILL.md`.
- Shared references are now maintained in one place (`claude-code/plugin/references/`) instead of being duplicated per skill.

### Removed

- Removed `scripts/install_claude_code_skill.sh`. Claude Code skills are installed via the plugin marketplace (`/plugin install code-workflow@ai-skills`), not a manual script.
- Removed contract tests that validated the now-deleted `claude-code/skills/` language-directory layout.

## 0.2.3 - 2026-03-08

### Added

- Added Claude Code skill variants under `claude-code/skills/` with `ko/`, `en/`, and `shared/` layout matching the Codex convention.
- Added `scripts/install_claude_code_skill.sh` installer for Claude Code skills.
- Added Claude Code plugin marketplace support:
  - `.claude-plugin/marketplace.json` at repo root registers this repo as a plugin marketplace.
  - `claude-code/plugin/` contains the `code-workflow` plugin with all five skills (plan, implement, review, refactor, source-analyzer).
  - Plugin skills are bilingual — they detect the user's language and respond accordingly.
- Added contract tests for Claude Code skills and plugin marketplace structure.

### Changed

- Renamed `plan-for-codex` to `plan` in the Claude Code distribution since it is no longer Codex-specific.
- Updated repository README to document Claude Code skills, plugin marketplace installation, and the new installer.

## 0.2.2 - 2026-03-08

### Fixed

- Flattened the local project wrapper skill at `.codex/skills/skill-generator` so it exposes a single root `SKILL.md` and a single root `agents/openai.yaml`.
- Kept `ko/README.md` and `en/README.md` only as human-facing guidance, preventing duplicate local skill entries in Codex.

## 0.2.1 - 2026-03-08

### Fixed

- Changed the installer to materialize only one runtime skill at `~/.codex/skills/<skill-name>` instead of copying nested `ko/` and `en/` variants into the installed skill.
- Removed `KO` and `EN` suffixes from installed skill display names so Codex shows a single clean skill entry per install.

## 0.2.0 - 2026-03-08

### Added

- Added four new public code skills under `codex/skills/`:
  - `implement`
  - `plan-for-codex`
  - `refactor`
  - `review`
- Added language-specific `ko/` and `en/` variants plus shared references for each new skill.

### Changed

- Updated the repository README to document all public skills.
- Ignored `.drafts/` and `.draft/` so local draft skills are not published accidentally.

## 0.1.2 - 2026-03-08

### Fixed

- Quoted `description` values in all `SKILL.md` frontmatter blocks so YAML parsers do not fail on colons inside description text.
- Added a contract test to keep future `SKILL.md` frontmatter descriptions YAML-safe.

## 0.1.1 - 2026-03-08

### Added

- Added `LICENSE` with the MIT license for public reuse.

### Changed

- Renamed release metadata file from `VERSION` to `VERSION.txt` to avoid IDE extension warnings.
- Updated repository docs to reference `VERSION.txt` and `LICENSE`.

### Security

- Moved `security_best_practices_report.md` out of tracked release artifacts and added it to `.gitignore`.

## 0.1.0 - 2026-03-08

### Added

- Initial public Codex skill repository layout with `ko/`, `en/`, and `shared/` skill variants.
- Public `source-analyzer` skill source under `codex/skills/source-analyzer`.
- Repository-local `skill-generator` wrapper skill under `.codex/skills/skill-generator`.
- Release metadata via `VERSION.txt`, `LICENSE`, and this `CHANGELOG.md`.

### Changed

- Installer now validates skill names and languages before copying files.
- `.install_test_home` is ignored so local smoke-test state is not accidentally published.

### Security

- Reduced path traversal risk in `scripts/install_codex_skill.sh` by rejecting invalid skill names and language values before deriving install paths.
