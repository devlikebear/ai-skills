import type { Lane, Snapshot, Status, Step } from '../types'

/** A heartbeat older than this means the session's process is gone. */
export const STALE_MS = 90_000

export const LANES: readonly Lane[] = ['needs', 'working', 'review', 'done']

export const LANE_LABEL: Record<Lane, string> = {
  needs: '나를 기다림',
  working: '작업 중',
  review: '리뷰',
  done: '완료',
}

export const LANE_COLOR: Record<Lane, string> = {
  needs: 'warning',
  working: 'claude',
  review: 'success',
  done: 'inactive',
}

export const STATUS_LABEL: Record<Status, string> = {
  working: '작업 중',
  permission: '권한 요청',
  question: '답변 대기',
  idle: '응답 완료',
  error: '오류',
  ended: '종료',
}

export const STATUS_COLOR: Record<Status, string> = {
  working: 'claude',
  permission: 'warning',
  question: 'warning',
  idle: 'success',
  error: 'error',
  ended: 'inactive',
}

export const isStale = (s: Snapshot, now: number) =>
  s.status !== 'ended' && now - s.beat > STALE_MS

export const laneOf = (s: Snapshot, now: number): Lane => {
  if (isStale(s, now)) return 'done'
  switch (s.status) {
    case 'working':
      return 'working'
    case 'permission':
    case 'question':
    case 'error':
      return 'needs'
    case 'idle':
      return 'review'
    default:
      return 'done'
  }
}

export const statusText = (s: Snapshot, now: number) =>
  isStale(s, now) ? '연결 끊김' : STATUS_LABEL[s.status]

export const statusColor = (s: Snapshot, now: number) =>
  isStale(s, now) ? 'inactive' : STATUS_COLOR[s.status]

export const ago = (ms: number) => {
  const s = Math.max(0, Math.round(ms / 1000))
  if (s < 60) return `${s}s`
  const m = Math.round(s / 60)
  if (m < 60) return `${m}m`
  const h = Math.round(m / 60)
  if (h < 48) return `${h}h`
  return `${Math.round(h / 24)}d`
}

export const dur = (ms: number | undefined) => {
  if (ms === undefined) return ''
  if (ms < 1000) return `${ms}ms`
  if (ms < 60_000) return `${(ms / 1000).toFixed(1)}s`
  return ago(ms)
}

export const cut = (text: string, n: number) => {
  const one = text.replace(/\s+/g, ' ').trim()
  return one.length > n ? `${one.slice(0, Math.max(1, n - 1))}…` : one
}

/** Cells a code point takes on a terminal: two for Hangul, CJK, fullwidth and emoji. */
const isWide = (cp: number) =>
  cp >= 0x1100 &&
  (cp <= 0x115f ||
    (cp >= 0x2e80 && cp <= 0xa4cf && cp !== 0x303f) ||
    (cp >= 0xac00 && cp <= 0xd7a3) ||
    (cp >= 0xf900 && cp <= 0xfaff) ||
    (cp >= 0xfe30 && cp <= 0xfe4f) ||
    (cp >= 0xff00 && cp <= 0xff60) ||
    (cp >= 0xffe0 && cp <= 0xffe6) ||
    (cp >= 0x1f300 && cp <= 0x1f64f) ||
    (cp >= 0x1f900 && cp <= 0x1f9ff) ||
    (cp >= 0x20000 && cp <= 0x3fffd))

export const cells = (text: string) => {
  let n = 0
  for (const ch of text) n += isWide(ch.codePointAt(0)!) ? 2 : 1
  return n
}

/** Cuts `text` to at most `room` terminal cells, ending in … when cut. */
export const fit = (text: string, room: number) => {
  const one = text.replace(/\s+/g, ' ').trim()
  if (cells(one) <= room) return one
  let out = ''
  let used = 0
  for (const ch of one) {
    const w = isWide(ch.codePointAt(0)!) ? 2 : 1
    if (used + w > room - 1) break
    out += ch
    used += w
  }
  return `${out}…`
}

export const firstLine = (text: string) => {
  for (const raw of text.split('\n')) {
    const line = raw.replace(/^[#>*\-\s`]+/, '').trim()
    if (line.length > 0) return line
  }
  return ''
}

export const base = (path: string) => path.split('/').filter(Boolean).at(-1) ?? path

/** A ten-cell meter, ▰ filled and ▱ empty. */
export const meter = (percent: number, cells = 10) => {
  const filled = Math.max(0, Math.min(cells, Math.round((percent / 100) * cells)))
  return '▰'.repeat(filled) + '▱'.repeat(cells - filled)
}

export const ctxColor = (percent: number) =>
  percent >= 85 ? 'error' : percent >= 60 ? 'warning' : 'success'

const str = (v: unknown) => (typeof v === 'string' ? v : '')

/** A short label for a tool call: `Edit auth.ts`, `Bash npm test`, `github·create_pr`. */
export const toolLabel = (tool: string, input: Record<string, unknown>): string => {
  const path = str(input.file_path) || str(input.notebook_path) || str(input.path)
  switch (tool) {
    case 'Read':
    case 'Edit':
    case 'MultiEdit':
    case 'Write':
    case 'NotebookEdit':
      return path ? `${tool} ${base(path)}` : tool
    case 'Bash':
      return `Bash ${cut(str(input.description) || str(input.command), 48)}`
    case 'Grep':
    case 'Glob':
      return `${tool} ${cut(str(input.pattern), 40)}`
    case 'WebFetch':
      return `WebFetch ${cut(str(input.url).replace(/^https?:\/\//, ''), 40)}`
    case 'WebSearch':
      return `WebSearch ${cut(str(input.query), 40)}`
    case 'Agent':
    case 'Task':
      return `${str(input.subagent_type) || 'agent'}: ${cut(str(input.description), 40)}`
    case 'Skill':
      return `Skill ${str(input.skill)}`
    default:
      if (tool.startsWith('mcp__')) {
        const [, server = '', name = ''] = tool.split('__')
        return `${server.length > 12 ? server.slice(0, 8) : server}·${name}`
      }
      return tool
  }
}

export const GLYPH: Record<Step['kind'], string> = {
  prompt: '›',
  tool: '●',
  agent: '◆',
  permission: '◉',
  question: '?',
  answer: '✓',
  error: '✕',
}

export const stepColor = (step: Step): string => {
  if (step.state === 'fail' || step.kind === 'error') return 'error'
  if (step.state === 'wait') return 'warning'
  if (step.state === 'run') return 'claude'
  if (step.kind === 'answer') return 'success'
  if (step.kind === 'agent') return 'suggestion'
  if (step.kind === 'prompt') return 'text'
  return 'subtle'
}

/** Sort key: what needs the person first, then the freshest. */
export const byAttention = (now: number) => (a: Snapshot, b: Snapshot) => {
  const rank = (s: Snapshot) => LANES.indexOf(laneOf(s, now))
  return rank(a) - rank(b) || b.since - a.since
}
