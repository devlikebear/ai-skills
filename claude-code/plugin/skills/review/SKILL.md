---
name: review
description: "Diff-based code review for regressions, security issues, and missing tests. Use when users ask for a code review, diff review, or need concrete fix guidance after implementation."
---

# Review

## References

- [review-checklist.md](../../references/review-checklist.md): review checklist.
- [work-order.md](../../references/work-order.md): fix work-order template when changes are required.

## Language policy

- Detect the user's language from their message and respond in the same language.
- If the user explicitly requests a language, follow it.

## Workflow

1. Review findings first, ordered by severity.
2. Focus on regressions, security issues, and missing tests.
3. Include exact file and line references when reporting issues.
4. If fixes are needed, generate a concrete work order using the [work-order template](../../references/work-order.md).
5. Keep summaries brief after the findings.

## Output

- Verdict: OK / Needs changes / Blocking
- Findings with file and line references
- Optional improvement notes
- Fix work order when required
