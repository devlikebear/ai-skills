---
name: plan-for-codex
description: "Turn a request into executable work orders for Codex. Use this Korean-default variant when users ask for planning before implementation, call `/plan`, or need a request split into small verifiable tasks."
---

# Plan

This is the Korean-default variant of `plan-for-codex`.

## Load only what you need

- `shared/references/work-order.md`: required work-order structure.

## Language policy

- Write responses in Korean by default.
- If the user explicitly requests another language policy, follow it.

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
- Suggested next step: `/implement`
