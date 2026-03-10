---
name: review
description: "Review code changes for regressions, security issues, and missing tests. Use when users call `/review`, ask for a diff review, or need concrete fix guidance after implementation."
---

# Review

## Load only what you need

- `shared/references/review-checklist.md`: review checklist.
- `shared/references/work-order.md`: fix work-order template when changes are required.

## Language policy

- Respond in the same language the user writes in.
- If the user explicitly requests a language, follow it.

## Workflow

1. Review findings first, ordered by severity.
2. Focus on regressions, security issues, and missing tests.
3. Include exact file and line references when reporting issues.
4. If fixes are needed, generate a concrete work order using `shared/references/work-order.md`.
5. Keep summaries brief after the findings.

## Output

- Verdict: OK / Needs changes / Blocking
- Findings with file and line references
- Optional improvement notes
- Fix work order when required
