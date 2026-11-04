import { expect, mock, test } from 'claude-code/testing'
import type { On } from 'claude-code'

import * as collector from '../hooks/collector'
import * as live from '../hooks/live'
import type { Snapshot } from '../types'

const HOME = '/home/u'
const DIR = `${HOME}/.claude/session-board/sessions`
const T0 = 1_800_000_000_000

const PANE = (bodyColumns: number) =>
  ({
    plugin: 'session-board',
    component: 'Pane',
    requestId: 'session-board',
    props: {
      title: 'Session Board',
      isFocused: false,
      bodyColumns,
      placement: 'dock',
      scroll: { offset: 0, bodyRows: 40 },
      view: {},
    },
  }) as const

/** `/board <args>` as typed at the prompt. */
const board = (args: string) => ({
  command: 'board',
  args,
  origin: { kind: 'composer' as const },
  presentation: { isFullscreen: true, columns: 160 },
})

/** Everything beneath the plugin: an in-memory home folder and a session. */
const world = (on: On, files: Map<string, string>, where: { cwd?: string; root?: string } = {}) => {
  const cwd = where.cwd ?? '/work/app'
  const root = where.root ?? '/work/app'
  mock.env(on, { HOME })
  mock.store(on)
  const clock = mock.clock(on, { now: T0 })
  const toasts: string[] = []
  on('fs.read', (_, e) => {
    const text = files.get(e.path)
    if (text === undefined) throw new Error(`ENOENT ${e.path}`)
    return { value: text }
  })
  on('fs.write', (_, e) => {
    files.set(e.path, e.text)
    return { value: undefined }
  })
  on('fs.list', (_, e) => ({
    value: [...files.keys()]
      .filter(p => p.startsWith(`${e.path}/`))
      .map(p => ({ name: p.slice(e.path.length + 1), kind: 'file' as const, size: 1, mtimeMs: clock.now(), isLink: false })),
  }))
  on('session.id', () => ({ value: 'self' }))
  on('session.cwd', () => ({ value: cwd }))
  on('session.model', () => ({ value: 'claude-opus-5-5' }))
  on('session.repo', () => ({ value: { root, remote: null, internal: false, name: 'app' } }))
  on('session.usage', () => ({
    value: { startedAt: T0, context: { window: 200_000, percent: 42 }, rateLimits: [], cost: { usd: 0.5 } },
  }))
  on('agent.list', () => ({ value: [] }))
  on('ui.panes', () => ({ value: [] }))
  on('ui.status', () => ({ value: undefined }))
  on('ui.toast', (_, e) => {
    toasts.push(e.text)
    return { value: undefined }
  })
  on('command.register', () => ({ value: { command: 'board' } }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  on('turn.start', (_, e) => ({ turnId: e.turnId }))
  on('turn.complete', (_, e) => ({ text: e.answer }))
  on('tool.call', () => ({ result: {} }))
  on('fs.stat', (_, e) => {
    const text = files.get(e.path)
    if (text === undefined) throw new Error(`ENOENT ${e.path}`)
    return { value: { kind: 'file' as const, size: text.length, mtimeMs: clock.now(), isLink: false } }
  })
  // `ps -o pid= -p …` answers the pids in `alive`; `tail -c N path` the file's end.
  const alive = new Set<number>()
  on('process.run', (_, e) => {
    const [cmd, ...args] = e.argv
    if (cmd === 'ps') {
      const asked = String(args.at(-1) ?? '').split(',').map(Number)
      const out = asked.filter(n => alive.has(n)).map(n => `  ${n}`).join('\n')
      return { value: { exitCode: out ? 0 : 1, stdout: out, stderr: '', isStdoutTruncated: false, isStderrTruncated: false } }
    }
    if (cmd === 'tail') {
      const text = files.get(String(args.at(-1))) ?? ''
      const n = Number(args[1])
      return { value: { exitCode: 0, stdout: text.slice(-n), stderr: '', isStdoutTruncated: false, isStderrTruncated: false } }
    }
    throw new Error(`unexpected ${cmd}`)
  })
  files.set('/work/app/.git/HEAD', 'ref: refs/heads/feat/login\n')
  return { clock, toasts, alive }
}

const other = (id: string, fields: Partial<Snapshot>): Snapshot => ({
  v: 1,
  id,
  title: id,
  cwd: `/work/${id}`,
  project: id,
  branch: 'main',
  model: 'claude-sonnet-5-5',
  status: 'working',
  since: T0 - 60_000,
  startedAt: T0 - 600_000,
  beat: T0,
  tool: null,
  summary: '',
  answer: '',
  prompt: '',
  turns: 1,
  todos: [],
  files: [],
  agents: [],
  steps: [],
  ctx: null,
  cost: null,
  surface: 'terminal',
  ...fields,
})

test('a session writes its own heartbeat as it works', async ($, on) => {
  const files = new Map<string, string>()
  const { clock } = world(on, files)

  await $.session.start({ cwd: '/work/app', surface: 'terminal', isInteractive: true })
  await $.turn.start({ text: 'Add a login form\nwith validation', turnId: 't1' })
  await $.tool.call({ tool: 'Edit', file_path: '/work/app/src/login.tsx', old_string: 'a', new_string: 'b' })
  await $.tool.call({
    tool: 'TodoWrite',
    todos: [
      { content: 'form', status: 'completed', activeForm: 'form' },
      { content: 'tests', status: 'in_progress', activeForm: 'tests' },
    ],
  })
  await $.turn.complete({ answer: '## Done\nThe form is in.', turnId: 't1', durationMs: 4200, isAborted: false, reason: 'answer' })
  await clock.advance(1000)

  const snap = JSON.parse(files.get(`${DIR}/self.json`)!) as Snapshot
  expect(snap.status).toBe('idle')
  expect(snap.title).toBe('Add a login form')
  expect(snap.branch).toBe('feat/login')
  expect(snap.project).toBe('app')
  expect(snap.files).toEqual(['/work/app/src/login.tsx'])
  expect(snap.todos.map(t => t.state)).toEqual(['completed', 'in_progress'])
  expect(snap.steps.map(s => s.kind)).toEqual(['prompt', 'tool', 'tool', 'answer'])
  expect(snap.summary).toBe('Done')
  expect(snap.ctx).toBe(42)
  expect(snap.cost).toBe(0.5)
})

test("a git worktree shows its own branch, not the main checkout's", async ($, on) => {
  const files = new Map<string, string>()
  // The repository root the engine reports is the main checkout, on another branch.
  const { clock } = world(on, files, { cwd: '/work/wt/packages/ui', root: '/work/app' })
  files.set('/work/wt/.git', 'gitdir: /work/app/.git/worktrees/wt\n')
  files.set('/work/app/.git/worktrees/wt/HEAD', 'ref: refs/heads/claude/session-fix\n')

  await $.session.start({ cwd: '/work/wt/packages/ui', surface: 'terminal', isInteractive: true })
  await clock.advance(1000)

  const snap = JSON.parse(files.get(`${DIR}/self.json`)!) as Snapshot
  expect(snap.branch).toBe('claude/session-fix')
})

test('folders are walked from the session up to the root', async () => {
  expect(collector.dirsUp('/a/b/c/')).toEqual(['/a/b/c', '/a/b', '/a', '/'])
  expect(collector.dirsUp('/')).toEqual(['/'])
  expect(collector.resolveGitDir('/w', 'gitdir: ../main/.git/worktrees/w')).toBe('/w/../main/.git/worktrees/w')
  expect(collector.resolveGitDir('/w', 'gitdir: /m/.git/worktrees/w')).toBe('/m/.git/worktrees/w')
})

test('a permission prompt puts the session in the needs-you lane', async ($, on) => {
  const files = new Map<string, string>()
  const { clock } = world(on, files)
  on('tool.check', () => ({ decision: 'ask' as const, reason: 'needs approval' }))

  await $.session.start({ cwd: '/work/app', surface: 'terminal', isInteractive: true })
  await $.turn.start({ text: 'Run the tests', turnId: 't1' })
  await $.tool.check({ tool: 'Bash', input: { command: 'npm test', description: 'Run tests' } })
  await clock.advance(1000)

  const snap = JSON.parse(files.get(`${DIR}/self.json`)!) as Snapshot
  expect(snap.status).toBe('permission')
  expect(snap.tool).toBe('권한 요청 · Bash Run tests')
  expect(snap.steps.at(-1)).toMatchObject({ kind: 'permission', state: 'wait' })
})

test('the ask marks the call it came from, which the engine raises inside the call', async () => {
  collector.start({ id: 'x', cwd: '/w', model: 'm', now: 0, project: 'w', branch: null, surface: null, prior: null })
  collector.addStep({ id: 'tu1', kind: 'tool', label: 'Bash ls', state: 'run' }, 1)
  collector.asked('tu1', 'Bash ls', 2)
  collector.endStep('tu1', 'ok', 5)
  const snap = collector.current()!
  expect(snap.steps).toHaveLength(1)
  expect(snap.steps[0]).toMatchObject({ kind: 'tool', state: 'ok', ms: 4 })
  expect(snap.status).toBe('permission')
})

test('the board sorts sessions into lanes and opens one in detail, on every surface', async ($, on) => {
  const files = new Map<string, string>()
  const { clock } = world(on, files)
  files.set(`${DIR}/a.json`, JSON.stringify(other('a', { title: 'Fix flaky tests', status: 'permission', tool: '권한 요청 · Bash npm test' })))
  files.set(`${DIR}/b.json`, JSON.stringify(other('b', { title: 'Refactor auth', status: 'working', tool: 'Edit auth.ts', ctx: 71 })))
  files.set(`${DIR}/c.json`, JSON.stringify(other('c', { title: 'Write docs', status: 'idle', answer: 'Docs are written.' })))
  files.set(`${DIR}/d.json`, JSON.stringify(other('d', { title: 'Old run', status: 'working', beat: T0 - 3_600_000 })))

  await $.session.start({ cwd: '/work/app', surface: 'desktop', isInteractive: true })
  await $.command.run(board(''))
  await clock.advance(2000)

  for (const surface of ['terminal', 'desktop', 'vscode', 'mobile'] as const) {
    const ui = await $.ui.mount({ ...PANE(130), surface })
    expect(await ui.find({ key: 'open-a' })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /권한 요청/ })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /연결 끊김/ })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /▸ Edit auth.ts/ })).toBeDefined()

    await ui.press({ key: 'open-c' })
    expect(await ui.find({ type: 'Text', text: /마지막 답변/ })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /Write docs/ })).toBeDefined()

    await ui.press({ key: 'tab-flow' })
    expect(await ui.find({ type: 'Text', text: /턴 1|아직 활동이 없습니다/ })).toBeDefined()

    await ui.press({ key: 'all-flow' })
    expect(await ui.find({ type: 'Text', text: /서브에이전트/ })).toBeDefined()

    await ui.press({ key: 'tab-board' })
    await ui.unmount()
  }
})

test('a narrow pane stacks the lanes and still draws', async ($, on) => {
  const files = new Map<string, string>()
  const { clock } = world(on, files)
  files.set(`${DIR}/a.json`, JSON.stringify(other('a', { title: 'Narrow one', status: 'question' })))

  await $.session.start({ cwd: '/work/app', surface: 'terminal', isInteractive: true })
  await $.command.run(board('board'))
  await clock.advance(2000)

  const ui = await $.ui.mount({ ...PANE(40), surface: 'terminal' })
  expect(await ui.find({ type: 'Text', text: /답변 대기/ })).toBeDefined()
  await ui.unmount()
})

test('another session that starts needing the person raises a toast', async ($, on) => {
  const files = new Map<string, string>()
  const { clock, toasts } = world(on, files)
  files.set(`${DIR}/a.json`, JSON.stringify(other('a', { title: 'Deploy check', status: 'working' })))

  await $.session.start({ cwd: '/work/app', surface: 'terminal', isInteractive: true })
  await $.command.run(board(''))
  await clock.advance(2000)
  expect(toasts).toEqual([])

  files.set(`${DIR}/a.json`, JSON.stringify(other('a', { title: 'Deploy check', status: 'permission', beat: T0 + 2000 })))
  await clock.advance(2000)
  expect(toasts.some(t => t.includes('Deploy check') && t.includes('권한 요청'))).toBe(true)
})

test('a value an earlier version stored is declined', async ($, on) => {
  on('state.get', () => ({ value: { value: { list: 'not a list' }, version: 1 } }))
  const ui = await $.ui.mount({ ...PANE(100), surface: 'desktop' })
  expect(await ui.find({ type: 'Text', text: /아직 기록된 세션이 없습니다/ })).toBeDefined()
  await ui.unmount()
})

const row = (o: Record<string, unknown>) => JSON.stringify(o)

/** A transcript as the engine writes it: one JSON row per line. */
const TRANSCRIPT = [
  row({ type: 'custom-title', customTitle: '결제 모듈 정리', sessionId: 'live-1' }),
  row({ type: 'user', isSidechain: false, gitBranch: 'feat/pay', timestamp: '2026-11-04T08:00:00.000Z', uuid: 'u1', message: { role: 'user', content: 'Clean up the payment module' } }),
  row({ type: 'user', isSidechain: false, isMeta: true, timestamp: '2026-11-04T08:00:00.100Z', message: { role: 'user', content: '<system-reminder>ignore me</system-reminder>' } }),
  row({ type: 'assistant', isSidechain: false, gitBranch: 'feat/pay', timestamp: '2026-11-04T08:00:01.000Z', message: { role: 'assistant', model: 'claude-opus-5-5', content: [{ type: 'tool_use', id: 't1', name: 'Edit', input: { file_path: '/w/pay/charge.ts' } }] } }),
  row({ type: 'user', isSidechain: false, timestamp: '2026-11-04T08:00:03.000Z', message: { role: 'user', content: [{ type: 'tool_result', tool_use_id: 't1' }] } }),
  row({ type: 'assistant', isSidechain: false, timestamp: '2026-11-04T08:00:04.000Z', message: { role: 'assistant', content: [{ type: 'tool_use', id: 't2', name: 'TodoWrite', input: { todos: [{ content: 'split charge()', status: 'completed' }, { content: 'add tests', status: 'in_progress' }] } }] } }),
  row({ type: 'user', isSidechain: false, timestamp: '2026-11-04T08:00:04.500Z', message: { role: 'user', content: [{ type: 'tool_result', tool_use_id: 't2' }] } }),
  row({ type: 'assistant', isSidechain: false, timestamp: '2026-11-04T08:00:05.000Z', message: { role: 'assistant', content: [{ type: 'text', text: 'Split charge() into two steps.' }], stop_reason: 'end_turn' } }),
  row({ type: 'user', isSidechain: false, timestamp: '2026-11-04T08:01:00.000Z', uuid: 'u2', message: { role: 'user', content: [{ type: 'text', text: 'now run the tests' }] } }),
  row({ type: 'assistant', isSidechain: false, timestamp: '2026-11-04T08:01:01.000Z', message: { role: 'assistant', content: [{ type: 'tool_use', id: 't3', name: 'Bash', input: { command: 'npm test', description: 'Run tests' } }] } }),
  row({ type: 'assistant', isSidechain: true, timestamp: '2026-11-04T08:01:02.000Z', message: { role: 'assistant', content: [{ type: 'tool_use', id: 'side', name: 'Read', input: { file_path: '/x' } }] } }),
  row({ type: 'cost-state', totalCostUSD: 0.87 }),
  row({ type: 'pr-link', prNumber: 42, prUrl: 'https://github.com/acme/pay/pull/42' }),
].join('\n')

test('a transcript tail reads into a card: title, steps, todos, files, the call still running', async () => {
  const tail = live.readTail(TRANSCRIPT, true)
  expect(tail.title).toBe('결제 모듈 정리')
  expect(tail.branch).toBe('feat/pay')
  expect(tail.model).toBe('claude-opus-5-5')
  expect(tail.turns).toBe(2)
  expect(tail.steps.map(s => `${s.kind}:${s.state}`)).toEqual([
    'prompt:ok',
    'tool:ok',
    'tool:ok',
    'answer:ok',
    'prompt:ok',
    'tool:run',
  ])
  expect(tail.steps[1]?.ms).toBe(2000)
  expect(tail.todos.map(t => t.state)).toEqual(['completed', 'in_progress'])
  expect(tail.files).toEqual(['/w/pay/charge.ts'])
  expect(tail.summary).toBe('Split charge() into two steps.')
  expect(tail.tool).toBe('Bash Run tests')
  expect(tail.cost).toBe(0.87)
  expect(tail.pr).toEqual({ number: 42, url: 'https://github.com/acme/pay/pull/42' })

  // Read from the middle of a file, the first, partial line is dropped.
  expect(live.readTail(`{"type":"cust\n${TRANSCRIPT}`, false).title).toBe('결제 모듈 정리')
})

test('the registry status maps onto the board, waiting split by what it waits for', async () => {
  const reg = (fields: Partial<live.Reg>): live.Reg => ({ pid: 1, sessionId: 's', cwd: '/w/pay', startedAt: 0, ...fields })
  expect(live.statusOfReg(reg({ status: 'busy' }))).toBe('working')
  expect(live.statusOfReg(reg({ status: 'shell' }))).toBe('working')
  expect(live.statusOfReg(reg({ status: 'idle' }))).toBe('idle')
  expect(live.statusOfReg(reg({ status: 'waiting', waitingFor: 'dialog open' }))).toBe('permission')
  expect(live.statusOfReg(reg({ status: 'waiting', waitingFor: 'input needed' }))).toBe('question')
  expect(live.projectDir('/Users/me/work/ai-skills/.claude/worktrees/x-1')).toBe('-Users-me-work-ai-skills--claude-worktrees-x-1')

  const card = live.fromLive(reg({ status: 'waiting', waitingFor: 'dialog open', name: 'Payments', nameSource: 'user', entrypoint: 'claude-desktop', statusUpdatedAt: 5 }), live.readTail(TRANSCRIPT, true), 9)
  expect(card).toMatchObject({ status: 'permission', title: 'Payments', tool: '확인 대기 · 대화상자 열림', surface: 'desktop', since: 5, source: 'live', branch: 'feat/pay' })

  // A derived registry name gives way to the transcript's title.
  expect(live.fromLive(reg({ name: 'x-1-27', nameSource: 'derived' }), live.readTail(TRANSCRIPT, true), 9).title).toBe('결제 모듈 정리')
})

test('a running session without the plugin shows on the board from the registry and its transcript', async ($, on) => {
  const files = new Map<string, string>()
  const { clock, alive, toasts } = world(on, files)
  const REG = `${HOME}/.claude/sessions`
  files.set(`${REG}/4242.json`, JSON.stringify({ pid: 4242, sessionId: 'live-1', cwd: '/w/pay', startedAt: T0 - 60_000, kind: 'interactive', entrypoint: 'cli', name: 'pay-3', nameSource: 'derived', status: 'busy', statusUpdatedAt: T0 - 5000 }))
  files.set(`${REG}/999.json`, JSON.stringify({ pid: 999, sessionId: 'gone', cwd: '/w/old', startedAt: T0 - 60_000, kind: 'interactive', status: 'idle', name: 'Gone session', nameSource: 'user' }))
  files.set(`${HOME}/.claude/projects/-w-pay/live-1.jsonl`, TRANSCRIPT)
  alive.add(4242)

  await $.session.start({ cwd: '/work/app', surface: 'desktop', isInteractive: true })
  await $.command.run(board(''))
  await clock.advance(2000)

  for (const surface of ['terminal', 'desktop'] as const) {
    const ui = await $.ui.mount({ ...PANE(130), surface })
    expect(await ui.find({ key: 'open-live-1' })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /▸ Bash Run tests/ })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /#42/ })).toBeDefined()
    expect(await ui.find({ key: 'open-gone' })).toBeUndefined()
    await ui.press({ key: 'open-live-1' })
    expect(await ui.find({ type: 'Text', text: /플러그인 미로드/ })).toBeDefined()
    await ui.press({ key: 'tab-board' })
    await ui.unmount()
  }

  // The registry says it now waits on a dialog: the person hears of it.
  files.set(`${REG}/4242.json`, JSON.stringify({ pid: 4242, sessionId: 'live-1', cwd: '/w/pay', startedAt: T0 - 60_000, kind: 'interactive', status: 'waiting', waitingFor: 'dialog open', statusUpdatedAt: T0 + 2500 }))
  await clock.advance(2000)
  expect(toasts.some(t => t.includes('결제 모듈 정리') && t.includes('권한 요청'))).toBe(true)
})

test('the registry corrects a heartbeat: its status wins, an empty heartbeat fills from the transcript', async () => {
  const reg: live.Reg = { pid: 7, sessionId: 'm', cwd: '/w/pay', startedAt: 0, status: 'busy', statusUpdatedAt: 50, name: 'pay-1', nameSource: 'derived' }
  const tail = live.readTail(TRANSCRIPT, true)

  // A permission prompt the desktop app settled unseen: the registry says busy.
  const asked = other('m', { status: 'permission', tool: '권한 요청 · Bash ls', since: 10, turns: 3, title: 'Mine' })
  const fixed = live.overlay(asked, reg, tail, 100)
  expect(fixed).toMatchObject({ status: 'working', since: 50, running: true, title: 'Mine', tool: 'Bash Run tests', pr: { number: 42 } })

  // The plugin loaded mid-session: no turn of its own yet.
  const empty = other('m', { status: 'idle', turns: 0, title: '', steps: [] })
  const filled = live.overlay(empty, { ...reg, status: 'idle' }, tail, 100)
  expect(filled).toMatchObject({ turns: 2, title: '결제 모듈 정리', running: true, tool: null })
  expect(filled.steps.length).toBe(tail.steps.length)

  // A turn that failed stays an error while the registry calls the session idle.
  expect(live.overlay(other('m', { status: 'error', turns: 1 }), { ...reg, status: 'idle' }, null, 100).status).toBe('error')
})
