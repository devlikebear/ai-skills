# Feature Map Template

A feature map is a small, maintained index of what a project exposes and how an
agent can drive each piece. Keep it in `docs/feature-map.md` unless the project
already names another location, and mention that location in the project's
agent instructions so future sessions find it.

## File layout

```markdown
# Feature Map

How to start: `<command that runs the app locally>`
How to reset state: `<command or steps>`
Last reviewed: YYYY-MM-DD

## <Area name>

### <Surface name>
- Kind: screen | command | shortcut | endpoint | job
- Reach: <URL, menu path, CLI invocation, key chord, or route>
- Drive: <the minimal steps or request that exercises it>
- Healthy result: <what you should observe when it works>
- Evidence: <how to capture proof: screenshot, log line, exit code, response>
- Code: <entry-point file or module, optional>
```

## Example entries

```markdown
### Export report
- Kind: command
- Reach: `app export --format csv <project-id>`
- Drive: run against the seeded fixture project `demo`
- Healthy result: exit code 0, `demo.csv` with a header row and 12 data rows
- Evidence: command output plus `head -3 demo.csv`

### Command palette
- Kind: shortcut
- Reach: Cmd/Ctrl+K from any page
- Drive: open palette, type "theme", press Enter
- Healthy result: theme picker dialog opens with the current theme selected
- Evidence: screenshot of the dialog

### Create invoice
- Kind: endpoint
- Reach: `POST /api/invoices`
- Drive: `curl -s -X POST localhost:3000/api/invoices -d @fixtures/invoice.json`
- Healthy result: HTTP 201 and a JSON body containing `id` and `status: "draft"`
- Evidence: full request and response with status line
```

## Maintenance rules

- Add an entry when you add or change a user-reachable surface.
- Delete entries for removed surfaces in the same change that removes them.
- Prefer fixtures and seeded data that make "healthy result" deterministic.
- Keep each entry under about eight lines; link out for detail.

## From vague report to reproduction

1. Underline every noun and verb in the report ("the export button is broken").
2. Match each to a feature-map entry (`Export report`). If nothing matches, the
   map has a gap or the report refers to something else; ask.
3. Copy the entry's Reach and Drive lines into numbered steps.
4. Add the reporter's specifics (data, account type, platform) as preconditions.
5. Write the expected result from Healthy result and the actual result from
   your run. A reproduction is ready only when you have seen the actual result.
