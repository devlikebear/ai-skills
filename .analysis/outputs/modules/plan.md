# 모듈: plan

요청을 실행 가능한 작업 지시서(Work Order)로 분할하는 스킬.

## 역할

사용자의 요청을 분석하여 최대 3개의 작업 지시서로 나눕니다. 각 WO는 30-90분, 최대 5개 터치포인트로 범위가 제한됩니다.

## 핵심 파일

| 파일 | 역할 |
|------|------|
| `claude-code/plugin/skills/plan/SKILL.md` | Claude Code 스킬 |
| `codex/skills/plan-for-codex/SKILL.md` | Codex 스킬 |
| `references/work-order.md` | 작업 지시서 템플릿 |

## 워크플로

1. 요청의 명시적 제약 조건 파악
2. ≤3개 작업 지시서로 분할
3. 측정 가능한 수락 기준 작성
4. 검증 명령 포함
5. API 변경/광범위 리팩토링은 차단 표시

## 출력

- 계획 요약 + 작업 지시서 1-3개 + `/implement` 제안
