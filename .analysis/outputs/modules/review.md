# 모듈: review

diff 기반 코드 리뷰 스킬.

## 역할

코드 변경사항을 검토하여 회귀, 보안 이슈, 누락된 테스트를 찾습니다. 수정이 필요하면 구체적인 fix 작업 지시서를 생성합니다.

## 핵심 파일

| 파일 | 역할 |
|------|------|
| `claude-code/plugin/skills/review/SKILL.md` | Claude Code 스킬 |
| `codex/skills/review/SKILL.md` | Codex 스킬 |
| `references/review-checklist.md` | 리뷰 체크리스트 |
| `references/work-order.md` | fix WO 템플릿 |

## 출력

- 판정: OK / Needs changes / Blocking
- 파일+라인 참조가 포함된 발견 사항
- 필요 시 fix 작업 지시서
