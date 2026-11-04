# session-board

A Claude Code mod that shows every running Claude Code session on one board, in a
pane beside the chat. Sessions in the terminal and the desktop app both appear,
whether or not they load the plugin.

## Install

From a terminal:

```bash
claude plugin marketplace add devlikebear/ai-skills
```

```bash
claude plugin install session-board@ai-skills
```

`install` defaults to user scope. Every running session shows on the board.
Sessions that load the plugin add live context use, subagents and the exact
permission prompt. New sessions load it; restart sessions that were already
running to get that detail for them too.

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

The board reads three sources and merges them per session:

| Source | Gives |
| --- | --- |
| The engine's session registry, `~/.claude/sessions/<pid>.json`, kept to pids `ps` reports alive | which sessions run, their name, and whether each is busy, idle, or waiting on a dialog or input |
| The end of each session's transcript, `~/.claude/projects/<project>/<session-id>.jsonl` (the last 512 KB, read again only when the file changes) | title, branch, model, prompts, tool calls, todos, changed files, last answer, cost, linked PR |
| The plugin's own heartbeat, `~/.claude/session-board/sessions/<session-id>.json`, for sessions that load it | the same, live, plus context use and subagents |

- The registry's status wins: it is the engine's own word, and it knows when a
  dialog is open. A heartbeat keeps an error status while the registry calls the
  session idle.
- A session that loads the plugin writes its heartbeat from `turn.start`,
  `tool.call`, `tool.check`, `turn.complete` and `session.end`, within a second of
  a change and every 15 seconds otherwise. Todos follow TodoWrite, the Task tools
  and the desktop app's plan tool.
- No hook blocks or waits on the board: the hooks record and pass the event on.
- Only the session with the board open polls, every two seconds: one `ps` and one
  `tail` per transcript that changed. Heartbeats of sessions that are no longer
  running stay on the board, under 완료, for three days.

## Develop

```bash
claude plugin validate claude-code/session-board
claude plugin test claude-code/session-board
claude --plugin-dir claude-code/session-board
```

`hooks/register.tsx` wires the hooks and the ticker, `hooks/collector.ts` keeps the
snapshot, `hooks/live.ts` reads the registry and transcripts, `hooks/views.tsx` draws the pane, and `types/index.d.ts` is the state
contract. Engine calls stay inside hooks, spelled `$.noun.method(...)`; the other
modules are pure.
