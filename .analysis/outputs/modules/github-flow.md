# 모듈: github-flow

## 역할

브랜치 생성부터 PR, 머지, 릴리스까지 GitHub Flow 전체를 한 스킬로 묶은 운영 스킬이다.

## 핵심 경로

- Codex: `codex/skills/github-flow/SKILL.md`
- Codex 체크리스트: `codex/skills/github-flow/shared/references/github-flow-checklist.md`
- Codex 메타데이터: `codex/skills/github-flow/agents/openai.yaml`
- Claude Code 플러그인: `claude-code/plugin/skills/github-flow/SKILL.md`

## 단계 구성

1. Branch
2. Develop
3. Push & Pull Request
4. Merge
5. Tag & Release

가운데 Develop 단계는 다시 `plan -> implement -> review -> commit`의 내부 루프로 쪼개진다.

## 저장소에서 중요한 이유

이 저장소는 공개 배포용 스킬 모음이기 때문에 개별 기능보다 배포 절차와 릴리스 일관성이 중요하다. `github-flow`는 그 운영 절차를 스킬 자체로 명시해 둔 사례다.

## 입문자가 먼저 볼 파일

1. `codex/skills/github-flow/SKILL.md`
2. `codex/skills/github-flow/shared/references/github-flow-checklist.md`
3. `CHANGELOG.md`

## 관찰 포인트

`README.md`에는 포함되어 있지만 `scripts/publish_wiki.sh`의 홈/사이드바 템플릿은 아직 `github-flow` 모듈 링크를 만들지 않는다. 저장소 문서를 확장할 때 같이 확인할 항목이다.
