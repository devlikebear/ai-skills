# Changelog

All notable changes to this repository will be documented in this file.

## 0.1.0 - 2026-03-08

### Added

- Initial public Codex skill repository layout with `ko/`, `en/`, and `shared/` skill variants.
- Public `source-analyzer` skill source under `codex/skills/source-analyzer`.
- Repository-local `skill-generator` wrapper skill under `.codex/skills/skill-generator`.
- Release metadata via `VERSION` and this `CHANGELOG.md`.

### Changed

- Installer now validates skill names and languages before copying files.
- `.install_test_home` is ignored so local smoke-test state is not accidentally published.

### Security

- Reduced path traversal risk in `scripts/install_codex_skill.sh` by rejecting invalid skill names and language values before deriving install paths.
