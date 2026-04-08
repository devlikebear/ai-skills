# 모듈: github-flow

전체 GitHub Flow 라이프사이클을 관리하는 스킬.

## 역할

branch → develop → PR → merge → release의 전체 GitHub Flow를 5개 단계로 안내합니다. Phase 2에서 plan → implement → review → commit 내부 루프를 반복합니다.

## 핵심 파일

| 파일 | 역할 |
|------|------|
| `claude-code/plugin/skills/github-flow/SKILL.md` | Claude Code 스킬 |
| `codex/skills/github-flow/SKILL.md` | Codex 스킬 |
| `references/github-flow-checklist.md` | 단계별 체크리스트 |

## 5개 Phase

1. **Branch**: base에서 feature 브랜치 생성
2. **Develop**: plan → implement → review → commit (내부 루프)
3. **Push & PR**: `gh pr create`로 PR 생성
4. **Merge**: CI/리뷰 통과 후 머지
5. **Tag & Release** (선택): SemVer 태그 + GitHub 릴리스

## 규칙

- main/master에 force-push 금지
- `--no-verify` 금지 (명시적 승인 없이)
- 파괴적 작업 전 항상 확인
- PR 당 하나의 논리적 변경
