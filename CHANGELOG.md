# Changelog

All notable changes to this repository will be documented in this file.

## 0.10.0 - 2026-04-05

### Added

- Added a local `source-analyzer-search` MCP server under `servers/source-analyzer-mcp/`.
  - Exposes overview, module lookup, hybrid search, dependency tracing, issue-candidate lookup, checkpoint reads, and session state queries.
  - Supports direct-scan fallback when `.analysis/cache/source-analyzer-search/` is missing.
- Added `generate-search-index` to `checkpoint_manager.py`.
  - Produces `search-documents.jsonl`, `chunk-manifest.json`, `file-to-chunks.json`, `output-to-chunks.json`, and `index-metadata.json`.
  - Tracks `dirty_files` and `last_indexed_commit` in session state for incremental retrieval context.
- Added Claude Code MCP bundle support through `claude-code/plugin/.mcp.json`.
- Added Codex MCP distribution artifacts:
  - skill installer support via `scripts/install_codex_skill.sh source-analyzer --with-mcp`
  - local plugin bundle under `plugins/source-analyzer-tools/`
  - local marketplace manifest under `.agents/plugins/marketplace.json`
- Added tests covering search index generation, MCP request handling, installer MCP registration, and repository contract checks for MCP assets.

### Changed

- Updated README and development guide for the new search MCP workflow, installation paths, and release metadata.
- Updated `source-analyzer` skill docs in both Codex and Claude distributions to describe `.analysis/cache/source-analyzer-search/` and the post-analysis search-index step.

## 0.9.0 - 2026-03-15

### Added

- System overhaul mode (`--mode overhaul`) for source-analyzer skill.
  - Identifies architectural flaws (`ARCH-*`), unnecessary features (`DEAD-*`), over-engineering (`OVER-*`), and accumulated technical debt (`DEBT-*`).
  - Produces `overhaul-<scope>.md` with target architecture, OH work orders, migration paths, execution order, and risk assessment.
  - Supports starting from existing analyze outputs or from scratch.
  - Breaking changes are explicitly documented with migration paths.
- `overhaul-template.md` reference file for both codex and claude-code distributions.

## 0.8.0 - 2026-03-15

### Added

- Root `scripts/publish_wiki.sh` helper for publishing this repository's analysis outputs to GitHub wiki.
  - Generates ordered wiki pages, module pages, Home, and Sidebar from `.analysis/sessions/<session-id>/outputs/`.
  - Supports `--session-id` and `--dry-run`.
- Distributed `publish_wiki.sh` helpers for `source-analyzer` in both codex (`shared/scripts/`) and claude-code (`plugin/scripts/`) distributions.
  - Support `--project-dir`, `--session-id`, and `--dry-run`.
  - Fall back to published outputs when session outputs are unavailable.
- Wiki publishing documentation added to source-analyzer SKILL.md (both codex and claude-code).

### Changed

- Updated README wording to reflect the `0.8.0` release, flat skill layout, and wiki publishing entry points.

## 0.7.0 - 2026-03-15

### Added

- Connected `source-analyzer` refactor-guide mode to `refactor` skill via `issue-candidates.md`.
  - refactor-guide mode now documents how to start from existing `issue-candidates.md` vs. scratch.
  - `refactor` skill (both codex and claude-code) now checks `.analysis/outputs/` for issue-candidates and existing work orders before starting.
- Added `Source Issue` traceability field to refactor-template.md WOs for linking back to analyze-mode findings.
- Added `Source` metadata field to refactor work order header.

### Changed

- Updated `refactor-template.md` output path from `.analysis/refactor-*.md` to `.analysis/outputs/refactor-*.md`.

## 0.6.1 - 2026-03-15

### Added

- `migrate` CLI command for backward compatibility with pre-0.6.0 layout.
  - Copies latest session outputs to `.analysis/outputs/` and prints `.gitignore` reminder.
  - Migration guide added to SKILL.md (both codex and claude-code).
- 3 new tests for migrate behavior (48 total).

## 0.6.0 - 2026-03-15

### Added

- Publish workflow: session outputs are now copied to `.analysis/outputs/` (git-tracked) on `paused`/`completed` checkpoints.
  - Session working state (`sessions/`) stays git-ignored; only stable outputs are committed.
  - New `publish` CLI command for manual publish.
  - Auto-publish on `paused`/`completed` checkpoints.
- Directory layout documentation in SKILL.md with recommended `.gitignore` entry.
- 5 new tests for publish behavior (25 total checkpoint manager tests, 45 total).

### Changed

- AI_CONTEXT.md paths now point to `.analysis/outputs/` instead of session-specific paths.
- `ensure_layout` now creates both `sessions/` and `outputs/` directories.
- `generate_summary` module file paths now use `outputs/modules/` relative format.

## 0.5.1 - 2026-03-15

### Fixed

- Auto-register analysis in all project instruction files (`CLAUDE.md`, `AGENTS.md`, `codex.md`, `.claude/CLAUDE.md`) instead of only suggesting manual addition.

## 0.5.0 - 2026-03-15

### Added

- Structured AI-consumable outputs: `SUMMARY.json`, `dependency-graph.json`, `module-map.json`.
- `generate-summary` CLI command to produce `SUMMARY.json` from session state.
- Default exclude patterns (`.analysis/`, `.codex/`, `.claude/`, `vendor/`, `node_modules/`, etc.) with `--exclude` CLI option for custom patterns.
- Empty checkpoint validation: rejects checkpoints with no visited files, outputs, summary, or next actions.
- Analyze-to-refactor bridge: `issue-candidates.md` generated at analyze pause/completion.
- Post-analysis AI context generation: `AI_CONTEXT.md` with pointers for CLAUDE.md integration.
- Sync incremental update notices for changed files in existing module documents.
- 6 new tests for exclude patterns, empty checkpoint rejection, and summary generation (20 total).

### Changed

- Updated `SKILL.md` for both codex and claude-code with structured output rules, bridge, and context generation sections.

## 0.4.0 - 2026-03-10

### Added

- Git-based incremental checkpoint system for source-analyzer.
  - Records HEAD commit hash in checkpoint state (v2) and detects changed files via `git diff` on resume.
  - Added `sync` CLI command to compare stored commit with current HEAD and update frontier.
  - Added `migrate_state()` for transparent v1→v2 session upgrade.
  - Only analyzes committed files (`git ls-tree -r HEAD`); ignores uncommitted/unstaged changes.
  - Force push/rebase fallback: invalid old commit triggers full rescan.
- Added 11 new tests for git helpers, migration, sync, and CLI sync (14 total).

### Changed

- Updated `SKILL.md` workflow and resume protocol (both codex and claude-code).
- Updated `checkpoint-template.md` with commit hash metadata (both).

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
