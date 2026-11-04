/** What a session is doing, as its own collector last wrote it. */
export type Status = 'working' | 'permission' | 'question' | 'idle' | 'error' | 'ended'

/** The board column a session sits in. */
export type Lane = 'working' | 'needs' | 'review' | 'done'

export type StepKind = 'prompt' | 'tool' | 'agent' | 'permission' | 'question' | 'answer' | 'error'

/** One node of a session's workflow: a prompt, a tool call, a subagent, an answer. */
export type Step = {
  id: string
  kind: StepKind
  label: string
  detail?: string
  at: number
  ms?: number
  state: 'run' | 'ok' | 'fail' | 'wait'
  turn: number
  /** Set when the step ran inside a subagent. */
  agent?: string
}

export type Todo = { text: string; state: 'pending' | 'in_progress' | 'completed' }

export type Sub = { id: string; type: string; description: string; status: string }

/** The heartbeat file each session writes under ~/.claude/session-board/sessions. */
export type Snapshot = {
  v: 1
  id: string
  title: string
  cwd: string
  project: string
  branch: string | null
  model: string
  status: Status
  /** When `status` last changed. */
  since: number
  startedAt: number
  /** Last heartbeat. */
  beat: number
  /** The tool running now, as a short label. */
  tool: string | null
  /** First line of the last answer. */
  summary: string
  /** The last answer, cut to a readable length. */
  answer: string
  prompt: string
  turns: number
  todos: Todo[]
  files: string[]
  agents: Sub[]
  steps: Step[]
  ctx: number | null
  cost: number | null
  surface: string | null
}

export type View = 'board' | 'flow' | 'detail'

export type ViewState = { view: View; selected: string | null; showDone: boolean }

export type BoardData = { at: number; self: string; list: Snapshot[]; hidden: string[] }

declare module 'claude-code' {
  interface PluginState {
    'session-board': {
      board: Shaped<BoardData>
      ui: Shaped<ViewState>
    }
  }
}
