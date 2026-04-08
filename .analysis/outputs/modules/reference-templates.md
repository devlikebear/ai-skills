# 모듈: reference-templates

스킬들이 참조하는 14개 레퍼런스 템플릿 모음.

## 역할

스킬이 생성하는 출력물(작업 지시서, 체크리스트, 제안서)의 표준 형식을 정의합니다.

## 핵심 파일

| 파일 | 사용 스킬 | 내용 |
|------|-----------|------|
| `work-order.md` | plan, implement, review | 작업 지시서 기본 형식 |
| `refactor-work-order.md` | refactor | 리팩토링 전용 WO 형식 |
| `review-checklist.md` | review | 리뷰 체크리스트 |
| `refactoring-checklist.md` | refactor | 리팩토링 안전 체크리스트 |
| `refactoring-patterns.md` | refactor | 리팩토링 패턴 선택 가이드 |
| `refactor-template.md` | source-analyzer (refactor-guide) | 리팩토링 작업 지시서 전체 구조 |
| `overhaul-template.md` | source-analyzer (overhaul) | 시스템 오버홀 제안서 구조 |
| `tutorial-template.md` | source-analyzer (analyze) | 튜토리얼/클론코딩 구조 |
| `checkpoint-template.md` | source-analyzer | 수동 체크포인트 폴백 |
| `tidy-first-rules.md` | source-analyzer (refactor-guide) | TIDY 규칙 매핑 |
| `security-triage-checklist.md` | source-analyzer (refactor-guide) | 보안 분류 체크리스트 |
| `github-flow-checklist.md` | github-flow | 단계별 체크리스트 |

## 배포 위치

- Claude Code: `claude-code/plugin/references/`
- Codex: 각 스킬의 `shared/references/`
