import type { ElementTable } from 'claude-code'

import type { BoardData, Lane, Snapshot, Step, ViewState } from '../types'
import {
  GLYPH,
  LANES,
  LANE_COLOR,
  LANE_LABEL,
  ago,
  base,
  byAttention,
  ctxColor,
  cut,
  dur,
  fit,
  isStale,
  laneOf,
  meter,
  statusColor,
  statusText,
  stepColor,
} from './util'

type Kit = ElementTable

/** What the drawing may do: closures the render hook makes over its own `$`. */
export type Act = {
  ui: (fields: Partial<ViewState>) => void
  hide: (ids: string[]) => void
  send: (s: Snapshot, text: string) => void
}

type Ctx = {
  act: Act
  kit: Kit
  data: BoardData
  ui: ViewState
  width: number
  now: number
}

const titleOf = (s: Snapshot) => s.title || cut(s.prompt, 70) || '새 세션'

const visible = (c: Ctx) =>
  c.data.list
    .filter(s => !c.data.hidden.includes(s.id) && (s.turns > 0 || s.id === c.data.self))
    .sort(byAttention(c.now))

// ── shared bits ────────────────────────────────────────────────────────────

const header = (c: Ctx, all: Snapshot[]) => {
  const { Box, Text, Button } = c.kit
  const counts = LANES.filter(l => l !== 'done')
    .map(l => [l, all.filter(s => laneOf(s, c.now) === l).length] as const)
    .filter(([, n]) => n > 0)
  const tab = (view: ViewState['view'], label: string, hotkey: string) => (
    <Button
      key={`tab-${view}`}
      label={label}
      hotkey={hotkey}
      variant={c.ui.view === view ? 'primary' : 'secondary'}
      dimColor={c.ui.view !== view}
      onPress={() => c.act.ui({ view })}
    />
  )

  return (
    <Box flexDirection="row" justifyContent="space-between" flexWrap="wrap" columnGap={2}>
      <Box flexDirection="row" gap={1}>
        {tab('board', '보드', '1')}
        {tab('flow', '워크플로우', '2')}
        {tab('detail', '상세', '3')}
      </Box>
      <Box flexDirection="row" gap={2}>
        {counts.length === 0 && <Text dimColor>활성 세션 없음</Text>}
        {counts.map(([lane, n]) => (
          <Text color={LANE_COLOR[lane]}>
            ● {LANE_LABEL[lane]} <Text bold>{String(n)}</Text>
          </Text>
        ))}
      </Box>
    </Box>
  )
}

const empty = (c: Ctx) => {
  const { Box, Text } = c.kit

  return (
    <Box flexDirection="column" paddingY={1} alignItems="center">
      <Text dimColor>아직 기록된 세션이 없습니다.</Text>
      <Text dimColor>session-board가 켜진 세션이 시작되면 여기에 나타납니다.</Text>
    </Box>
  )
}

const meters = (c: Ctx, s: Snapshot) => {
  const { Box, Text } = c.kit
  const done = s.todos.filter(t => t.state === 'completed').length
  const running = s.agents.filter(a => a.status === 'running' || a.status === 'pending').length

  return (
    <Box flexDirection="row" columnGap={2} flexWrap="wrap">
      {s.ctx !== null && (
        <Text color={ctxColor(s.ctx)}>
          {meter(s.ctx, 6)} <Text dimColor>{`${Math.round(s.ctx)}%`}</Text>
        </Text>
      )}
      {s.todos.length > 0 && (
        <Text dimColor={done < s.todos.length} color={done === s.todos.length ? 'success' : undefined}>
          ☑ {`${done}/${s.todos.length}`}
        </Text>
      )}
      {running > 0 && <Text color="suggestion">◆ {String(running)}</Text>}
      {s.cost !== null && s.cost > 0 && <Text dimColor>{`$${s.cost.toFixed(2)}`}</Text>}
    </Box>
  )
}

// ── board ──────────────────────────────────────────────────────────────────

const card = (c: Ctx, s: Snapshot, width: number) => {
  const { Box, Text, Button } = c.kit
  const self = s.id === c.data.self
  const color = statusColor(s, c.now)
  const inner = Math.max(8, width - 4)
  const where = [s.project, s.branch ? `⎇ ${s.branch}` : ''].filter(Boolean).join('  ')
  const line = s.tool ? `▸ ${s.tool}` : s.summary

  return (
    <Box
      key={`card-${s.id}`}
      flexDirection="column"
      borderStyle="round"
      borderColor={c.ui.selected === s.id ? color : 'subtle'}
      hover={{ borderColor: color }}
      paddingX={1}
      width={width}
    >
      <Box flexDirection="row" justifyContent="space-between">
        <Text color={color}>● {statusText(s, c.now)}</Text>
        <Text dimColor>{self ? `이 세션 · ${ago(c.now - s.since)}` : ago(c.now - s.since)}</Text>
      </Box>
      <Button
        key={`open-${s.id}`}
        label={fit(titleOf(s), inner)}
        plain
        onPress={() => c.act.ui({ view: 'detail', selected: s.id })}
      />
      {where && (
        <Text dimColor wrap="truncate-end">
          {fit(where, inner)}
        </Text>
      )}
      {line && (
        <Text color={s.tool ? 'claude' : undefined} dimColor={!s.tool} wrap="truncate-end">
          {fit(line, inner)}
        </Text>
      )}
      {meters(c, s)}
    </Box>
  )
}

const column = (c: Ctx, lane: Lane, items: Snapshot[], width: number) => {
  const { Box, Text, Button } = c.kit
  const capped = lane === 'done' && !c.ui.showDone
  const shown = capped ? items.slice(0, 3) : items

  return (
    <Box flexDirection="column" width={width} gap={0}>
      <Box flexDirection="row" justifyContent="space-between" paddingX={1}>
        <Text color={LANE_COLOR[lane]} bold>
          {LANE_LABEL[lane]} <Text dimColor>{String(items.length)}</Text>
        </Text>
        {lane === 'done' && items.length > 0 && (
          <Button
            key="clear-done"
            plain
            dimColor
            label="정리"
            onPress={() => c.act.hide(items.map(s => s.id))}
          />
        )}
      </Box>
      {items.length === 0 && (
        <Box paddingX={1}>
          <Text dimColor>—</Text>
        </Box>
      )}
      {shown.map(s => card(c, s, width))}
      {capped && items.length > shown.length && (
        <Button
          key="more-done"
          plain
          dimColor
          label={`+ ${items.length - shown.length}개 더 보기`}
          onPress={() => c.act.ui({ showDone: true })}
        />
      )}
      {lane === 'done' && c.ui.showDone && items.length > 3 && (
        <Button
          key="less-done"
          plain
          dimColor
          label="접기"
          onPress={() => c.act.ui({ showDone: false })}
        />
      )}
    </Box>
  )
}

const board = (c: Ctx, all: Snapshot[]) => {
  const { Box } = c.kit
  const byLane = (lane: Lane) => all.filter(s => laneOf(s, c.now) === lane)
  const cols = c.width >= 120 ? 4 : c.width >= 60 ? 2 : 1
  const gap = 1
  const w = Math.floor((c.width - gap * (cols - 1)) / cols)
  const rows: Lane[][] = []
  for (let i = 0; i < LANES.length; i += cols) rows.push(LANES.slice(i, i + cols) as Lane[])

  return (
    <Box flexDirection="column" gap={1}>
      {rows.map(row => (
        <Box flexDirection="row" gap={gap} alignItems="flex-start">
          {row.map(lane => column(c, lane, byLane(lane), w))}
        </Box>
      ))}
    </Box>
  )
}

// ── workflow ───────────────────────────────────────────────────────────────

const chain = (c: Ctx, steps: Step[], room: number) => {
  const { Box, Text } = c.kit
  const tail = steps.slice(-Math.max(4, Math.min(40, Math.floor(room / 2))))

  return (
    <Box flexDirection="row" columnGap={1}>
      {tail.map(step => (
        <Text color={stepColor(step)} dimColor={step.state === 'ok' && step.kind === 'tool'}>
          {GLYPH[step.kind]}
        </Text>
      ))}
    </Box>
  )
}

const lanesFlow = (c: Ctx, all: Snapshot[]) => {
  const { Box, Text, Button } = c.kit
  const name = Math.min(28, Math.max(12, Math.floor(c.width * 0.3)))
  const room = c.width - name - 14

  return (
    <Box flexDirection="column" gap={0}>
      {all.map(s => (
        <Box key={`lane-${s.id}`} flexDirection="row" gap={1} hover={{ backgroundColor: 'subtle' }}>
          <Text color={statusColor(s, c.now)}>●</Text>
          <Box width={name}>
            <Button
              key={`flow-${s.id}`}
              label={fit(titleOf(s), name - 1)}
              plain
              onPress={() => c.act.ui({ view: 'flow', selected: s.id })}
            />
          </Box>
          <Box flexGrow={1}>{chain(c, s.steps, room)}</Box>
          <Text dimColor>{ago(c.now - s.since)}</Text>
        </Box>
      ))}
      <Box marginTop={1} flexDirection="row" columnGap={2} flexWrap="wrap">
        {(
          [
            ['prompt', '프롬프트'],
            ['tool', '도구'],
            ['agent', '서브에이전트'],
            ['permission', '권한'],
            ['question', '질문'],
            ['answer', '답변'],
            ['error', '오류'],
          ] as const
        ).map(([kind, label]) => (
          <Text dimColor>
            {GLYPH[kind]} {label}
          </Text>
        ))}
      </Box>
    </Box>
  )
}

const stepRow = (c: Ctx, step: Step, last: boolean) => {
  const { Box, Text } = c.kit
  const branch = step.agent ? '│  ' : ''
  const elbow = last ? '└─' : '├─'
  const time = step.state === 'run' ? '실행 중' : step.state === 'wait' ? '대기 중' : dur(step.ms)

  return (
    <Box flexDirection="row" gap={1}>
      <Text dimColor>{`${branch}${elbow}`}</Text>
      <Text color={stepColor(step)}>{GLYPH[step.kind]}</Text>
      <Box flexGrow={1} flexShrink={1}>
        <Text wrap="truncate-end" dimColor={step.state === 'ok' && step.kind === 'tool'}>
          {step.label}
        </Text>
      </Box>
      <Text dimColor color={step.state === 'run' ? 'claude' : undefined}>
        {time}
      </Text>
    </Box>
  )
}

const timeline = (c: Ctx, s: Snapshot, turns = 6) => {
  const { Box, Text } = c.kit
  const numbers = [...new Set(s.steps.map(st => st.turn))].slice(-turns)
  if (numbers.length === 0) return <Text dimColor>아직 활동이 없습니다.</Text>

  return (
    <Box flexDirection="column" gap={1}>
      {numbers.map(n => {
        const steps = s.steps.filter(st => st.turn === n)
        const prompt = steps.find(st => st.kind === 'prompt')
        const rest = steps.filter(st => st.kind !== 'prompt')
        const total = rest.find(st => st.kind === 'answer' || st.kind === 'error')?.ms

        return (
          <Box flexDirection="column">
            <Box flexDirection="row" gap={1}>
              <Text bold>{`턴 ${n}`}</Text>
              <Box flexGrow={1} flexShrink={1}>
                <Text dimColor wrap="truncate-end">
                  {prompt ? `› ${prompt.label}` : ''}
                </Text>
              </Box>
              <Text dimColor>{total !== undefined ? dur(total) : ''}</Text>
            </Box>
            {rest.map((st, i) => stepRow(c, st, i === rest.length - 1))}
          </Box>
        )
      })}
    </Box>
  )
}

// ── detail ─────────────────────────────────────────────────────────────────

const nav = (c: Ctx, all: Snapshot[], s: Snapshot) => {
  const { Box, Text, Button } = c.kit
  const i = all.findIndex(one => one.id === s.id)
  const go = (d: number) => () => {
    const next = all[(i + d + all.length) % all.length]
    if (next) c.act.ui({ selected: next.id })
  }

  return (
    <Box flexDirection="row" justifyContent="space-between" flexWrap="wrap">
      <Box flexDirection="row" gap={1}>
        <Button key="prev" label="‹" hotkey="k" plain onPress={go(-1)} />
        <Text dimColor>{`${i + 1} / ${all.length}`}</Text>
        <Button key="next" label="›" hotkey="j" plain onPress={go(1)} />
      </Box>
      <Box flexDirection="row" gap={1}>
        {c.ui.view === 'flow' ? (
          <Button key="to-detail" plain label="상세" onPress={() => c.act.ui({ view: 'detail' })} />
        ) : (
          <Button key="to-flow" plain label="워크플로우" onPress={() => c.act.ui({ view: 'flow' })} />
        )}
        {c.ui.view === 'flow' && (
          <Button key="all-flow" plain label="전체" onPress={() => c.act.ui({ selected: null })} />
        )}
        {s.id !== c.data.self && (laneOf(s, c.now) === 'done' || laneOf(s, c.now) === 'review') && (
          <Button key="hide" plain dimColor label="숨기기" onPress={() => c.act.hide([s.id])} />
        )}
      </Box>
    </Box>
  )
}

const section = (c: Ctx, title: string, body: unknown, aside?: string) => {
  const { Box, Text } = c.kit

  return (
    <Box flexDirection="column">
      <Box flexDirection="row" gap={1}>
        <Text bold dimColor>
          {title}
        </Text>
        {aside && <Text dimColor>{aside}</Text>}
      </Box>
      {body as never}
    </Box>
  )
}

const fact = (c: Ctx, label: string, value: string, color?: string) => {
  const { Box, Text } = c.kit

  return (
    <Box flexDirection="row" gap={1}>
      <Box width={9} flexShrink={0}>
        <Text dimColor>{label}</Text>
      </Box>
      <Box flexShrink={1}>
        <Text color={color} wrap="truncate-middle">
          {value}
        </Text>
      </Box>
    </Box>
  )
}

const detail = (c: Ctx, all: Snapshot[], s: Snapshot) => {
  const { Box, Text, Markdown } = c.kit
  const Input = 'Input' in c.kit ? c.kit.Input : null
  const color = statusColor(s, c.now)
  const done = s.todos.filter(t => t.state === 'completed').length
  const canSend = s.id !== c.data.self && s.status !== 'ended' && !isStale(s, c.now)

  return (
    <Box flexDirection="column" gap={1}>
      {nav(c, all, s)}
      <Box flexDirection="column">
        <Text bold wrap="wrap">
          {titleOf(s)}
        </Text>
        <Text wrap="truncate-end">
          <Text color={color}>● {statusText(s, c.now)}</Text>
          <Text dimColor>{` · ${ago(c.now - s.since)} 전부터`}</Text>
        </Text>
        {s.tool && (
          <Text color="claude" wrap="truncate-end">
            ▸ {s.tool}
          </Text>
        )}
      </Box>
      <Box flexDirection="column">
        {fact(c, '프로젝트', s.branch ? `${s.project}  ⎇ ${s.branch}` : s.project)}
        {fact(c, '경로', s.cwd)}
        {fact(c, '모델', s.model)}
        {fact(c, '시작', `${ago(c.now - s.startedAt)} 전 · ${s.turns}턴${s.surface ? ` · ${s.surface}` : ''}`)}
        {s.ctx !== null && fact(c, '컨텍스트', `${meter(s.ctx, 12)} ${Math.round(s.ctx)}%`, ctxColor(s.ctx))}
        {s.cost !== null && fact(c, '비용', `$${s.cost.toFixed(2)}`)}
      </Box>
      {canSend &&
        Input &&
        section(
          c,
          '메시지',
          <Input
            key={`msg-${s.id}`}
            placeholder="이 세션에 메시지 보내기…"
            submitLabel="보내기"
            onSubmit={value => c.act.send(s, value)}
          />,
        )}
      {s.answer &&
        section(
          c,
          '마지막 답변',
          <Box borderStyle="round" borderColor="subtle" paddingX={1}>
            <Markdown text={s.answer} />
          </Box>,
        )}
      {s.todos.length > 0 &&
        section(
          c,
          '할 일',
          <Box flexDirection="column">
            {s.todos.map(t => (
              <Text
                color={t.state === 'in_progress' ? 'claude' : undefined}
                dimColor={t.state === 'completed'}
                strikethrough={t.state === 'completed'}
                wrap="truncate-end"
              >
                {t.state === 'completed' ? '✓' : t.state === 'in_progress' ? '◐' : '○'} {t.text}
              </Text>
            ))}
          </Box>,
          `${done}/${s.todos.length}`,
        )}
      {s.agents.length > 0 &&
        section(
          c,
          '서브에이전트',
          <Box flexDirection="column">
            {s.agents.map(a => (
              <Box flexDirection="row" gap={1}>
                <Text color={a.status === 'running' ? 'suggestion' : a.status === 'failed' ? 'error' : 'subtle'}>◆</Text>
                <Text bold>{a.type}</Text>
                <Box flexGrow={1} flexShrink={1}>
                  <Text dimColor wrap="truncate-end">
                    {a.description}
                  </Text>
                </Box>
                <Text dimColor>{a.status}</Text>
              </Box>
            ))}
          </Box>,
        )}
      {s.files.length > 0 &&
        section(
          c,
          '변경 파일',
          <Box flexDirection="column">
            {s.files.slice(0, 12).map(f => (
              <Box flexDirection="row" gap={1}>
                <Text>{base(f)}</Text>
                <Box flexShrink={1}>
                  <Text dimColor wrap="truncate-start">
                    {f.startsWith(s.cwd) ? f.slice(s.cwd.length + 1).split('/').slice(0, -1).join('/') : f}
                  </Text>
                </Box>
              </Box>
            ))}
          </Box>,
          s.files.length > 12 ? `+${s.files.length - 12}` : String(s.files.length),
        )}
      {section(c, '최근 활동', timeline(c, s, 2))}
    </Box>
  )
}

// ── entry ──────────────────────────────────────────────────────────────────

export const view = (act: Act, kit: Kit, data: BoardData, ui: ViewState, width: number) => {
  const { Box } = kit
  const c: Ctx = { act, kit, data, ui, width: Math.max(24, width), now: data.at }
  const all = visible(c)
  const picked = all.find(s => s.id === ui.selected) ?? null
  let body: unknown
  if (all.length === 0) body = empty(c)
  else if (ui.view === 'board') body = board(c, all)
  else if (ui.view === 'flow')
    body = picked ? (
      <Box flexDirection="column" gap={1}>
        {nav(c, all, picked)}
        {timeline(c, picked)}
      </Box>
    ) : (
      lanesFlow(c, all)
    )
  else body = detail(c, all, picked ?? all[0]!)

  return (
    <Box flexDirection="column" gap={1}>
      {header(c, all)}
      {body as never}
    </Box>
  )
}
