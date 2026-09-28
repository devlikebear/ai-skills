# Existing-product extensions

Use the provided checkout and read its instructions first. Ask for a location
only when none is available and inspecting source would change the plan.

1. Inspect Git status and distinguish committed behavior from unfinished changes.
   Do not edit source or discard work while planning.
2. Look for `.analysis/AI_CONTEXT.md`, relevant `.analysis/outputs/`, and existing
   plans under `docs/plans/`. Treat them as navigation aids until verified.
3. Check recorded commit/session, referenced files, Git changes since the analysis
   when available, and current relevant symbols. A recent mtime does not establish
   freshness. For missing revision metadata, verify the relevant claims directly.
4. Read README, dependency manifests and test/build configuration just enough to
   identify the runtime, entry points, and verification commands. Then inspect
   only the feature's affected modules, analogous behavior, tests, and callers.
5. Record reusable patterns with actual file paths and symbols, constraints,
   existing behavior, relevant WIP, and which assumptions remain unverified.

Separate the user's intended future behavior from observed current behavior.
When they differ, explain the difference rather than dismissing either source.
Do not prescribe a nonexistent helper or repeat functionality already present.
A plan should distinguish inspected files from proposed additions.

Reuse `source-analyzer` output if available and fresh enough for the affected
area. The planning skill does not require that skill or MCP installation, and
does not launch a whole-repository analysis for a narrow feature. Architecture
analysis alone remains the source-analyzer workflow.

If code cannot be accessed, produce the useful product-level plan with an
explicit evidence gap. Mark implementation paths and commands as provisional;
do not claim that repository conventions were checked. For continuation, refresh
only affected assumptions and preserve prior product decisions.
