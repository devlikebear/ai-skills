---
name: plan
description: "Turn a request into executable work orders. Use this English-default variant when users ask for planning before implementation, call `/plan`, or need a request split into small verifiable tasks."
---

# Plan

This is the English-default variant of `plan`.

## Load only what you need

- [work-order.md](../shared/references/work-order.md): required work-order structure.

## Language policy

- Write responses in English by default.
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
