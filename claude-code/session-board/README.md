# session-board

A Claude Code mod that shows every active session on one board. Each session that
loads the plugin records its own state; the session where you open the board reads
them all and draws three views in a pane beside the chat.

## Install

From a terminal:

```bash
claude plugin marketplace add devlikebear/ai-skills
```

```bash
claude plugin install session-board@ai-skills
```

`install` defaults to user scope. Keep it there so every session records itself:
a session that does not load the plugin does not appear on the board. New
sessions load it; restart sessions that were already running.

Update or remove it the same way:

```bash
claude plugin update session-board@ai-skills
```

```bash
claude plugin uninstall session-board@ai-skills
```

## Use

| Command | Opens |
| --- | --- |
| `/board` | the board |
| `/board flow` | the workflow view |
| `/board detail` | the detail view |

In the pane, `1` `2` `3` switch views and `j` / `k` step through sessions in the
detail and workflow views.

### Board

Four lanes, sorted so the sessions that need you come first:

| Lane | Status |
| --- | --- |
| 나를 기다림 (needs you) | permission prompt, question or plan waiting, error |
| 작업 중 (working) | a turn is running |
| 리뷰 (review) | the last turn finished |
| 완료 (done) | the session ended, or its heartbeat is older than 90 seconds |

A card shows the status and how long it has held, the title (first prompt), project
and branch, the tool running now or the last answer's first line, and a row with
context use, todo progress, running subagents and cost. The pane lays the lanes out
in four columns, a 2×2 grid or a single stack, depending on its width. Press a title
to open the session in detail. "정리" hides finished sessions.

### Workflow

With no session selected, one row per session shows its recent steps as a chain:
`›` prompt, `●` tool, `◆` subagent, `◉` permission, `?` question, `✓` answer,
`✕` error. Select a session for its timeline: each turn with its prompt, every tool
call and subagent step, and how long each took.

### Detail

Status, project, branch, path, model, turns, context meter and cost, followed by the
last answer, todos, subagents, files changed and recent activity. For another live
session, a field sends it a message.

### Notifications

While the board is open, a toast tells you when another session starts waiting for
permission or an answer, stops on an error, or finishes a turn. The status line
keeps a count per lane.

## How it works

- Each session keeps a snapshot and writes it to
  `~/.claude/session-board/sessions/<session-id>.json` within a second of a
  change, and every 15 seconds otherwise.
- The snapshot follows `turn.start`, `tool.call`, `tool.check` (a permission
  prompt), `turn.complete` and `session.end`. It reads context use, cost and
  subagents from the session. Todos come from TodoWrite, the Task tools and the
  desktop app's plan tool.
- No hook blocks or waits on the board: the hooks record and pass the event on.
- The session with the board open reads the folder every two seconds. Snapshots
  older than three days are skipped. Files are small; delete the folder to reset.

## Develop

```bash
claude plugin validate claude-code/session-board
claude plugin test claude-code/session-board
claude --plugin-dir claude-code/session-board
```

`hooks/register.tsx` wires the hooks and the ticker, `hooks/collector.ts` keeps the
snapshot, `hooks/views.tsx` draws the pane, and `types/index.d.ts` is the state
contract. Engine calls stay inside hooks, spelled `$.noun.method(...)`; the other
modules are pure.
