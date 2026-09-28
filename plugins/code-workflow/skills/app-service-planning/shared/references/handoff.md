# Implementation-ready handoff

The plan must convey the product decision and how to verify it, independently
of which coding agent implements it. Do not expand scope to fill a template.

## Choose the smallest useful format

- A cohesive MVP with few dependencies: [single development plan](../templates/dev-plan.md).
- Several independently useful increments, important integration uncertainties,
  or explicit milestone needs: [roadmap](../templates/roadmap.md) plus one
  [phase plan](../templates/phase.md) per useful vertical slice.

Prefer a single file in borderline cases. Explain the choice using dependencies
and validation opportunities, not a rigid feature count or guessed hour total.
Follow a user-specified format. If estimates are requested, state assumptions
and ranges rather than promising a delivery date.

Use a feature prefix, for example `reading-list-dev-plan.md` or
`reading-list-roadmap.md` with `reading-list-phase-1-capture.md`. When saving
into the target repository, follow its documentation location, otherwise use
`docs/plans/`; never write into an unrelated working directory. Fill all
applicable template slots; remove unused sections and placeholder text.

## Connect decisions to tasks

For every MVP item, specify a task or phase, its visible user outcome, and an
acceptance scenario. Write each task as a work order an implementing agent can
take directly: goal, non-goals, at most 5 touch points, steps, acceptance
criteria, and verification commands with expected results. Size each task to
30-90 minutes and split larger ones. Treat plan-level exclusions as non-goals
for every task, and note dependencies and observed patterns.
Label new file paths as proposed. Do not invent existing function signatures,
commands, database schemas, package versions, or test results.

For a new project without a chosen stack, keep tasks at component/behavior level
and record the stack decision as open if it changes implementation. For existing
projects, cite verified source paths and confirmed test/build scripts. Respect
project test-first instructions. Distinguish commands found in configuration
from commands actually executed, and execution from successful verification.

A vertical phase finishes with something the user can try: for a reading list,
phase 1 adds a book and shows the list; phase 2 searches and opens details.
Database-only, backend-only, and UI-only phases delay validation; combine the
necessary layers into user-visible increments where feasible.

## Checkpoints and authority

Each checkpoint states the setup, command or manual action, expected result, and
response to failure. Stop dependent work when its prerequisite check fails;
record the failure and fix within authorized scope before retrying. Independent
work can continue. A passing checkpoint is evidence, not an automatic approval
request. Carry forward the user's requested review cadence.

Document material open product decisions and actions requiring separate authority.
Do not add implementation, external posting, deployment, or purchasing permission
to the handoff. The implementing agent must follow the actual user request and
repository instructions. A planning-only request ends with the requested artifacts.
