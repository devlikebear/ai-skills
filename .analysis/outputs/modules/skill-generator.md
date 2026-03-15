# 모듈: skill-generator

## 역할

이 저장소 안에서 새 Codex 스킬을 만들 때 upstream `skill-creator` 흐름을 재사용하면서, 이 저장소 전용 구조 규칙을 덧붙이는 로컬 래퍼다.

## 핵심 경로

- 래퍼 스킬: `.codex/skills/skill-generator/SKILL.md`
- 래퍼 메타데이터: `.codex/skills/skill-generator/agents/openai.yaml`

## 강제하는 규칙

1. 스킬 루트에는 단일 `SKILL.md`만 둔다.
2. `agents/openai.yaml`을 둔다.
3. 재사용 가능한 자료는 `shared/` 밑으로 분리한다.
4. `ko/`, `en/` 디렉터리는 만들지 않는다.

## 왜 `.codex/` 아래에 있나

이 스킬은 공개 배포 대상이 아니라 현재 저장소를 관리하는 작성자 전용 도구다. 그래서 `codex/skills/`가 아니라 `.codex/skills/`에 들어 있다.

## 입문자가 먼저 볼 파일

1. `.codex/skills/skill-generator/SKILL.md`
2. `.codex/skills/skill-generator/agents/openai.yaml`
3. `tests/test_skill_repository_contract.py`
