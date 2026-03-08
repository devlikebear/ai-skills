# Changelog

All notable changes to this repository will be documented in this file.

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
