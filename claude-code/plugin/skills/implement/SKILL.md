---
name: implement
description: "Execute an approved work order directly with small, test-proven code changes. Use when users move from planning into implementation or want Claude to make code changes."
---

# Implement

## References

- [work-order.md](../../references/work-order.md): required work-order format.

## Language policy

- Detect the user's language from their message and respond in the same language.
- If the user explicitly requests a language, follow it.

## Workflow

1. Restate the implementation goal in 1-2 sentences.
2. Confirm or rewrite the work order using the [work-order template](../../references/work-order.md).
3. Keep the scope to one work unit, 30-90 minutes, and at most 5 touch points.
4. Implement the work directly.
5. Retry at most 2 times if verification fails for a narrow, local reason.
6. Stop and report if the task expands into a larger redesign or refactor.

## Rules

- Prefer minimal changes that satisfy the work order.
- Treat non-goals as hard constraints.
- Run the listed verification commands.
- If tests do not exist, use the best available build/lint/runtime validation and say so.
- If the task turns into a review or refactor, hand off to `/code-workflow:review` or `/code-workflow:refactor`.

## Final output

- Completed work summary
- Changed files
- Verification results
- Remaining risks or follow-up
