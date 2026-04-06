---
name: source-analyzer
description: "Analyze existing source code and generate beginner-friendly architecture documents, actionable refactoring work orders, or system overhaul proposals without modifying source files. Use when users ask for codebase analysis, clone-coding guides, BFS-style architecture/data-flow summaries, refactor proposals with DUP/SEC/TIDY issue codes, or system overhaul with ARCH/DEAD/OVER/DEBT issue codes."
---

# Source Analyzer

## References

- [tutorial-template.md](../../references/tutorial-template.md): tutorial and clone-coding structure.
- [refactor-template.md](../../references/refactor-template.md): refactor work-order structure.
- [tidy-first-rules.md](../../references/tidy-first-rules.md): TIDY rule mapping.
- [security-triage-checklist.md](../../references/security-triage-checklist.md): security fallback checks.
- [overhaul-template.md](../../references/overhaul-template.md): system overhaul proposal structure.
- [checkpoint-template.md](../../references/checkpoint-template.md): manual checkpoint fallback.

Scripts:
- Checkpoint session manager: `${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint_manager.py`
- Search chunk builder: `${CLAUDE_PLUGIN_ROOT}/scripts/source_analyzer_search.py`
- Wiki publisher: `${CLAUDE_PLUGIN_ROOT}/scripts/publish_wiki.sh`

Checkpoint session manager script:

```bash
CHECKPOINT_SCRIPT="${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint_manager.py"
COMMIT=$(git rev-parse HEAD)
python3 "$CHECKPOINT_SCRIPT" init --mode analyze --scope "." --commit "$COMMIT"
# Resume: sync with latest HEAD
python3 "$CHECKPOINT_SCRIPT" sync
python3 "$CHECKPOINT_SCRIPT" checkpoint --title "service layer analyzed" --status paused
# Manual publish (auto-runs on paused/completed checkpoint)
python3 "$CHECKPOINT_SCRIPT" publish
# Generate AI-consumable summary
python3 "$CHECKPOINT_SCRIPT" generate-summary
# Generate search index for MCP retrieval
python3 "$CHECKPOINT_SCRIPT" generate-search-index
```

## Language policy

- Detect the user's language from their message and respond in the same language.
- If the user explicitly requests a language, follow it.

## Directory layout

```
.analysis/
├── RESUME.md              ← resume pointer (git-tracked)
├── AI_CONTEXT.md          ← AI discovery file (git-tracked)
├── cache/                 ← search index cache (git-ignored)
│   └── source-analyzer-search/
│       ├── search-documents.jsonl
│       ├── chunk-manifest.json
│       ├── file-to-chunks.json
│       ├── output-to-chunks.json
│       └── index-metadata.json
├── outputs/               ← published stable outputs (git-tracked)
│   ├── overview.md
│   ├── architecture.md
│   ├── technologies.md
│   ├── glossary.md
│   ├── tutorial.md
│   ├── clone-coding.md
│   ├── implementation-checklist.md
│   ├── issue-candidates.md
│   ├── overhaul-<scope>.md
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
- `cache/` contains search indexes for MCP retrieval and should be in `.gitignore`.
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

1. Decide the mode: `analyze`, `refactor-guide`, or `overhaul`.
2. Capture the current commit: `COMMIT=$(git rev-parse HEAD)`.
3. Start or resume a session: pass `--commit "$COMMIT"` to init.
4. If resuming, run `sync` to detect new commits and update the frontier.
5. Use `git ls-tree -r HEAD --name-only -- <scope>` to enumerate files (committed files only).
6. Filter out files matching exclude patterns (see Constraints).
7. Traverse first-party source with BFS in small chunks.
8. Update `.analysis/sessions/<session-id>/outputs/` after each chunk.
9. Write a checkpoint after each chunk (must include at least one of: visited-add, outputs, summary, or next-actions).
10. On `paused` or `completed` checkpoint, outputs are auto-published to `.analysis/outputs/`.

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
- Search index cache: auto-generated when outputs are published on `paused` or `completed` checkpoints, and can also be rebuilt manually via `python3 "$CHECKPOINT_SCRIPT" generate-search-index`. Files are stored under `.analysis/cache/source-analyzer-search/`.

## Refactor-guide mode

- Goal: produce actionable work orders with `DUP-*`, `SEC-*`, and `TIDY-*` codes.
- Follow [refactor-template.md](../../references/refactor-template.md) exactly.
- For each issue include evidence, completion criteria, and test criteria.
- Check security references first, then fall back to [security-triage-checklist.md](../../references/security-triage-checklist.md).
- Output: `.analysis/sessions/<session-id>/outputs/refactor-<scope>.md` (published to `.analysis/outputs/` on pause/complete).

### Starting from issue-candidates

When `issue-candidates.md` exists (from a prior analyze session):

1. Read `.analysis/outputs/issue-candidates.md` first.
2. Use each candidate as the seed for a WO — copy the issue code, module, and evidence into the WO's `Source Issue` field.
3. Expand each candidate with full analysis: read the actual source files, verify the issue, and fill all required WO fields.
4. Remove candidates that turn out to be false positives and note the reason.

### Starting from scratch

When no `issue-candidates.md` exists, perform BFS analysis in refactor-guide mode directly and produce WOs as you discover issues.

## Overhaul mode

- Goal: produce a system overhaul proposal that identifies architectural flaws, unnecessary features, and over-engineering, then proposes a redesigned architecture — even if it breaks backward compatibility.
- Follow [overhaul-template.md](../../references/overhaul-template.md) exactly.
- Issue classification codes:
  - `ARCH-*`: architectural design flaws — incorrect layer separation, circular dependencies, mixed responsibilities, wrong abstraction boundaries.
  - `DEAD-*`: unnecessary features/code — unused modules, obsolete features, legacy compatibility layers.
  - `OVER-*`: over-engineering — unnecessary abstractions, excessive configurability, premature optimization.
  - `DEBT-*`: accumulated technical debt — outdated patterns, deprecated API usage, inconsistent conventions.
- Output: `.analysis/sessions/<session-id>/outputs/overhaul-<scope>.md` (published to `.analysis/outputs/` on pause/complete).
- Each work order (OH-NNN) must include: current state, target state, migration path, instructions, completion criteria, and test criteria.
- Every breaking change must have a documented migration path or an explicit "clean reimplementation" justification.

### Starting from analyze outputs

When analyze outputs exist (from a prior analyze session):

1. Read `.analysis/outputs/architecture.md`, `module-map.json`, and `dependency-graph.json` first.
2. Read `issue-candidates.md` if available — `DUP-*`/`SEC-*`/`TIDY-*` issues that indicate deeper architectural problems feed into `ARCH-*`/`DEBT-*` classifications.
3. Diagnose root problems at the architecture level, not individual code-level symptoms.
4. Design the target architecture based on the diagnosis.
5. Produce OH work orders for the transition.

### Starting from scratch

When no analyze outputs exist, perform BFS analysis in overhaul mode directly: first build an architectural understanding, then diagnose and propose redesign.

### Execution order principles

1. **Remove first**: eliminate unnecessary code/features to reduce scope before redesigning.
2. **Foundation first**: redesign core architecture before adjusting dependent modules.
3. **Verify per phase**: run full tests after each phase completes.

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
3. Search index generation happens automatically on publish. If this analysis was completed before the MCP cache existed, or if you need to rebuild it, run `python3 "$CHECKPOINT_SCRIPT" generate-search-index`.
4. Write `.analysis/AI_CONTEXT.md` with the following structure:

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

If none of these files exist, create `CLAUDE.md` with the block above and inform the user.

## Search MCP integration

- When the bundled `source-analyzer-search` MCP server is enabled, prefer MCP tools/resources over reopening every analysis file manually.
- Build or refresh the cache with:
  ```bash
  python3 "$CHECKPOINT_SCRIPT" generate-search-index
  ```
- If the cache is missing, the MCP server may fall back to direct scanning of `.analysis/outputs/` and checkpoints.
- MCP resource examples:
  - `analysis://overview`
  - `analysis://architecture`
  - `analysis://module-map`
  - `analysis://modules/<name>`
- MCP tool examples:
  - `analysis.search`
  - `analysis.get_module`
  - `analysis.trace_dependencies`
  - `analysis.get_issue_candidates`

## Publishing to GitHub Wiki

After analysis is complete (or paused), publish the outputs to the project's GitHub wiki:

```bash
PUBLISH_SCRIPT="${CLAUDE_PLUGIN_ROOT}/scripts/publish_wiki.sh"
# Publish latest session outputs
bash "$PUBLISH_SCRIPT"
# Publish a specific session
bash "$PUBLISH_SCRIPT" --session-id analyze-20260308-120027
# Dry-run: prepare wiki pages locally without pushing
bash "$PUBLISH_SCRIPT" --dry-run
```

Prerequisites:
- The GitHub wiki must be enabled for the repository (Settings > Features > Wikis).
- At least one page must exist in the wiki (create it via the GitHub UI first).
- The script uses the current directory as the project root by default. Use `--project-dir <path>` to override.

The script generates:
- Ordered wiki pages from analysis outputs (overview, architecture, etc.).
- Per-module pages with `module-` prefix.
- A `Home.md` with document and module tables.
- A `_Sidebar.md` for navigation.

## Setup MCP server (`--setup-mcp`)

When the user runs `/code-workflow:source-analyzer --setup-mcp`, install the `source-analyzer-search` MCP server into the current project.

### Steps

1. **Find uvx or python3**:
   ```bash
   UVX_PATH=$(which uvx 2>/dev/null) && echo "found uvx: $UVX_PATH"
   PYTHON_PATH=$(which python3 2>/dev/null) && echo "found python3: $PYTHON_PATH"
   ```

2. **Choose strategy** (prefer uvx, fallback to python3):
   - If `uvx` found: use `uvx --from git+https://github.com/devlikebear/ai-skills#subdirectory=claude-code/plugin/servers/source-analyzer-mcp source-analyzer-search`
   - If only `python3` found: use `python3 ${CLAUDE_PLUGIN_ROOT}/servers/source-analyzer-mcp/server.py`

3. **Test the server starts**:
   ```bash
   echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' | python3 -c "
   import json,sys
   msg=json.dumps(json.loads(sys.stdin.read())).encode()
   sys.stdout.buffer.write(f'Content-Length: {len(msg)}\r\n\r\n'.encode())
   sys.stdout.buffer.write(msg)
   sys.stdout.buffer.flush()
   " | timeout 5 <CHOSEN_COMMAND> 2>&1
   ```
   Verify the response contains `"serverInfo"`.

4. **Register via `claude mcp add`** using the absolute path found in step 1:
   - uvx strategy:
     ```bash
     claude mcp add source-analyzer-search --scope project -- "$UVX_PATH" --from 'git+https://github.com/devlikebear/ai-skills#subdirectory=claude-code/plugin/servers/source-analyzer-mcp' source-analyzer-search
     ```
   - python3 strategy:
     ```bash
     claude mcp add source-analyzer-search --scope project -- "$PYTHON_PATH" "${CLAUDE_PLUGIN_ROOT}/servers/source-analyzer-mcp/server.py"
     ```

5. **Verify** the `.mcp.json` was created in the project root and report success.

6. **Generate search index** if `.analysis/outputs/` exists:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint_manager.py" generate-search-index
   ```

After setup, tell the user to run `/mcp` to connect. The MCP server will be project-scoped and use absolute paths that work on their machine.

## Constraints

- Never modify analyzed source files.
- Update only `.analysis/` outputs while running this skill.
- Only analyze files committed to git (`git ls-tree -r HEAD --name-only`). Ignore uncommitted/unstaged changes.
- Exclude non-source paths by default: `.analysis/`, `.codex/`, `.claude/`, `.git/`, `vendor/`, `node_modules/`, `.venv/`, `__pycache__/`, `dist/`, `build/`. Pass `--exclude` to add more patterns.
- Every checkpoint must contain at least one of: visited files, output files, summary text, or next actions. Empty checkpoints are rejected.
