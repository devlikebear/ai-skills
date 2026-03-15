# 모듈: implement

## 역할

승인된 work order 하나를 받아 작고 검증 가능한 코드 변경으로 끝내는 실행 스킬이다.

## 핵심 경로

- Codex: `codex/skills/implement/SKILL.md`
- Codex 참조: `codex/skills/implement/shared/references/work-order.md`
- Codex 메타데이터: `codex/skills/implement/agents/openai.yaml`
- Claude Code 플러그인: `claude-code/plugin/skills/implement/SKILL.md`

## 책임

1. 구현 목표를 1-2문장으로 다시 적는다.
2. 범위를 하나의 작업 단위로 제한한다.
3. work order에 적힌 검증 명령을 실제로 실행한다.
4. 검증 실패가 국소적일 때만 좁게 재시도한다.

## 저장소 관점에서 중요한 이유

이 저장소의 다른 스킬들은 문서나 절차를 만든다. `implement`만 실제 파일 변경을 수행하므로, 다른 스킬과 비교해 가장 실행 지향적이다.

## 입문자가 먼저 볼 파일

1. `codex/skills/implement/SKILL.md`
2. `codex/skills/implement/agents/openai.yaml`
3. `claude-code/plugin/skills/implement/SKILL.md`
