# Reintroduction Checks

After removing a workaround or duplicate path, add the strongest check the
project can support. Each option below lists when it fits and a minimal shape.

## 1. Remove the capability

Delete or make private the API the workaround depended on. Nothing to lint if
the bad call no longer compiles.

## 2. Types and contract tests

- Narrow a parameter type so the hack (for example passing `any` or a raw
  string) is rejected.
- Add a test that asserts there is exactly one implementation, such as a test
  that lists modules exporting a given symbol and expects one entry.

## 3. Lint rules

- Banned imports or modules (`no-restricted-imports`, `ruff` banned-api,
  `depguard`, `forbiddenApis`).
- Banned call patterns via AST rules (`no-restricted-syntax`, Semgrep,
  custom rule).
- The message must name the paved path, for example
  `"Use fetchJson from src/net/client instead of raw fetch."`

## 4. CI grep with allowlist

Cheapest option when no linter is available. Keep remaining legacy sites in an
allowlist file that may only shrink.

```bash
#!/usr/bin/env bash
# scripts/check-no-sleep-in-tests.sh
set -euo pipefail
pattern='time\.sleep\('
allowlist='scripts/allowlists/sleep-in-tests.txt'
violations=$(rg -l "$pattern" tests/ | sort | comm -23 - <(sort "$allowlist") || true)
if [[ -n "$violations" ]]; then
  echo "Fixed sleeps found; wait on a condition with wait_until() instead:" >&2
  echo "$violations" >&2
  exit 1
fi
```

## 5. Comment hygiene checks

- Flag comments that contain markers like `HACK`, `temporary`, or
  `workaround` without an issue link, for example by a grep that requires a
  URL or issue number on the same line.
- When a workaround is removed, search for its explanatory comment text in
  other files; copies of the comment usually mark copies of the hack.

## Prove the check works

1. Temporarily add one instance of the old pattern.
2. Run the check and confirm it fails with the intended message.
3. Revert the sample and confirm the check passes.
