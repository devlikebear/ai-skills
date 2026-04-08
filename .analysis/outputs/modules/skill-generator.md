# 모듈: skill-generator

저장소 전용 Codex 스킬 생성 래퍼.

## 역할

`.codex/skills/skill-generator/`에 위치하며, 업스트림 `skill-creator` 워크플로를 래핑하여 이 저장소의 flat 레이아웃 규칙을 강제합니다.

## 핵심 파일

| 파일 | 역할 |
|------|------|
| `.codex/skills/skill-generator/SKILL.md` | 래퍼 스킬 정의 |
| `.codex/skills/skill-generator/agents/openai.yaml` | Codex 에이전트 설정 |

## 강제하는 규칙

1. 단일 `SKILL.md` + 자동 언어 감지 정책
2. `ko/`, `en/` 언어 하위 디렉토리 금지
3. 재사용 가능한 내용은 `shared/`에 배치
4. YAML frontmatter description은 따옴표로 감싸기

## 작성 흐름

1. 스킬 이름과 트리거 예시 확인
2. `skill-creator` 워크플로를 따라 내용 결정
3. 단일 SKILL.md 작성
4. agents/openai.yaml 추가
5. frontmatter 검증
