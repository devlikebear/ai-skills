# 모듈: review

## 역할

변경된 코드에 대해 회귀, 보안, 테스트 누락을 먼저 찾는 검토 스킬이다.

## 핵심 경로

- Codex: `codex/skills/review/SKILL.md`
- Codex 참조: `codex/skills/review/shared/references/review-checklist.md`
- Codex 보조 템플릿: `codex/skills/review/shared/references/work-order.md`
- Claude Code 플러그인: `claude-code/plugin/skills/review/SKILL.md`

## 출력 특징

- 결과는 항상 findings-first 순서다.
- 이슈가 있으면 파일과 라인 기준으로 지적한다.
- 수정이 필요하면 work order를 다시 만든다.

## 왜 중요한가

이 저장소는 스킬 배포 저장소라서 런타임 버그보다 구조 회귀가 더 자주 문제 된다. `review` 스킬은 이런 저장소에서 문서 변경과 구조 변경이 실제 계약을 깨는지 점검하는 데 잘 맞는다.

## 입문자가 먼저 볼 파일

1. `codex/skills/review/SKILL.md`
2. `codex/skills/review/shared/references/review-checklist.md`
3. `tests/test_skill_repository_contract.py`
