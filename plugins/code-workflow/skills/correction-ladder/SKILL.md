---
name: correction-ladder
description: "Choose the strongest durable place to fix a mistake found in agent or human code so it cannot recur, preferring architecture changes, then type and static checks, lint or review-bot rules, a skill, and style-guide prose only as a last resort. Use when you spot a repeated or preventable error during implementation or review and need to decide how to prevent it. Do not select for fixing a one-off bug with no prevention step or for routine diff review."
---

# Correction Ladder

Fixing one instance of a mistake helps once. Agents and teammates repeat what
the codebase allows, so every correction should also ask: where can this be
stopped automatically next time? Climb the ladder from the top and stop at the
first rung that can realistically hold the fix.

Respond in the same language the user writes in. Detect the user's language
from the current conversation; retain technical identifiers as written.

Inspired by Lauren Tan (@poteto), "here's how i shipped 2,500 PRs last month to production": https://x.com/poteto/status/2102050467505430555

## Load only what you need

- [ladder examples](shared/references/ladder-examples.md): worked examples for
  each rung and common misplacements.

## The ladder (strongest first)

1. **Make it impossible.** Change the code or architecture so the wrong thing
   cannot be expressed: remove the unsafe API, wrap it behind one safe entry
   point, make invalid states unrepresentable, move the concern into a shared
   module that every caller must go through.
2. **Make the compiler or analyzer reject it.** Types, schemas, exhaustiveness
   checks, `strict` modes, static analysis queries, or a contract test that
   fails the build.
3. **Make a lint or review-bot rule flag it.** Custom lint rules, banned-import
   lists, grep-based CI checks, or automated review rules with a message that
   names the correct alternative.
4. **Teach it in a skill.** Agent-facing instructions for judgment calls that
   tools cannot detect, loaded when the relevant task comes up.
5. **Write it in the style guide.** Prose for humans. Use only when nothing
   above applies, because only a careful reviewer will enforce it.

Lower rungs are allowed as a complement (for example a skill that explains the
new type), never as a replacement for a reachable higher rung.

## Decision checklist

Answer in order; the first "yes" picks the rung.

- [ ] Can a code or API change remove the possibility of this mistake without
      disproportionate churn? → rung 1
- [ ] Can a type, schema, or test detect it deterministically at build time?
      → rung 2
- [ ] Can a pattern match (AST rule, regex, import ban) detect it with few
      false positives? → rung 3
- [ ] Is it a judgment call an agent must make during a specific kind of task?
      → rung 4
- [ ] Otherwise → rung 5, and note why higher rungs did not fit.

Then confirm:

- [ ] The fix also corrects the existing instances, not just future ones.
- [ ] The check fails on a sample of the original mistake (prove it bites).
- [ ] The error message or doc points to the correct alternative.

## Workflow

1. State the mistake in one sentence and find every existing instance
   (`rg` for the pattern, not just the file you were looking at).
2. Classify why it happened: missing abstraction, weak types, no check, missing
   context, or genuine taste.
3. Walk the checklist and pick a rung. Write down why higher rungs were rejected.
4. Implement the prevention and fix the existing instances in the same change
   when the scope is small; otherwise fix the instances first and propose the
   prevention as a follow-up work order.
5. Demonstrate the prevention: reintroduce the mistake locally and show the
   build, lint, or test failing, then revert.
6. If the fix is a skill or style-guide entry, keep it to a few lines with one
   example of right and wrong.

## Rules

- Do not answer a structural problem with a reminder in prose.
- Keep new checks narrow; a noisy rule gets disabled and protects nothing.
- Prefer extending an existing rule or type over adding a parallel mechanism.
- Ask before large architectural changes; propose them with the evidence.

## Done when

- Existing instances are fixed or tracked.
- The chosen rung is in place and shown to catch the original mistake.
- The reason for the chosen rung (and rejected higher rungs) is recorded in the
  PR description or final report.

## Final output

- Mistake and root cause
- Chosen rung and why higher rungs did not fit
- Prevention added and proof that it fails on the bad pattern
- Instances fixed and any follow-up
