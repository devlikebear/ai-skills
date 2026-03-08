---
name: implement
description: "Execute an approved work order directly with small, test-proven code changes. Use this English-default variant when users call `/implement`, move from planning into implementation, or want Codex to make the code changes itself."
---

# Implement

This is the English-default variant of `implement`.

## Load only what you need

- `shared/references/work-order.md`: required work-order format.

## Language policy

- Write responses in English by default.
- If the user explicitly requests another language policy, follow it.

## Workflow

1. Restate the implementation goal in 1-2 sentences.
2. Confirm or rewrite the work order using `shared/references/work-order.md`.
3. Keep the scope to one work unit, 30-90 minutes, and at most 5 touch points.
4. Implement the work directly.
5. Retry at most 2 times if verification fails for a narrow, local reason.
6. Stop and report if the task expands into a larger redesign or refactor.

## Rules

- Prefer minimal changes that satisfy the work order.
- Treat non-goals as hard constraints.
- Run the listed verification commands.
- If tests do not exist, use the best available build/lint/runtime validation and say so.
- If the task turns into a review or refactor, hand off to `/review` or `/refactor`.

## Final output

- Completed work summary
- Changed files
- Verification results
- Remaining risks or follow-up
