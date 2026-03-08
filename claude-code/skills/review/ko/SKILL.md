---
name: review
description: "Review code changes for regressions, security issues, and missing tests. Use this Korean-default variant when users call `/review`, ask for a diff review, or need concrete fix guidance after implementation."
---

# Review

This is the Korean-default variant of `review`.

## Load only what you need

- [review-checklist.md](../shared/references/review-checklist.md): review checklist.
- [work-order.md](../shared/references/work-order.md): fix work-order template when changes are required.

## Language policy

- Write responses in Korean by default.
- If the user explicitly requests another language policy, follow it.

## Workflow

1. Review findings first, ordered by severity.
2. Focus on regressions, security issues, and missing tests.
3. Include exact file and line references when reporting issues.
4. If fixes are needed, generate a concrete work order using the [work-order template](../shared/references/work-order.md).
5. Keep summaries brief after the findings.

## Output

- Verdict: OK / Needs changes / Blocking
- Findings with file and line references
- Optional improvement notes
- Fix work order when required
