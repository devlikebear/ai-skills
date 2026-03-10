# GitHub Flow Checklist

## Phase 1 — Branch

- [ ] On `main` (or the agreed base branch) and fully synced (`git pull`)
- [ ] Branch name follows convention: `feat/`, `fix/`, `chore/`, or `refactor/`
- [ ] Branch name is lowercase kebab-case
- [ ] Working tree is clean before branching

## Phase 2 — Develop

- [ ] `/plan-for-codex` run — work orders are bounded and have acceptance criteria
- [ ] `/implement` run per work order — scope held to the work order
- [ ] `/review` run after each implementation — all blocking findings fixed
- [ ] Only relevant files staged (no secrets, binaries, or generated files)
- [ ] Commit message follows Conventional Commits format
- [ ] Commit subject ≤72 characters, imperative mood
- [ ] Pre-commit hooks pass without `--no-verify`

## Phase 3 — Pull Request

- [ ] Branch pushed to remote
- [ ] PR title is concise (≤70 chars) and imperative
- [ ] PR body contains **Summary** and **Test plan** sections
- [ ] PR linked to relevant issues if applicable

## Phase 4 — Merge

- [ ] CI passes
- [ ] Code review complete
- [ ] Merge strategy chosen (`merge` / `squash` / `rebase`)
- [ ] Remote branch deleted after merge
- [ ] Local main synced after merge

## Phase 5 — Release (optional)

- [ ] Version bumped in all version files
- [ ] `CHANGELOG.md` updated with the new version entry
- [ ] Version bump commit is on `main`
- [ ] GitHub release created with meaningful notes
- [ ] Release URL confirmed
