# 모듈: refactor

동작 보존 리팩토링 스킬.

## 역할

기존 동작을 변경하지 않으면서 코드 구조를 개선합니다. source-analyzer의 `issue-candidates.md`와 연동하여 기존 분석 결과를 기반으로 리팩토링을 시작할 수 있습니다.

## ��심 파일

| 파일 | 역할 |
|------|------|
| `claude-code/plugin/skills/refactor/SKILL.md` | Claude Code 스킬 |
| `codex/skills/refactor/SKILL.md` | Codex 스킬 |
| `references/refactor-work-order.md` | 리팩토링 WO 형식 |
| `references/refactoring-checklist.md` | 안전 체크리스트 |
| `references/refactoring-patterns.md` | 패턴 선택 가이드 |

## Pre-flight

`.analysis/outputs/`가 있으면:
1. `issue-candidates.md` 읽고 이슈 제시
2. 기존 `refactor-*.md` WO 읽고 이어서 진행

## 안전 규칙

- 기능 변경 금지
- 공개 API 변경 금지 (명시적 승인 없이)
- 대규모 포맷 변경 금지
- 테스트를 항상 전후로 실행
