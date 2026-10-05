---
name: verify-own-work
description: "Prove a change works by running the real app, CLI, or service yourself and capturing evidence before reporting it done. Use when finishing a feature or bug fix, when a vague bug report needs a concrete reproduction, or when a project needs a feature map describing how to drive its screens, commands, shortcuts, and endpoints. Do not select for diff-only code review, static architecture analysis, or questions that require no code change."
---

# Verify Own Work

Passing unit tests and a clean diff are not proof that a change works. Before
calling anything finished, drive the actual software the way a user would,
keep what you observed, and compare it against the project's feature map.

Respond in the same language the user writes in. Detect the user's language
from the current conversation; retain technical identifiers as written.

Inspired by Lauren Tan (@poteto), "here's how i shipped 2,500 PRs last month to production": https://x.com/poteto/status/2102050467505430555

## Load only what you need

- [feature-map template](shared/references/feature-map.md): file layout and
  entry format for a project's feature map.

## The rule

A task is "done" only when you can point to evidence produced by running the
changed behavior after the last edit. "It compiles", "tests pass", or "it
should work" are inputs to verification, not substitutes for it. If you cannot
run the software, say exactly what you could not verify and why; never imply
otherwise.

## Workflow

1. **Find the feature map.** Look for `docs/feature-map.md` or the location
   named in the project's agent instructions. If none exists and the task
   touches user-visible behavior, create a minimal one (step 2).
2. **Build or update the map.** Record only entries relevant to the task, using
   the template. Each entry names the surface (screen, command, shortcut,
   endpoint, job), how to reach it, how to drive it, and what a healthy result
   looks like. Discover entries from routes, CLI parsers, keybinding tables, and
   menus rather than from memory. Remove entries for things that no longer exist.
3. **Turn the report into a reproduction.** For a bug or vague request, map each
   noun in the report to a feature-map entry, then write numbered steps with an
   expected and an actual result. Run them before changing code and confirm you
   see the failure. If you cannot reproduce it, report what you tried and stop
   guessing; ask for the missing detail instead.
4. **Make the change.** Keep the reproduction steps at hand; they become the
   acceptance check.
5. **Run the real thing.** Start the app, service, or CLI from the working tree
   (dev server, built binary, container, simulator). Replay the reproduction and
   exercise the neighboring entries in the map that share code with the change.
6. **Capture evidence.** Save artifacts that a reviewer can inspect without
   rerunning anything:
   - command lines with their exit codes and relevant output
   - log or trace excerpts covering the request path
   - screenshots or short recordings for UI changes
   - HTTP request/response pairs for endpoints
   Store them where the project keeps such artifacts, or in a scratch directory
   that is not committed, and reference them in your report.
7. **Compare against the map.** Check each touched entry's "healthy result".
   Update an entry when the change intentionally altered how it is driven or
   what it shows.

## Rules

- Verify after the final edit; evidence from an earlier build does not count.
- Prefer driving the software through its public surface (UI, CLI, API) over
  calling internals directly.
- Never fake evidence, crop away errors, or summarize output you did not see.
- Keep the feature map short and factual; it is an index for driving the app,
  not documentation of its internals.
- Do not start services that touch production data, send real messages, or
  spend money without explicit permission; use local or sandboxed targets.
- When verification needs a tool you lack (browser automation, device,
  credentials), state the gap and the closest check you did run.

## Done when

- The reproduction (or acceptance steps) passes against the running software.
- Evidence for each acceptance step is captured and referenced.
- Feature-map entries touched by the change are accurate.
- Anything unverified is listed explicitly with the reason.

## Final output

- What was verified and how (commands, URLs, screens)
- Evidence locations or inline excerpts
- Feature-map changes
- Unverified items and remaining risks
