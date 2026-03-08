# Refactoring Checklist

## Before

- [ ] The current behavior is understood.
- [ ] Existing tests or validation commands are identified.
- [ ] The scope is limited to at most 5 files.

## During

- [ ] Apply one refactoring pattern at a time.
- [ ] Avoid feature changes.
- [ ] Avoid large formatting-only diffs.

## After

- [ ] Re-run verification commands.
- [ ] Inspect the diff for unintended changes.
- [ ] Confirm public APIs are unchanged unless explicitly approved.
