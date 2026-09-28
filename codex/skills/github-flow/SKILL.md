---
name: github-flow
description: "Run the full GitHub Flow lifecycle: branch → develop → PR → merge → release. Use when starting a new feature, bugfix, or refactor that follows GitHub Flow conventions, or when resuming any phase of an in-progress flow."
---

# GitHub Flow

## Load only what you need

- `shared/references/github-flow-checklist.md`: phase-by-phase checklist.

## Language policy

- Respond in the same language the user writes in.
- If the user explicitly requests a language, follow it.

## Overview

```
main → [feature branch] → commits → PR → merge → main → [tag/release]
```

Call this skill at any phase. If no phase is specified, start from Phase 1. Complete
only the phase the user requested; never infer permission to push, open a PR, merge,
or publish a release from an earlier phase.

---

## Phase 1 — Branch

1. Inspect the current branch and working tree before checkout, pull, or cleanup:
   ```bash
   git status --short --branch
   ```
   - Preserve all tracked and untracked user changes.
   - If the tree is dirty, do not checkout, pull, reset, or clean. Determine whether
     a new branch can be created safely from the current state; otherwise stop and
     report the exact conflict.
2. When the tree is clean, confirm the agreed base branch and update it only with a
   fast-forward pull:
   ```bash
   git checkout <base-branch>
   git pull --ff-only
   ```
3. Create a well-named branch:
   - Format: `feat/`, `fix/`, `chore/`, or `refactor/` + lowercase kebab-case
   ```bash
   git checkout -b feat/<short-description>
   ```
4. Report: branch name, base branch, working tree status.

---

## Phase 2 — Develop

For each unit of work, run the inner loop in order:

### 2-1. Scope — work orders
- Split the request into ≤3 bounded work orders (30–90 min each) using the
  `/implement` work-order format. Use the host's built-in planning mode if needed.
- Each work order must include measurable acceptance criteria and verification commands.
- Mark API changes or broad refactors as blocked unless explicitly allowed.

### 2-2. Implement — `/implement`
- Execute one work order at a time.
- Keep the scope to the work order; stop and re-plan if it expands.
- Retry at most 2 times on narrow verification failures.

### 2-3. Review — `/review`
- Diff-review the changes before committing.
- Fix all blocking findings. Do not commit until review passes.

### 2-4. Commit
After the review passes:

1. Stage specific files only:
   ```bash
   git add <specific-files>
   ```
2. Commit with a Conventional Commits message (`feat:`, `fix:`, `chore:`, `refactor:`, `docs:`):
   - Subject: imperative mood, ≤72 characters.
   - Body (optional): explain *why*, not *what*.
   ```bash
   git commit -m "feat: short description"
   ```
3. Retry at most once on hook failure — fix the root cause, never use `--no-verify`.

Repeat 2-1 → 2-4 for each work order.

---

## Phase 3 — Push & Pull Request

1. Push the branch:
   ```bash
   git push -u origin <branch-name>
   ```
2. Create a PR:
   - Title: ≤70 characters, imperative mood.
   - Body: Summary (bullets) + Test plan (checklist).
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

Merge only after CI passes and review is complete.

1. Choose strategy: `--merge` / `--squash` / `--rebase`
2. Merge and delete remote branch:
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

1. Decide new version (SemVer: `patch` / `minor` / `major`).
2. Ensure version files and `CHANGELOG.md` are updated and committed on main.
3. Create the GitHub release:
   ```bash
   gh release create v<version> --title "v<version>" --notes "<release notes>"
   ```
4. Report the release URL.

---

## Rules

- Never force-push to `main` or `master`.
- Never use `--no-verify` without explicit user approval.
- Confirm before any destructive action.
- Stage specific files only — avoid secrets and binaries.
- One PR per logical change.
- If work expands beyond scope, stop and re-scope the work orders.
- Treat push, PR creation, merge, branch deletion, tag creation, and release
  publication as separate externally visible phases that require explicit user intent.

## Output at each phase

- What was done
- Current state: branch name, PR URL, or release URL
- Next suggested phase or command
