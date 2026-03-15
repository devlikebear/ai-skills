# 모듈: 참조 템플릿

## 역할

계획, 구현, 리뷰, 리팩터링, 분석 작업에서 반복되는 체크리스트와 문서 틀을 재사용 가능한 Markdown 템플릿으로 제공한다.

## 핵심 경로

- Codex 공유 템플릿: `codex/skills/*/shared/references/*`
- Claude Code 공유 템플릿: `claude-code/plugin/references/*`

## 구조적 특징

1. Codex 쪽은 스킬별 `shared/references/`에 필요한 템플릿만 둔다.
2. Claude Code 쪽은 `references/` 한 디렉터리에 공용 템플릿을 모은다.
3. `source-analyzer`는 튜토리얼 템플릿, 리팩터링 템플릿, TIDY/보안 체크리스트, 체크포인트 템플릿을 함께 가진다.
4. `github-flow`, `review`, `refactor`, `implement`, `plan-for-codex`도 각자 필요한 워크오더/체크리스트를 공유 문서로 둔다.

## 대표 문서

- `tutorial-template.md`
- `refactor-template.md`
- `checkpoint-template.md`
- `review-checklist.md`
- `refactoring-patterns.md`
- `github-flow-checklist.md`

## 입문자가 먼저 볼 파일

1. `codex/skills/source-analyzer/shared/references/tutorial-template.md`
2. `claude-code/plugin/references/refactor-template.md`
3. `codex/skills/github-flow/shared/references/github-flow-checklist.md`
