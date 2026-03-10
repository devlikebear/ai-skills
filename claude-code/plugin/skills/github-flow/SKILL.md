---
name: github-flow
description: "Run the full GitHub Flow lifecycle: branch → develop → PR → merge → release. Use when starting a new feature, bugfix, or refactor that follows GitHub Flow conventions, or when resuming any phase of an in-progress flow."
---

# GitHub Flow

## Language policy

- Detect the user's language from their message and respond in the same language.
- If the user explicitly requests a language, follow it.

## References

- [github-flow-checklist.md](../../references/github-flow-checklist.md): phase-by-phase checklist.

## Overview

```
main → [feature branch] → commits → PR → merge → main → [tag/release]
```

Call this skill at any phase. If no phase is specified, start from Phase 1.
State the current phase or describe where you are to resume mid-flow.

---

## Phase 1 — Branch

1. Confirm you are on `main` (or the agreed base branch) and it is up to date:
   ```bash
   git checkout main && git pull
   ```
2. Create a well-named feature branch:
   - Format: `feat/<short-description>`, `fix/<short-description>`, `chore/<short-description>`, or `refactor/<short-description>`
   - Lowercase kebab-case. No issue numbers unless the project convention requires them.
   ```bash
   git checkout -b feat/<short-description>
   ```
3. Report: branch name, base branch, working tree status.

---

## Phase 2 — Develop

For each unit of work, run the inner loop in order:

### 2-1. Plan — `/code-workflow:plan`
- Split the request into ≤3 bounded work orders (30–90 min each).
- Each work order must include measurable acceptance criteria and verification commands.
- Mark API changes or broad refactors as blocked unless explicitly allowed.

### 2-2. Implement — `/code-workflow:implement`
- Execute one work order at a time.
- Keep the scope to the work order; stop and re-plan if it expands.
- Retry at most 2 times on narrow verification failures.

### 2-3. Review — `/code-workflow:review`
- Diff-review the changes before committing.
- Fix all blocking findings. Do not commit until review passes.

### 2-4. Commit
After the review passes, stage and commit:

1. Stage only the relevant files — never `git add -A` or `git add .` blindly:
   ```bash
   git add <specific-files>
   ```
2. Commit with a Conventional Commits message (`feat:`, `fix:`, `chore:`, `refactor:`, `docs:`):
   - Subject line: imperative mood, ≤72 characters.
   - Body (optional): explain *why*, not *what*.
   ```bash
   git commit -m "feat: short description"
   ```
3. Retry at most once if a pre-commit hook fails; fix the root cause — never use `--no-verify`.

Repeat 2-1 → 2-4 for each work order.

---

## Phase 3 — Push & Pull Request

1. Push the branch:
   ```bash
   git push -u origin <branch-name>
   ```
2. Create a PR with `gh pr create`:
   - **Title**: ≤70 characters, imperative mood.
   - **Body**: Summary (bullet points) + Test plan (checklist).
   ```bash
   gh pr create --title "..." --body "$(cat <<'EOF'
   ## Summary
   - ...

   ## Test plan
   - [ ] ...
   EOF
   )"
   ```
3. Report the PR URL.

---

## Phase 4 — Merge

Merge only after review is complete and CI passes.

1. Choose the merge strategy:
   - `--merge` (default): preserves commit history with a merge commit.
   - `--squash`: collapses all commits into one clean commit.
   - `--rebase`: replays commits for a linear history.
2. Merge and delete the remote branch in one step:
   ```bash
   gh pr merge <number> --<strategy> --delete-branch
   ```
3. Sync local main:
   ```bash
   git checkout main && git pull
   ```
4. Report: merged PR, deleted branch, current HEAD of main.

---

## Phase 5 — Tag & Release (optional)

Run this phase only when publishing a versioned release.

1. Decide the new version using SemVer (`major.minor.patch`):
   - `patch`: backward-compatible bug fixes.
   - `minor`: new backward-compatible feature.
   - `major`: breaking change.
2. Ensure version files (`VERSION.txt`, `package.json`, `pyproject.toml`, etc.) and `CHANGELOG.md` are already updated and committed on main.
3. Create the GitHub release:
   ```bash
   gh release create v<version> --title "v<version>" --notes "<release notes>"
   ```
4. Report the release URL.

---

## Rules

- Never force-push to `main` or `master`.
- Never skip hooks (`--no-verify`) without explicit user approval.
- Always confirm before destructive actions (reset --hard, force-push, branch deletion).
- Stage specific files only — avoid accidentally committing secrets or large binaries.
- One PR per logical change; keep PRs small and reviewable.
- If work expands beyond the original scope, stop and re-run `/code-workflow:plan`.

---

## Output at each phase

- What was done in this phase
- Current state: branch name, PR URL, or release URL
- Next suggested phase or command
