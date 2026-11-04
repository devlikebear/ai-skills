// Sessions that do not load this plugin: the engine's registry of running
// sessions (~/.claude/sessions/<pid>.json) says which are alive and what they
// are doing; the tail of each one's transcript fills in the rest. Pure data
// work: the hooks read the files and hand the text in.
import type { Snapshot, Status, Step, Todo } from '../types'
import { cut, firstLine, nextTodos, toolLabel } from './util'

/** How much of a transcript's end is read for a session's card. */
export const TAIL_BYTES = 512 * 1024

const MAX_STEPS = 160
const EDITS = new Set(['Edit', 'Write', 'MultiEdit', 'NotebookEdit'])
const QUESTIONS = new Set(['AskUserQuestion', 'ExitPlanMode'])
const AGENTS = new Set(['Agent', 'Task'])

/** One entry of the engine's session registry, as far as the board reads it. */
export type Reg = {
  pid: number
  sessionId: string
  cwd: string
  startedAt: number
  kind?: string
  entrypoint?: string
  name?: string
  nameSource?: string
  status?: string
  waitingFor?: string
  updatedAt?: number
  statusUpdatedAt?: number
}

export const parseReg = (text: string): Reg | null => {
  try {
    const r = JSON.parse(text) as Reg
    return typeof r?.pid === 'number' && typeof r.sessionId === 'string' && typeof r.cwd === 'string' ? r : null
  } catch {
    return null
  }
}

/** The folder under ~/.claude/projects that holds a session's transcript. */
export const projectDir = (cwd: string) => cwd.replace(/[^A-Za-z0-9]/g, '-')

/** The pids `ps -o pid= -p …` printed. */
export const alivePids = (stdout: string) =>
  new Set(stdout.split(/\s+/).filter(Boolean).map(Number).filter(n => Number.isFinite(n)))

export const statusOfReg = (r: Reg): Status => {
  if (r.status === 'busy' || r.status === 'shell') return 'working'
  if (r.status === 'waiting') return /input|goal/.test(r.waitingFor ?? '') ? 'question' : 'permission'
  return 'idle'
}

const WAITING_LABEL: Record<string, string> = {
  'dialog open': '확인 대기 · 대화상자 열림',
  'input needed': '입력 필요',
  'sandbox request': '샌드박스 승인 요청',
  'goal proposal': '목표 제안 확인',
}

export const waitingLabel = (waitingFor: string | null | undefined) =>
  waitingFor ? (WAITING_LABEL[waitingFor] ?? waitingFor) : null

const surfaceOf = (entrypoint: string | undefined) =>
  entrypoint === 'claude-desktop' ? 'desktop' : entrypoint === 'cli' ? 'terminal' : (entrypoint ?? null)

/** What the end of a transcript says about its session. */
export type Tail = {
  title: string
  prompt: string
  branch: string | null
  model: string
  summary: string
  answer: string
  cost: number | null
  pr: { number: number; url: string } | null
  tool: string | null
  turns: number
  todos: Todo[]
  files: string[]
  steps: Step[]
}

type Entry = Record<string, unknown> & { type?: string; message?: { role?: string; content?: unknown; model?: string; stop_reason?: string } }

const at = (e: Entry) => {
  const t = typeof e.timestamp === 'string' ? Date.parse(e.timestamp) : NaN
  return Number.isFinite(t) ? t : 0
}

/** The words a person typed, or null for a row they did not type. */
const typed = (text: string): string | null => {
  const t = text.trim()
  if (!t) return null
  const command = /<command-name>\/?([^<]+)<\/command-name>/.exec(t)
  if (command) return `/${command[1]!.trim()}`
  if (t.startsWith('<')) return null
  return t
}

/**
 * Reads the end of a transcript. `whole` says the text starts at the file's
 * start; otherwise its first line is a partial row and is dropped.
 */
export const readTail = (text: string, whole: boolean): Tail => {
  const lines = text.split('\n')
  if (!whole) lines.shift()
  const tail: Tail = {
    title: '',
    prompt: '',
    branch: null,
    model: '',
    summary: '',
    answer: '',
    cost: null,
    pr: null,
    tool: null,
    turns: 0,
    todos: [],
    files: [],
    steps: [],
  }
  let agentName = ''
  const open = new Map<string, Step>()
  for (const line of lines) {
    if (!line.trim()) continue
    let e: Entry
    try {
      e = JSON.parse(line) as Entry
    } catch {
      continue
    }
    switch (e.type) {
      case 'custom-title':
        if (typeof e.customTitle === 'string') tail.title = e.customTitle
        continue
      case 'agent-name':
        if (typeof e.agentName === 'string') agentName = e.agentName
        continue
      case 'last-prompt':
        if (typeof e.lastPrompt === 'string') tail.prompt = cut(e.lastPrompt, 300)
        continue
      case 'cost-state':
        if (typeof e.totalCostUSD === 'number') tail.cost = e.totalCostUSD
        continue
      case 'pr-link':
        if (typeof e.prNumber === 'number' && typeof e.prUrl === 'string') tail.pr = { number: e.prNumber, url: e.prUrl }
        continue
      case 'user':
      case 'assistant':
        break
      default:
        continue
    }
    if (e.isSidechain === true) continue
    if (typeof e.gitBranch === 'string' && e.gitBranch) tail.branch = e.gitBranch
    const when = at(e)
    const content = e.message?.content
    const blocks = Array.isArray(content) ? (content as Record<string, unknown>[]) : [{ type: 'text', text: content }]

    if (e.type === 'user') {
      for (const b of blocks) {
        if (b.type === 'tool_result' && typeof b.tool_use_id === 'string') {
          const step = open.get(b.tool_use_id)
          if (step) {
            step.state = b.is_error === true ? 'fail' : 'ok'
            if (when && step.at) step.ms = when - step.at
            open.delete(b.tool_use_id)
          }
        } else if (b.type === 'text' && typeof b.text === 'string' && e.isMeta !== true) {
          const words = typed(b.text)
          if (!words) continue
          tail.turns += 1
          tail.steps.push({ id: String(e.uuid ?? `p${tail.turns}`), kind: 'prompt', label: cut(firstLine(words), 120), at: when, state: 'ok', turn: tail.turns })
          if (!tail.prompt) tail.prompt = cut(words, 300)
        }
      }
      continue
    }

    if (typeof e.message?.model === 'string') tail.model = e.message.model
    let said = ''
    for (const b of blocks) {
      if (b.type === 'text' && typeof b.text === 'string') said += b.text
      if (b.type !== 'tool_use' || typeof b.id !== 'string' || typeof b.name !== 'string') continue
      const input = (b.input ?? {}) as Record<string, unknown>
      const kind = AGENTS.has(b.name) ? 'agent' : QUESTIONS.has(b.name) ? 'question' : 'tool'
      const step: Step = { id: b.id, kind, label: toolLabel(b.name, input), at: when, state: kind === 'question' ? 'wait' : 'run', turn: tail.turns }
      tail.steps.push(step)
      open.set(b.id, step)
      tail.todos = nextTodos(b.name, input, tail.todos)
      if (EDITS.has(b.name)) {
        const path = input.file_path ?? input.notebook_path
        if (typeof path === 'string') tail.files = [path, ...tail.files.filter(f => f !== path)].slice(0, 40)
      }
    }
    if (said.trim()) {
      tail.answer = said.length > 1500 ? `${said.slice(0, 1500)}…` : said
      tail.summary = cut(firstLine(said), 160)
    }
    if (e.message?.stop_reason === 'end_turn') {
      tail.steps.push({ id: `answer-${String(e.uuid ?? when)}`, kind: 'answer', label: tail.summary || '(응답)', at: when, state: 'ok', turn: tail.turns })
      for (const step of open.values()) if (step.state === 'run') step.state = 'ok'
      open.clear()
    }
  }
  if (!tail.title) tail.title = agentName
  const pending = [...open.values()].at(-1)
  tail.tool = pending ? pending.label : null
  if (tail.steps.length > MAX_STEPS) tail.steps = tail.steps.slice(-MAX_STEPS)
  return tail
}

const isDerived = (r: Reg) => r.nameSource === 'derived' || !r.name

/** A card for a running session that does not load this plugin. */
export const fromLive = (r: Reg, tail: Tail | null, now: number): Snapshot => {
  const status = statusOfReg(r)
  const waiting = status === 'permission' || status === 'question' ? waitingLabel(r.waitingFor) : null
  return {
    v: 1,
    id: r.sessionId,
    title: (!isDerived(r) && r.name) || tail?.title || (tail?.prompt ? cut(firstLine(tail.prompt), 70) : '') || r.name || '',
    cwd: r.cwd,
    project: r.cwd.split('/').filter(Boolean).at(-1) ?? r.cwd,
    branch: tail?.branch ?? null,
    model: tail?.model ?? '',
    status,
    since: r.statusUpdatedAt ?? r.updatedAt ?? r.startedAt,
    startedAt: r.startedAt,
    beat: now,
    tool: waiting ?? (status === 'working' ? (tail?.tool ?? null) : null),
    summary: tail?.summary ?? '',
    answer: tail?.answer ?? '',
    prompt: tail?.prompt ?? '',
    turns: tail?.turns ?? 0,
    todos: tail?.todos ?? [],
    files: tail?.files ?? [],
    agents: [],
    steps: tail?.steps ?? [],
    ctx: null,
    cost: tail?.cost ?? null,
    surface: surfaceOf(r.entrypoint),
    source: 'live',
    running: true,
    waitingFor: r.waitingFor ?? null,
    pr: tail?.pr ?? null,
  }
}

/**
 * A session's own heartbeat, brought up to date by the registry. The registry
 * is the engine's own word on what the session is doing: busy, idle, or waiting
 * on a dialog or input (the plugin's hooks see a permission prompt that the
 * desktop app may settle unseen). A person's name for the session wins over its
 * first prompt, and a heartbeat with no turn yet (the plugin loaded mid-session)
 * is filled in from the transcript.
 */
export const overlay = (s: Snapshot, r: Reg, tail: Tail | null, now: number): Snapshot => {
  const status = statusOfReg(r)
  const out: Snapshot = { ...s, beat: Math.max(s.beat, now), running: true, pr: s.pr ?? tail?.pr ?? null }
  if (!isDerived(r) && r.name) out.title = r.name
  else if (!out.title && tail?.title) out.title = tail.title
  if (s.turns === 0 && s.steps.length === 0 && tail && tail.steps.length > 0) {
    out.turns = tail.turns
    out.prompt = tail.prompt
    out.steps = tail.steps
    out.summary = tail.summary
    out.answer = tail.answer
    out.todos = tail.todos
    out.files = tail.files
    out.branch = out.branch ?? tail.branch
    out.cost = out.cost ?? tail.cost
    if (!out.title) out.title = cut(firstLine(tail.prompt), 70)
  }
  const keepsError = s.status === 'error' && status === 'idle'
  if (!keepsError && status !== s.status) {
    out.status = status
    out.since = r.statusUpdatedAt ?? s.since
  }
  const waiting = out.status === 'permission' || out.status === 'question'
  out.waitingFor = waiting ? (r.waitingFor ?? null) : null
  if (waiting) out.tool = waitingLabel(r.waitingFor) ?? s.tool
  else if (out.status !== 'working' || s.tool?.startsWith('권한 요청')) out.tool = out.status === 'working' ? (tail?.tool ?? null) : null
  return out
}
