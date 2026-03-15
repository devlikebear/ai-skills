---
name: source-analyzer
description: "Analyze existing source code and generate beginner-friendly architecture documents or actionable refactoring work orders without modifying source files. Use when users ask for codebase analysis, clone-coding guides, BFS-style architecture/data-flow summaries, or refactor proposals with DUP/SEC/TIDY issue codes."
---

# Source Analyzer

## Load only what you need

- `shared/references/tutorial-template.md`: tutorial and clone-coding structure.
- `shared/references/refactor-template.md`: refactor work-order structure.
- `shared/references/tidy-first-rules.md`: TIDY rule mapping.
- `shared/references/security-triage-checklist.md`: security fallback checks.
- `shared/references/checkpoint-template.md`: manual checkpoint fallback.
- `shared/scripts/checkpoint_manager.py`: resumable checkpoint session manager.

## Language policy

- Respond in the same language the user writes in.
- If the user explicitly requests a language, follow it.

## Directory layout

```
.analysis/
├── RESUME.md              ← resume pointer (git-tracked)
├── AI_CONTEXT.md          ← AI discovery file (git-tracked)
├── outputs/               ← published stable outputs (git-tracked)
│   ├── overview.md
│   ├── architecture.md
│   ├── technologies.md
│   ├── glossary.md
│   ├── tutorial.md
│   ├── clone-coding.md
│   ├── implementation-checklist.md
│   ├── issue-candidates.md
│   ├── SUMMARY.json
│   ├── dependency-graph.json
│   ├── module-map.json
│   └── modules/
│       └── <name>.md
└── sessions/              ← working state (git-ignored)
    └── <session-id>/
        ├── state.json
        ├── index.md
        ├── checkpoints/
        └── outputs/       ← work-in-progress outputs
```

- `sessions/` contains transient analysis state and should be in `.gitignore`.
- `outputs/` at the root level contains published (stable) results and should be committed to git.
- Outputs are published automatically when a checkpoint is written with status `paused` or `completed`.
- Manual publish: `python3 "$CHECKPOINT_SCRIPT" publish`.

### Migrating from old layout

If the project has existing analysis results under `.analysis/sessions/<id>/outputs/` (pre-0.6.0 layout), run:

```bash
python3 "$CHECKPOINT_SCRIPT" migrate --analysis-dir .analysis
```

This copies the latest session's outputs to `.analysis/outputs/` and prints a `.gitignore` reminder. Run this once before starting new analysis sessions.

### Recommended .gitignore entry

```gitignore
.analysis/sessions/
```

## Required workflow

1. Decide the mode: `analyze` or `refactor-guide`.
2. Capture the current commit: `COMMIT=$(git rev-parse HEAD)`.
3. Start or resume a session: pass `--commit "$COMMIT"` to init.
4. If resuming, run `sync` to detect new commits and update the frontier.
5. Use `git ls-tree -r HEAD --name-only -- <scope>` to enumerate files (committed files only).
6. Filter out files matching exclude patterns (see Constraints).
7. Traverse first-party source with BFS in small chunks.
8. Update `.analysis/sessions/<session-id>/outputs/` after each chunk.
9. Write a checkpoint after each chunk (must include at least one of: visited-add, outputs, summary, or next-actions).
10. On `paused` or `completed` checkpoint, outputs are auto-published to `.analysis/outputs/`.

Use the shared checkpoint script:

```bash
CHECKPOINT_SCRIPT="${CODEX_HOME:-$HOME/.codex}/skills/source-analyzer/shared/scripts/checkpoint_manager.py"
COMMIT=$(git rev-parse HEAD)
python3 "$CHECKPOINT_SCRIPT" init --mode analyze --scope "." --commit "$COMMIT"
# Resume: sync with latest HEAD
python3 "$CHECKPOINT_SCRIPT" sync
python3 "$CHECKPOINT_SCRIPT" checkpoint --title "service layer analyzed" --status paused
# Manual publish (auto-runs on paused/completed checkpoint)
python3 "$CHECKPOINT_SCRIPT" publish
# Generate AI-consumable summary
python3 "$CHECKPOINT_SCRIPT" generate-summary
```

## Analyze mode

- Goal: produce newcomer-friendly architecture and clone-coding material.
- Markdown outputs (human-readable):
  - `overview.md`, `architecture.md`, `technologies.md`, `glossary.md`
  - `tutorial.md`, `clone-coding.md`, `implementation-checklist.md`
  - `modules/<name>.md`
- Structured outputs (AI-consumable):
  - `SUMMARY.json`: module list, key flows, known issues.
  - `dependency-graph.json`: `{"file": ["imported_file", ...]}` mapping.
  - `module-map.json`: `{"module_name": {"path": "...", "responsibility": "...", "key_files": [...]}}`.
- All outputs are written to `.analysis/sessions/<session-id>/outputs/` during work, then published to `.analysis/outputs/` on pause/complete.
- Use real file paths, short paragraphs, and plain language.

### Structured output rules

After completing each module analysis chunk, update the structured JSON outputs incrementally:

- `dependency-graph.json`: for each visited source file, record its import/dependency targets as an array. Use relative paths from project root.
- `module-map.json`: for each logical module (directory group), record path prefix, one-line responsibility, and list of key files.
- `SUMMARY.json`: auto-generated via `python3 "$CHECKPOINT_SCRIPT" generate-summary`. Run this after the final checkpoint or at each pause.

## Refactor-guide mode

- Goal: produce actionable work orders with `DUP-*`, `SEC-*`, and `TIDY-*` codes.
- Follow `shared/references/refactor-template.md` exactly.
- For each issue include evidence, completion criteria, and test criteria.
- Check security references first, then fall back to `shared/references/security-triage-checklist.md`.
- Output: `.analysis/sessions/<session-id>/outputs/refactor-<scope>.md` (published to `.analysis/outputs/` on pause/complete).

### Starting from issue-candidates

When `issue-candidates.md` exists (from a prior analyze session):

1. Read `.analysis/outputs/issue-candidates.md` first.
2. Use each candidate as the seed for a WO — copy the issue code, module, and evidence into the WO's `Source Issue` field.
3. Expand each candidate with full analysis: read the actual source files, verify the issue, and fill all required WO fields.
4. Remove candidates that turn out to be false positives and note the reason.

### Starting from scratch

When no `issue-candidates.md` exists, perform BFS analysis in refactor-guide mode directly and produce WOs as you discover issues.

## Analyze-to-refactor bridge

When analyze mode completes (or pauses), scan the produced documents for refactor candidates and write:

- `.analysis/sessions/<session-id>/outputs/issue-candidates.md`

Format each candidate as:

```markdown
### <CODE>-<NNN>: <short title>

- Module: `<module path>`
- Type: `DUP` | `SEC` | `TIDY`
- Evidence: <1-2 sentence observation from analyze outputs>
- Suggested action: <brief description>
```

This file is published to `.analysis/outputs/issue-candidates.md` and serves as the starting point when the user later runs `refactor-guide` mode or the `refactor` skill.

## Sync and incremental update

When `sync` detects changed files:

1. Changed files are added to the frontier for re-analysis.
2. For each changed file that has an existing module document, prepend a notice:
   ```
   > **Updated since last analysis** — file changed between commits `<old>...<new>`. Re-analysis pending.
   ```
3. After re-analyzing changed files, remove the notice and update the content.

## Resume protocol

1. Open `.analysis/RESUME.md`.
2. Open the referenced `index.md`, latest checkpoint, and `state.json`.
3. Run `sync` to detect new commits.
   - `status=synced`: changed files added to frontier for re-analysis.
   - `status=unchanged`: continue BFS from existing frontier.
4. Continue from `frontier` and pending `next actions`.
5. Write the next checkpoint before ending.

## Post-analysis: AI context generation

When the session reaches `completed` or `paused` status, generate a context file for AI assistants:

1. Run `python3 "$CHECKPOINT_SCRIPT" generate-summary` to produce `outputs/SUMMARY.json`.
2. Run `python3 "$CHECKPOINT_SCRIPT" publish` (or rely on auto-publish from checkpoint).
3. Write `.analysis/AI_CONTEXT.md` with the following structure:

```markdown
# Codebase Analysis Context

> Auto-generated by source-analyzer. Session: `<session-id>`
> Commit: `<hash>` | Status: `<status>` | Updated: `<timestamp>`

## Quick Reference

- Overview: `.analysis/outputs/overview.md`
- Architecture: `.analysis/outputs/architecture.md`
- Module details: `.analysis/outputs/modules/`
- Structured data: `.analysis/outputs/SUMMARY.json`
- Dependency graph: `.analysis/outputs/dependency-graph.json`

## Module Summary

<one-line summary per module from module-map.json>

## Known Issues

<list from issue-candidates.md if exists>
```

4. Register the analysis in project instruction files so all AI assistants can discover it.
   Check for these files in the project root and append a pointer block to each one that exists:
   - `CLAUDE.md` (Claude Code)
   - `AGENTS.md` (Codex / general agents)
   - `codex.md` (Codex legacy)
   - `.claude/CLAUDE.md` (Claude Code project-level)

   Append this block only if a `## Codebase Analysis` section does not already exist:

   ```markdown
   ## Codebase Analysis

   Architecture and module analysis available at `.analysis/AI_CONTEXT.md`.
   Read it first when you need to understand the project structure, dependencies, or key data flows.
   ```

   If none of these files exist, create `AGENTS.md` with the block above and inform the user.

## Constraints

- Never modify analyzed source files.
- Update only `.analysis/` outputs while running this skill.
- Only analyze files committed to git (`git ls-tree -r HEAD --name-only`). Ignore uncommitted/unstaged changes.
- Exclude non-source paths by default: `.analysis/`, `.codex/`, `.claude/`, `.git/`, `vendor/`, `node_modules/`, `.venv/`, `__pycache__/`, `dist/`, `build/`. Pass `--exclude` to add more patterns.
- Every checkpoint must contain at least one of: visited files, output files, summary text, or next actions. Empty checkpoints are rejected.
- Prefer `rg --files`, `rg`, `sed -n`, `head`, `tail`, `cat`, `find`, and `ls` for inspection.
