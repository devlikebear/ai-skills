// This session's snapshot, kept in memory and written by the ticker that
// session.start runs. Every function here is pure data work: the hooks do the
// engine calls and hand in what they read.
import type { Snapshot, Status, Step, Sub, Todo } from '../types'
import { cut, firstLine } from './util'

const MAX_STEPS = 160
const MAX_FILES = 40

let snap: Snapshot | null = null
let dirty = false

export const current = () => snap

export const isDirty = () => dirty

export const markDirty = () => {
  dirty = true
}

/** The snapshot as written, marking it clean. */
export const take = (now: number) => {
  if (!snap) return null
  snap.beat = now
  dirty = false
  return JSON.stringify(snap)
}

export type Start = {
  id: string
  cwd: string
  model: string
  now: number
  project: string
  branch: string | null
  surface: string | null
  prior: unknown
}

/** Builds this session's snapshot, picking up what an earlier load of the mod wrote. */
export const start = (a: Start) => {
  const p = a.prior as Partial<Snapshot> | null
  const prior = p && p.v === 1 && p.id === a.id ? (p as Snapshot) : null
  snap = {
    v: 1,
    id: a.id,
    title: prior?.title ?? '',
    cwd: a.cwd,
    project: a.project,
    branch: a.branch,
    model: a.model,
    status: prior && prior.status !== 'ended' ? prior.status : 'idle',
    since: prior?.since ?? a.now,
    startedAt: prior?.startedAt ?? a.now,
    beat: a.now,
    tool: prior?.tool ?? null,
    summary: prior?.summary ?? '',
    answer: prior?.answer ?? '',
    prompt: prior?.prompt ?? '',
    turns: prior?.turns ?? 0,
    todos: prior?.todos ?? [],
    files: prior?.files ?? [],
    agents: prior?.agents ?? [],
    steps: prior?.steps ?? [],
    ctx: prior?.ctx ?? null,
    cost: prior?.cost ?? null,
    surface: a.surface,
  }
  dirty = true
  return snap
}

/** `ref: refs/heads/x` → `x`; a detached HEAD → its short sha. */
export const branchOf = (head: string) => {
  const ref = head.trim()
  return ref.startsWith('ref: refs/heads/') ? ref.slice(16) : ref.slice(0, 8) || null
}

/** `dir` and each folder above it, nearest first, the filesystem root last. */
export const dirsUp = (dir: string): string[] => {
  const out: string[] = []
  let at = dir.replace(/\/+$/, '') || '/'
  for (let i = 0; i < 64; i += 1) {
    out.push(at)
    if (at === '/') break
    const cut = at.lastIndexOf('/')
    at = cut <= 0 ? '/' : at.slice(0, cut)
  }
  return out
}

/** The git directory a `.git` file's `gitdir: <path>` line names, absolute. */
export const resolveGitDir = (dir: string, pointer: string) => {
  const path = pointer.replace(/^gitdir:\s*/, '').trim()
  return path.startsWith('/') ? path : `${dir === '/' ? '' : dir}/${path}`
}

export const setStatus = (status: Status, now: number) => {
  if (!snap) return
  dirty = true
  if (snap.status === status) return
  snap.status = status
  snap.since = now
}

export const addStep = (step: Omit<Step, 'at' | 'turn'>, now: number) => {
  if (!snap) return
  snap.steps.push({ ...step, at: now, turn: snap.turns })
  if (snap.steps.length > MAX_STEPS) snap.steps.splice(0, snap.steps.length - MAX_STEPS)
  dirty = true
}

export const endStep = (id: string, state: Step['state'], now: number) => {
  const step = snap?.steps.findLast(one => one.id === id)
  if (!step || (step.state !== 'run' && step.state !== 'wait')) return
  step.ms = now - step.at
  step.state = state
  dirty = true
}

/** A permission prompt for a call: its step waits on the person, marked ◉. */
export const asked = (id: string | undefined, label: string, now: number) => {
  if (!snap) return
  const step = id ? snap.steps.findLast(one => one.id === id) : undefined
  if (step) {
    step.kind = 'permission'
    step.state = 'wait'
  } else addStep({ id: id ?? `perm-${now}`, kind: 'permission', label, state: 'wait' }, now)
  snap.tool = `권한 요청 · ${label}`
  setStatus('permission', now)
}

export const touch = (file: string) => {
  if (!snap) return
  snap.files = [file, ...snap.files.filter(one => one !== file)].slice(0, MAX_FILES)
}

export const setTodos = (raw: unknown) => {
  if (!snap || !Array.isArray(raw)) return
  const todos: Todo[] = []
  for (const item of raw as Record<string, unknown>[]) {
    const text = String(item?.content ?? item?.subject ?? item?.text ?? '')
    const state = String(item?.status ?? 'pending')
    if (!text) continue
    todos.push({
      text: cut(text, 120),
      state: state === 'completed' || state === 'in_progress' ? state : 'pending',
    })
  }
  snap.todos = todos
}

/** Follows TodoWrite, the Task tools and the desktop app's plan tool. */
export const trackTodos = (tool: string, input: Record<string, unknown>) => {
  if (!snap) return
  const todos = snap.todos
  if (tool === 'TodoWrite') return setTodos(input.todos)
  if (tool.endsWith('update_plan')) {
    if (Array.isArray(input.items)) return setTodos(input.items)
    const done = Array.isArray(input.done) ? (input.done as number[]) : []
    for (const n of done) if (todos[n - 1]) todos[n - 1]!.state = 'completed'
    if (input.advance === true) {
      const at = todos.findIndex(t => t.state === 'in_progress')
      if (at >= 0) todos[at]!.state = 'completed'
      const next = todos.find(t => t.state === 'pending')
      if (next) next.state = 'in_progress'
    }
    if (typeof input.start === 'number' && todos[input.start - 1]) todos[input.start - 1]!.state = 'in_progress'
    return
  }
  if (tool.endsWith('wrap_up')) {
    for (const t of todos) t.state = 'completed'
    return
  }
  if (tool === 'TaskCreate' && typeof input.subject === 'string') {
    todos.push({ text: cut(input.subject, 120), state: 'pending' })
    return
  }
  if (tool === 'TaskUpdate') {
    const t = todos[Number(input.taskId) - 1]
    const state = String(input.status ?? '')
    if (t && (state === 'pending' || state === 'in_progress' || state === 'completed')) t.state = state
  }
}

export const prompted = (text: string, turnId: string, now: number) => {
  if (!snap) return
  const line = firstLine(text)
  snap.turns += 1
  snap.prompt = cut(text, 300)
  if (!snap.title && line) snap.title = cut(line, 70)
  snap.tool = null
  setStatus('working', now)
  addStep({ id: turnId, kind: 'prompt', label: cut(line || '(빈 프롬프트)', 120), state: 'ok' }, now)
}

export const answered = (a: { answer: string; turnId: string; durationMs: number; failed: boolean; aborted: boolean }, now: number) => {
  if (!snap) return
  snap.summary = cut(firstLine(a.answer), 160)
  snap.answer = a.answer.length > 1500 ? `${a.answer.slice(0, 1500)}…` : a.answer
  snap.tool = null
  for (const step of snap.steps)
    if (step.turn === snap.turns && (step.state === 'run' || step.state === 'wait'))
      step.state = step.kind === 'permission' ? 'fail' : 'ok'
  addStep(
    {
      id: `answer-${a.turnId}`,
      kind: a.failed ? 'error' : 'answer',
      label: a.aborted ? '중단됨' : snap.summary || '(응답 없음)',
      state: a.failed ? 'fail' : 'ok',
      ms: a.durationMs,
    },
    now,
  )
  setStatus(a.failed ? 'error' : 'idle', now)
}

export type UsageRead = {
  percent: number | null
  usd: number | null
  model: string
  agents: readonly { id: string; type: string; description: string; status: string }[]
}

export const applyUsage = (u: UsageRead) => {
  if (!snap) return
  snap.ctx = u.percent
  snap.cost = u.usd
  snap.model = u.model
  snap.agents = u.agents.slice(-12).map(
    (a): Sub => ({ id: a.id, type: a.type, description: cut(a.description, 80), status: a.status }),
  )
  dirty = true
}
