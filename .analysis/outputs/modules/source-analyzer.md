# 모듈: source-analyzer

## 역할

기존 코드베이스를 수정하지 않고 읽어서 입문자용 구조 문서와 후속 리팩터링 입력을 만드는 분석 스킬이다.

## 핵심 경로

- Codex: `codex/skills/source-analyzer/SKILL.md`
- Codex 참조: `codex/skills/source-analyzer/shared/references/*`
- Codex 스크립트: `codex/skills/source-analyzer/shared/scripts/checkpoint_manager.py`
- Claude Code 플러그인: `claude-code/plugin/skills/source-analyzer/SKILL.md`
- 플러그인 스크립트: `claude-code/plugin/scripts/checkpoint_manager.py`
- 분석 산출물: `.analysis/outputs/*`

## 동작 모드

| 모드 | 목적 | 핵심 산출물 |
|------|------|-------------|
| `analyze` | 입문자용 구조 문서 생성 | `overview.md`, `architecture.md`, `modules/*.md`, `tutorial.md` |
| `refactor-guide` | 수정 작업 지시서 생성 | `DUP-*`, `SEC-*`, `TIDY-*` 코드가 붙은 리팩터링 가이드 |

## 현재 버전에서 중요한 점

`0.6.x` 기준으로 이 스킬은 세션 작업 디렉터리와 안정 산출물 디렉터리를 분리한다.

1. 작업 중 상태는 `.analysis/sessions/<session-id>/`에 남긴다.
2. `paused` 또는 `completed` 체크포인트에서 산출물을 `.analysis/outputs/`로 publish한다.
3. `SUMMARY.json`, `dependency-graph.json`, `module-map.json`, `issue-candidates.md`, `AI_CONTEXT.md`를 후속 AI 입력으로 남긴다.
4. `migrate` 명령으로 pre-0.6.0 세션 레이아웃도 새 구조로 끌어올릴 수 있다.

## checkpoint_manager.py 요약

현재 스크립트는 `init`, `sync`, `checkpoint`, `status`, `generate-summary`, `publish`, `migrate` 일곱 가지 CLI 진입점을 제공한다.

- `init`: 세션 디렉터리와 `state.json`, `index.md`, `RESUME.md`를 만든다.
- `sync`: 새 커밋이 생겼는지 확인하고 변경 파일을 frontier에 추가한다.
- `checkpoint`: 방문 파일, 남은 frontier, 생성 문서를 기록한다.
- `status`: 세션 상태를 사람이 읽기 좋은 텍스트로 출력한다.
- `generate-summary`: 모듈 요약 JSON을 만든다.
- `publish`: 세션 산출물을 `.analysis/outputs/`로 복사한다.
- `migrate`: 구형 세션 출력만 있는 레이아웃을 새 publish 구조로 복사한다.

## 세션 산출물

- `.analysis/sessions/<session-id>/state.json`: 세션의 단일 진실 공급원이다.
- `.analysis/sessions/<session-id>/index.md`: 체크포인트 목록이다.
- `.analysis/sessions/<session-id>/checkpoints/checkpoint-XXX.md`: 청크별 진행 로그다.
- `.analysis/sessions/<session-id>/outputs/*`: 작업 중 문서와 구조 JSON이다.
- `.analysis/outputs/*`: publish된 안정 결과다.
- `.analysis/AI_CONTEXT.md`: 다른 AI 에이전트를 위한 진입점이다.

## 입문자가 볼 파일 순서

1. `codex/skills/source-analyzer/SKILL.md`
2. `codex/skills/source-analyzer/shared/references/tutorial-template.md`
3. `codex/skills/source-analyzer/shared/scripts/checkpoint_manager.py`
4. `tests/test_checkpoint_manager.py`

## 주의할 점

- 이 스킬은 항상 `git ls-tree -r HEAD --name-only` 기준으로 커밋된 파일만 분석한다.
- Codex와 Claude Code 배포본의 `checkpoint_manager.py`는 현재 동일 파일이므로, 한쪽만 수정하면 배포가 바로 어긋난다.
