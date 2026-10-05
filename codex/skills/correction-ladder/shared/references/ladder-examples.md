# Correction Ladder Examples

Each example names the mistake, the rung chosen, and why the rungs above it
were not used.

## Rung 1: make it impossible

- **Mistake:** handlers build SQL with string concatenation.
  **Fix:** remove raw query access from the handler layer; expose only a query
  builder that takes bound parameters.
- **Mistake:** a feature flag is read with a typo'd string key and silently
  defaults to off.
  **Fix:** replace string keys with a generated enum of flag names so an unknown
  key cannot be written.
- **Mistake:** two services each format money differently.
  **Fix:** one `Money` value type with a single `format()`; delete the others.

## Rung 2: compiler or analyzer

- **Mistake:** a new status value is added but one `switch` forgets it.
  **Fix:** exhaustive matching (`never` check, sealed class, `match` with no
  wildcard) so the build fails. A code change is not needed beyond the check.
- **Mistake:** API responses drift from the client types.
  **Fix:** generate client types from the schema and fail CI on a diff.

## Rung 3: lint or review-bot rule

- **Mistake:** code imports the deprecated `http` wrapper instead of `apiClient`.
  **Fix:** banned-import lint rule whose message says "use `apiClient` from
  `src/net`". Rung 1 rejected: the old wrapper still serves a legacy module
  scheduled for removal.
- **Mistake:** tests sleep for fixed durations.
  **Fix:** a CI grep for `sleep(` under `tests/` with an allowlist file.

## Rung 4: skill

- **Mistake:** agents write migration files that are not reversible.
  **Fix:** a short skill section loaded for migration tasks that requires a
  `down` step and a dry run. Rung 2/3 rejected: reversibility depends on
  intent, which a pattern match cannot judge; a test still covers the syntax.

## Rung 5: style guide

- **Mistake:** error messages alternate between "Unable to" and "Couldn't".
  **Fix:** one style-guide line choosing a voice. Higher rungs rejected: the
  cost of a rule outweighs the benefit, and reviewers can enforce it cheaply.

## Common misplacements

- Adding "always remember to validate input" to agent instructions when a
  schema validator at the boundary would enforce it (should be rung 1 or 2).
- A lint rule that matches on a function name that is also used legitimately,
  producing noise until someone disables it (narrow it or move to rung 1).
- A comment above the dangerous function saying "do not call directly" instead
  of making it private (rung 1).
