import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

import type { BoardData, Snapshot, Status, StepKind, ViewState } from '../types'
import * as collector from './collector'
import * as live from './live'
import { LANE_LABEL, STATUS_LABEL, base, cut, laneOf, toolLabel } from './util'
import { view } from './views'
import type { Act } from './views'

const PANE = 'session-board'

// Change a tag when that value's fields change: it declines what an earlier
// version stored, which outlives a reload.
const boardAtom = atom(
  { plugin: 'session-board', key: 'board' } as const,
  { at: 0, self: '', list: [], hidden: [] } as BoardData,
  { shape: 'board-1' },
)
const uiAtom = atom(
  { plugin: 'session-board', key: 'ui' } as const,
  { view: 'board', selected: null, showDone: false } as ViewState,
  { shape: 'ui-1' },
)

const TICK_MS = 1000
const POLL_TICKS = 2
const BEAT_MS = 15_000
const USAGE_TICKS = 15
const KEEP_MS = 3 * 24 * 3600_000
const EDITS = new Set(['Edit', 'Write', 'MultiEdit', 'NotebookEdit'])
const QUESTIONS = new Set(['AskUserQuestion', 'ExitPlanMode'])
const AGENTS = new Set(['Agent', 'Task'])
const VIEWS = new Set(['board', 'flow', 'detail'])

// Module state: what one load of the mod keeps between its own hooks.
let ticker: { cancel(): void } | null = null
let file = ''
let dir = ''
let boardOpen = false
let pollNow = false
let seen = new Map<string, Status>()
const tailCache = new Map<string, { key: string; tail: live.Tail }>()

// ── pure board work ─────────────────────────────────────────────────────────

const parse = (text: string): Snapshot | null => {
  try {
    const s = JSON.parse(text) as Snapshot
    return s?.v === 1 && typeof s.id === 'string' ? s : null
  } catch {
    return null
  }
}

/** Toasts for another session that starts needing the person, or finishes. */
const transitions = (list: readonly Snapshot[], self: string): string[] => {
  const first = seen.size === 0
  const out: string[] = []
  for (const s of list) {
    const before = seen.get(s.id)
    seen.set(s.id, s.status)
    if (first || before === undefined || before === s.status || s.id === self) continue
    const name = cut(s.title || s.prompt || s.project, 32)
    if (s.status === 'permission' || s.status === 'question') out.push(`⚠ ${name} · ${STATUS_LABEL[s.status]}`)
    else if (s.status === 'error') out.push(`✕ ${name} · 오류로 멈춤`)
    else if (before === 'working' && s.status === 'idle') out.push(`✓ ${name} · 응답 완료`)
  }
  return out
}

const statusLine = (all: readonly Snapshot[], now: number, self: string) => {
  const list = all.filter(s => s.turns > 0 || s.id === self || s.running === true)
  const parts = (['needs', 'working', 'review'] as const)
    .map(l => [l, list.filter(s => laneOf(s, now) === l).length] as const)
    .filter(([, n]) => n > 0)
    .map(([l, n]) => `${LANE_LABEL[l]} ${n}`)
  return parts.length ? `⧉ ${parts.join(' · ')}` : undefined
}

// ── hooks ─────────────────────────────────────────────────────────────────

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'board',
      description: '세션 보드 열기 (board | flow | detail)',
      argumentHint: '[board|flow|detail]',
    })

    const [id, cwd, model, now, repo, home, panes] = await Promise.all([
      $.session.id(),
      $.session.cwd(),
      $.session.model(),
      $.clock.now(),
      $.session.repo(),
      $.env.get('HOME'),
      $.ui.panes(),
    ])
    dir = `${home ?? ''}/.claude/session-board/sessions`
    const regDir = `${home ?? ''}/.claude/sessions`
    file = `${dir}/${id}.json`
    const root = repo?.root ?? cwd

    let prior: unknown = null
    try {
      prior = JSON.parse((await $.fs.read(file)) as string)
    } catch {}

    // The nearest .git above the session's directory names its branch: a git
    // worktree's own `.git` file points at its HEAD, while the repository root
    // may be the main checkout on another branch.
    let branch: string | null = null
    for (const dir of collector.dirsUp(cwd)) {
      try {
        branch = collector.branchOf((await $.fs.read(`${dir}/.git/HEAD`)) as string)
        break
      } catch {}
      try {
        const pointer = ((await $.fs.read(`${dir}/.git`)) as string).trim()
        if (pointer.startsWith('gitdir:')) {
          const gitDir = collector.resolveGitDir(dir, pointer)
          branch = collector.branchOf((await $.fs.read(`${gitDir}/HEAD`)) as string)
          break
        }
      } catch {}
    }

    collector.start({
      id,
      cwd,
      model,
      now,
      project: repo?.name ?? base(root),
      branch,
      surface: e.surface,
      prior,
    })
    boardOpen = panes.some(p => p.id === PANE)
    pollNow = boardOpen

    // One ticker does every write and read this load makes after the start.
    let tick = 0
    let wrote = 0
    ticker?.cancel()
    ticker = $.clock.every(TICK_MS, () => {
      void (async () => {
        tick += 1
        const at = await $.clock.now()

        if (tick % USAGE_TICKS === 0) {
          try {
            const [usage, agents, model] = await Promise.all([
              $.session.usage(),
              $.agent.list(),
              $.session.model(),
            ])
            collector.applyUsage({
              percent: usage.context.percent ?? null,
              usd: usage.cost?.usd ?? null,
              model,
              agents,
            })
          } catch {}
        }

        if (collector.isDirty() || at - wrote >= BEAT_MS) {
          const text = collector.take(at)
          if (text) {
            wrote = at
            try {
              await $.fs.write(file, text)
            } catch {}
          }
        }

        if (!boardOpen || (!pollNow && tick % POLL_TICKS !== 0)) return
        pollNow = false
        const own = collector.current()

        // 1. Heartbeats the plugin wrote, this session's own from memory.
        let entries: { name: string; kind: string; mtimeMs: number }[] = []
        try {
          entries = await $.fs.list(dir)
        } catch {}
        const loaded = await Promise.all(
          entries
            .filter(f => f.kind === 'file' && f.name.endsWith('.json') && at - f.mtimeMs < KEEP_MS)
            .map(async f => {
              if (own && f.name === `${own.id}.json`) return own
              try {
                return parse((await $.fs.read(`${dir}/${f.name}`)) as string)
              } catch {
                return null
              }
            }),
        )
        const beats = new Map<string, Snapshot>()
        for (const s of loaded) if (s) beats.set(s.id, s)
        if (own) beats.set(own.id, own)

        // 2. The engine's registry of running sessions, alive by their pid.
        let regs: live.Reg[] = []
        try {
          const files = (await $.fs.list(regDir)).filter(f => f.kind === 'file' && f.name.endsWith('.json'))
          const found = await Promise.all(
            files.map(async f => {
              try {
                return live.parseReg((await $.fs.read(`${regDir}/${f.name}`)) as string)
              } catch {
                return null
              }
            }),
          )
          regs = found.filter((r): r is live.Reg => r !== null && (r.kind === undefined || r.kind === 'interactive' || r.kind === 'bg'))
        } catch {}
        if (regs.length > 0) {
          try {
            const ps = await $.process.run(['ps', '-o', 'pid=', '-p', regs.map(r => String(r.pid)).join(',')], { timeoutMs: 5000 })
            const alive = live.alivePids(ps.stdout)
            regs = regs.filter(r => alive.has(r.pid))
          } catch {
            regs = regs.filter(r => at - (r.updatedAt ?? r.startedAt) < 24 * 3600_000)
          }
        }

        // 3. Each running session's transcript tail, read again only when it grew.
        const tails = new Map<string, live.Tail>()
        await Promise.all(
          regs.map(async r => {
            const path = `${home ?? ''}/.claude/projects/${live.projectDir(r.cwd)}/${r.sessionId}.jsonl`
            try {
              const stat = await $.fs.stat(path)
              const key = `${stat.size}:${stat.mtimeMs}`
              const cached = tailCache.get(r.sessionId)
              if (cached && cached.key === key) return void tails.set(r.sessionId, cached.tail)
              const out = await $.process.run(['tail', '-c', String(live.TAIL_BYTES), path], { timeoutMs: 5000 })
              const tail = live.readTail(out.stdout, stat.size <= live.TAIL_BYTES)
              tailCache.set(r.sessionId, { key, tail })
              tails.set(r.sessionId, tail)
            } catch {}
          }),
        )

        const list: Snapshot[] = []
        const running = new Set<string>()
        for (const r of regs) {
          running.add(r.sessionId)
          const beat = beats.get(r.sessionId)
          const tail = tails.get(r.sessionId) ?? null
          list.push(beat ? live.overlay(beat, r, tail, at) : live.fromLive(r, tail, at))
        }
        for (const [id, s] of beats) if (!running.has(id)) list.push(s)
        for (const id of tailCache.keys()) if (!running.has(id)) tailCache.delete(id)

        for (const text of transitions(list, own?.id ?? '')) $.ui.toast(text)
        $.ui.status(statusLine(list, at, own?.id ?? ''))

        const stored = await $.store.get('hidden')
        const hidden = Array.isArray(stored) ? (stored as string[]) : []
        const data: BoardData = { at, self: own?.id ?? '', list: structuredClone(list), hidden }
        await update($, boardAtom, () => data)
      })()
    })

    return next(e)
  })

  on('command.run', { command: 'board' }, async ($, e) => {
    const arg = String(e.args ?? '').trim()
    if (VIEWS.has(arg)) await update($, uiAtom, ui => ({ ...ui, view: arg as ViewState['view'] }))
    const opened = await $.ui.open({ id: PANE, title: 'Session Board' })
    boardOpen = true
    pollNow = true

    return {
      text: opened.isPlaced ? 'Session Board를 열었습니다.' : `Session Board를 열지 못했습니다: ${opened.reason}`,
    }
  })

  on('ui.close', async ($, e, next) => {
    if (e.id === PANE) {
      boardOpen = false
      seen = new Map()
      $.ui.status(undefined)
    }
    return next(e)
  })

  on('session.end', async ($, e, next) => {
    ticker?.cancel()
    ticker = null
    const now = await $.clock.now()
    collector.setStatus('ended', now)
    const snap = collector.current()
    if (snap) snap.tool = null
    const text = collector.take(now)
    if (text && file) {
      try {
        await $.fs.write(file, text)
      } catch {}
    }
    return next(e)
  })

  on('turn.start', async ($, e, next) => {
    if ((e as { agentId?: string }).agentId === undefined) collector.prompted(e.text, e.turnId, await $.clock.now())
    return next(e)
  })

  on('tool.check', async ($, e, next) => {
    const verdict = await next(e)
    if (verdict.decision === 'ask' && (e as { agentId?: string }).agentId === undefined && collector.current()) {
      const label = toolLabel(e.tool, (e.input ?? {}) as Record<string, unknown>)
      collector.asked(e.tool_use_id, label, await $.clock.now())
    }
    return verdict
  })

  on('tool.call', async ($, e, next) => {
    const snap = collector.current()
    const input = e as unknown as Record<string, unknown>
    const main = e.agentId === undefined
    const label = toolLabel(e.tool, input)
    const kind: StepKind =
      AGENTS.has(e.tool) ? 'agent' : QUESTIONS.has(e.tool) ? 'question' : 'tool'
    if (snap) {
      const now = await $.clock.now()
      collector.addStep(
        { id: e.tool_use_id, kind, label, state: kind === 'question' ? 'wait' : 'run', ...(main ? {} : { agent: e.agentId }) },
        now,
      )
      collector.trackTodos(e.tool, input)
      if (EDITS.has(e.tool)) {
        const path = input.file_path ?? input.notebook_path
        if (typeof path === 'string') collector.touch(path)
      }
      if (main) {
        snap.tool = label
        collector.setStatus(kind === 'question' ? 'question' : 'working', now)
      }
    }
    let failed = true
    try {
      const ran = await next(e)
      failed = ran.isError === true || ran.deny !== undefined
      return ran
    } finally {
      if (snap) {
        const now = await $.clock.now()
        collector.endStep(e.tool_use_id, failed ? 'fail' : 'ok', now)
        if (main) {
          snap.tool = null
          if (snap.status === 'question' || snap.status === 'permission') collector.setStatus('working', now)
        }
      }
    }
  })

  on('turn.complete', async ($, e, next) => {
    const done = await next(e)
    if (e.agentId === undefined && collector.current()) {
      collector.answered(
        {
          answer: e.answer,
          turnId: e.turnId,
          durationMs: e.durationMs,
          failed: e.reason === 'error',
          aborted: e.isAborted,
        },
        await $.clock.now(),
      )
      try {
        const [usage, agents, model] = await Promise.all([$.session.usage(), $.agent.list(), $.session.model()])
        collector.applyUsage({ percent: usage.context.percent ?? null, usd: usage.cost?.usd ?? null, model, agents })
      } catch {}
    }
    return done
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const kit = $.ui.resolve(e)
    const [data, ui] = await Promise.all([read($, boardAtom), read($, uiAtom)])
    const act: Act = {
      ui: fields => void update($, uiAtom, now => ({ ...now, ...fields })),
      hide: ids =>
        void (async () => {
          const stored = await $.store.get('hidden')
          const before = Array.isArray(stored) ? (stored as string[]) : []
          const hidden = [...new Set([...before, ...ids])].slice(-500)
          await $.store.set('hidden', hidden)
          await update($, boardAtom, d => ({ ...d, hidden }))
        })(),
      send: (s, text) =>
        void (async () => {
          const body = text.trim()
          if (!body) return
          try {
            const sent = await $.session.send({ to: { sessionId: s.id }, text: body })
            $.ui.toast(sent.isDelivered ? `→ ${cut(s.title || s.project, 30)}에 보냈습니다` : `전송 실패: ${sent.reason}`)
          } catch (err) {
            $.ui.toast(`전송 실패: ${String(err)}`)
          }
        })(),
    }

    return view(act, kit, data, ui, e.props.bodyColumns)
  })
}
