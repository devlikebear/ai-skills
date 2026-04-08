# 모듈: implement

승인된 작업 지시서를 직접 실행하는 스킬.

## 역할

plan 스킬이 생성한 작업 지시서(WO)를 하나씩 실행합니다. 범위를 WO 내로 엄격히 제한하며, 범위가 확장되면 중단하고 보고합니다.

## 핵심 파일

| 파일 | 역할 |
|------|------|
| `claude-code/plugin/skills/implement/SKILL.md` | Claude Code 스킬 |
| `codex/skills/implement/SKILL.md` | Codex 스킬 |
| `references/work-order.md` | 작업 지시서 템플릿 |

## 워크플로

1. 구현 목표 1-2문장으로 재서술
2. WO 확인 또는 재작성
3. 범위: 1개 작업 단위, 30-90분, ≤5개 터치포인트
4. 직접 구현
5. 검증 실패 시 최대 2회 재시도
6. 범위 확대 시 즉시 중단

## 규칙

- 최소 변경 선호
- 비목표(non-goals)는 절대 제약 조건
- 검증 명령 실행 필수
