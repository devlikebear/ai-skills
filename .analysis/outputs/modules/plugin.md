# 모듈: Claude Code 플러그인

## 역할

`code-workflow`라는 이름으로 여러 스킬을 하나의 Claude Code 플러그인과 마켓플레이스 엔트리로 묶어 배포한다.

## 핵심 경로

- 마켓플레이스 등록: `.claude-plugin/marketplace.json`
- 플러그인 매니페스트: `claude-code/plugin/.claude-plugin/plugin.json`
- 플러그인 스킬: `claude-code/plugin/skills/*`
- 공용 참조: `claude-code/plugin/references/*`
- 플러그인 스크립트: `claude-code/plugin/scripts/checkpoint_manager.py`

## 포함 스킬

- `plan`
- `implement`
- `review`
- `refactor`
- `source-analyzer`
- `github-flow`

## 구조적 특징

1. 각 스킬은 단일 `SKILL.md`만 가진다.
2. 공용 문서는 `references/` 한 곳에만 둔다.
3. `source-analyzer`는 `${CLAUDE_PLUGIN_ROOT}`를 기준으로 체크포인트 스크립트를 찾는다.
4. Codex 전용 `agents/openai.yaml`은 포함하지 않는다.
5. 현재 버전은 매니페스트와 마켓플레이스 양쪽에서 `0.6.1`로 맞춰져 있다.

## 실제 참조 파일

`claude-code/plugin/references/`에는 현재 11개 문서가 있다.

- `work-order.md`
- `refactor-work-order.md`
- `review-checklist.md`
- `refactoring-checklist.md`
- `refactoring-patterns.md`
- `checkpoint-template.md`
- `refactor-template.md`
- `tidy-first-rules.md`
- `security-triage-checklist.md`
- `tutorial-template.md`
- `github-flow-checklist.md`

## 입문자가 먼저 볼 파일

1. `claude-code/plugin/.claude-plugin/plugin.json`
2. `claude-code/plugin/skills/source-analyzer/SKILL.md`
3. `claude-code/plugin/skills/github-flow/SKILL.md`
4. `.claude-plugin/marketplace.json`
