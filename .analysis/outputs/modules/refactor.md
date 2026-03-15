# 모듈: refactor

## 역할

동작을 바꾸지 않고 구조만 개선하도록 유도하는 리팩터링 스킬이다.

## 핵심 경로

- Codex: `codex/skills/refactor/SKILL.md`
- Codex 참조: `codex/skills/refactor/shared/references/work-order.md`
- Codex 체크리스트: `codex/skills/refactor/shared/references/refactoring-checklist.md`
- Codex 패턴 가이드: `codex/skills/refactor/shared/references/refactoring-patterns.md`
- Claude Code 플러그인: `claude-code/plugin/skills/refactor/SKILL.md`

## 안전 장치

- 기능 추가 금지
- 공개 API 변경 금지
- 파일 접점 5개 이하 유지
- 단계마다 테스트 전후 비교

## 저장소에서의 의미

이 저장소는 구조적 일관성이 중요하다. `refactor` 스킬은 스킬 디렉터리, 공용 참조, 설치 스크립트, 테스트 사이의 중복을 줄일 때 사용하는 운영 도구에 가깝다.

## 입문자가 먼저 볼 파일

1. `codex/skills/refactor/SKILL.md`
2. `codex/skills/refactor/shared/references/refactoring-checklist.md`
3. `codex/skills/refactor/shared/references/refactoring-patterns.md`
