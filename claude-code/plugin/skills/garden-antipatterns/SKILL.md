---
name: garden-antipatterns
description: "Remove workarounds, duplicate code paths, and stale comments that justify hacks before agents copy them elsewhere, then keep one paved path and add a check that blocks reintroduction. Use when you notice a workaround, a second way of doing the same thing, or a comment explaining why a hack is acceptable while implementing, reviewing, or refactoring. Do not select for behavior-preserving refactors with no antipattern involved or for broad cleanup without a specific pattern."
---

# Garden Antipatterns

Coding agents imitate the code around them. One workaround left in place reads
as precedent, and the next change copies it into three more files. Treat each
workaround you notice as something that will spread unless you remove it and
make the right way the obvious way.

Respond in the same language the user writes in. Detect the user's language
from the current conversation; retain technical identifiers as written.

Inspired by Lauren Tan (@poteto), "here's how i shipped 2,500 PRs last month to production": https://x.com/poteto/status/2102050467505430555

## Load only what you need

- [reintroduction checks](../../references/garden-antipatterns/references/reintroduction-checks.md): ways
  to block a removed pattern from coming back, from cheapest to strongest.

## What to look for

- **Workarounds:** retries around a race, `sleep` to wait for state, catching
  and ignoring an error, casting away a type, copying data to dodge a shared
  mutable object.
- **Duplicate paths:** two helpers, clients, or components that do the same job;
  a "v2" next to a "v1" that was never retired; a local reimplementation of a
  shared utility.
- **Comments that invite band-aids:** notes such as "temporary fix", "hack
  until X lands", "don't touch, it breaks Y", or a long paragraph explaining
  why an odd construct is fine. They tell the next reader the shortcut is
  sanctioned. Check whether the referenced reason still holds.
- **Explanatory comments that drift:** comments restating what code did before
  a change, or describing a constraint that was later removed.

## Workflow

1. **Name the pattern.** Write one sentence describing the workaround and the
   intended paved path (the single way it should be done).
2. **Measure the spread.** Search the repository for every copy (`rg` the call,
   the comment text, and close variants). Note how many exist and where.
3. **Find the root cause.** Ask why the workaround was needed. If the reason is
   gone (the bug was fixed upstream, the dependency was upgraded, the feature
   was removed), the workaround is dead weight. If the reason is real, fix it at
   the source when the change is small.
4. **Choose the paved path.** Keep exactly one implementation. Prefer the
   existing shared module; delete or redirect the others. Make the paved path
   easy to discover (clear name, single export, mention in agent instructions
   if needed).
5. **Remove the copies.** Migrate each call site to the paved path. If the
   migration is too large for the current task, fix the instance you touched,
   leave the rest tracked in a follow-up work order, and still add the check
   in step 6 with an allowlist of the remaining sites.
6. **Block reintroduction.** Add the strongest practical check from the
   reintroduction reference (type, lint rule, banned import, CI grep with
   allowlist). Show it failing on a sample of the old pattern.
7. **Fix the comments.** Delete comments whose justification no longer holds.
   Rewrite a still-valid comment to state the constraint and the correct
   approach, not to excuse the shortcut. Link an issue instead of describing a
   future fix in prose.

## Rules

- Do not add a new workaround to fix a symptom caused by an old one.
- Do not leave a second path "for compatibility" without an owner and a removal
  check (allowlist or deprecation lint).
- Keep behavior identical unless the workaround was hiding a bug; if behavior
  changes, say so and verify it.
- Stay within the task's scope; large migrations become follow-up work orders.
- Run the project's tests and the new check before reporting done.

## Done when

- One paved path remains for the pattern you addressed, or remaining copies are
  allowlisted and tracked.
- A check exists that fails when the old pattern is added again.
- Comments that justified the removed hack are gone or rewritten.
- Tests and the new check pass.

## Final output

- Pattern removed and the paved path kept
- Root cause and how it was resolved
- Call sites migrated and any tracked remainder
- Reintroduction check added and proof it fails on the old pattern
- Comments deleted or rewritten
