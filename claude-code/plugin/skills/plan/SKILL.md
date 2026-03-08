---
name: plan
description: "Turn a request into executable work orders. Use when users ask for planning before implementation or need a request split into small verifiable tasks."
---

# Plan

## References

- [work-order.md](../../references/work-order.md): required work-order structure.

## Language policy

- Detect the user's language from their message and respond in the same language.
- If the user explicitly requests a language, follow it.

## Workflow

1. Read the request and list explicit constraints.
2. Split the work into at most 3 work orders.
3. Keep each work order to 30-90 minutes and at most 5 touch points.
4. Write measurable acceptance criteria.
5. Include verification commands in every work order.
6. Mark API changes or broad refactors as blocked unless explicitly allowed.

## Output

- A short planning summary
- Work Order 1
- Work Order 2 (optional)
- Work Order 3 (optional)
- Suggested next step: `/code-workflow:implement`
