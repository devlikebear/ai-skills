# Source Analyzer Checkpoint Template

Use this template when the checkpoint script is unavailable.
Write one file per checkpoint:
`.analysis/sessions/<session-id>/checkpoints/checkpoint-XXX.md`
Write in the active skill language by default.

## Template

```markdown
# Checkpoint XXX: <작업 제목>

> Session / 세션: `<session-id>`
> Mode / 모드: `analyze | refactor-guide`
> Scope / 범위: `<진입점/파일/함수>`
> Status / 상태: `in_progress | paused | completed`
> Commit / 커밋: `<HEAD commit hash at checkpoint time>`
> Created At (UTC) / 생성 시각(UTC): `YYYY-MM-DDTHH:MM:SS+00:00`

## Summary / 요약

이번 체크포인트에서 무엇을 분석/정리했는지 2-4문장으로 작성.

## Newly Visited Nodes / 새로 방문한 노드

- `<새로 읽은 파일/모듈>`
- `<새로 읽은 파일/모듈>`

## Remaining Frontier / 남은 프런티어

- `<다음 BFS 대상>`
- `<다음 BFS 대상>`

## Produced or Updated Documents / 생성 또는 갱신한 문서

- `outputs/overview.md`
- `outputs/tutorial.md`
- `outputs/clone-coding.md`
- `outputs/implementation-checklist.md`
- `outputs/modules/<module>.md`
- `outputs/refactor-<target>.md`

## DUP/SEC/TIDY Progress / 진행 현황

- `DUP`: `<예: 2/5 이슈를 WO로 전환 완료>`
- `SEC`: `<예: 1/3 이슈에 완화 방향 정의>`
- `TIDY`: `<예: 3/4 이슈에 룰 매핑 완료>`

## Next Actions / 다음 작업

- `<다음 세션에서 시작할 작업>`
- `<다음 세션에서 시작할 작업>`

## Resume Instructions / 재개 지침

1. `index.md`에서 마지막 체크포인트 행을 확인한다.
2. `state.json.frontier`를 기준으로 BFS를 재개한다.
3. 미완료 `DUP/SEC/TIDY` 중 우선순위가 가장 높은 항목부터 재개한다.
4. 다음 진행 내용을 `checkpoint-(XXX+1).md`로 기록한다.
```

## Required companion updates
## 필수 동반 업데이트 / Required Companion Updates

When writing checkpoint markdown manually, also update:

1. `.analysis/sessions/<session-id>/state.json`
2. `.analysis/sessions/<session-id>/index.md`
3. `.analysis/RESUME.md`
