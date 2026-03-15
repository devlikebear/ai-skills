# 모듈: plan

## 역할

사용자 요청을 바로 구현하지 않고, 작고 검증 가능한 work order로 나누는 스킬이다.

## 핵심 경로

- Codex: `codex/skills/plan-for-codex/SKILL.md`
- Codex 참조: `codex/skills/plan-for-codex/shared/references/work-order.md`
- Claude Code 플러그인: `claude-code/plugin/skills/plan/SKILL.md`
- 플러그인 참조: `claude-code/plugin/references/work-order.md`

## 책임

1. 요청의 명시적 제약을 추출한다.
2. 작업을 최대 3개의 work order로 분할한다.
3. 각 work order에 수용 기준과 검증 명령을 넣는다.
4. API 변경이나 큰 리팩터링은 명시 승인 없이는 막는다.

## Codex와 Claude Code의 차이

- Codex 스킬 이름은 `plan-for-codex`다.
- Claude Code 플러그인 명령은 `/code-workflow:plan`이다.
- 핵심 워크플로우는 같고, 호출 이름만 다르다.

## 입문자가 먼저 볼 파일

1. `codex/skills/plan-for-codex/SKILL.md`
2. `codex/skills/plan-for-codex/shared/references/work-order.md`
3. `claude-code/plugin/skills/plan/SKILL.md`

## 연결되는 다음 단계

이 스킬의 출력은 보통 `implement`나 `github-flow` Phase 2의 입력이 된다.
