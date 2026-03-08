---
name: refactor
description: "Perform safe, test-driven refactoring without behavior changes. Use when users ask for structure cleanup or want duplication and technical debt reduced."
---

# Refactor

## References

- [refactor-work-order.md](../../references/refactor-work-order.md): refactoring work-order format.
- [refactoring-checklist.md](../../references/refactoring-checklist.md): safety checklist.
- [refactoring-patterns.md](../../references/refactoring-patterns.md): pattern selection guide.

## Language policy

- Detect the user's language from their message and respond in the same language.
- If the user explicitly requests a language, follow it.

## Workflow

1. Analyze the current state and existing tests.
2. Confirm a behavior-preserving goal and strict non-goals.
3. Limit the change to one refactoring pattern at a time.
4. Keep the touch points to at most 5 files.
5. Run tests before and after each step.
6. Stop immediately if behavior changes or scope expands into new feature work.

## Safety rules

- No feature changes.
- No public API changes unless explicitly approved.
- No large formatting-only diffs.
- Always summarize verification results.
