---
name: github-flow
description: "Run the full GitHub Flow lifecycle: branch → develop → PR → merge → release. Use this Korean-default variant when starting a new feature, bugfix, or refactor that follows GitHub Flow conventions."
---

# GitHub Flow

이 변형은 한국어 기본 출력의 `github-flow` 스킬입니다.

## Load only what you need

- `shared/references/github-flow-checklist.md`: 단계별 체크리스트.

## Language policy

- Write responses in Korean by default.
- If the user explicitly requests another language policy, follow it.

## 개요

```
main → [feature branch] → commits → PR → merge → main → [tag/release]
```

어느 단계에서든 이 스킬을 호출할 수 있습니다. 단계를 지정하지 않으면 Phase 1부터 시작합니다.

---

## Phase 1 — Branch (브랜치 생성)

1. `main`(또는 합의된 베이스 브랜치)에 있고 최신 상태인지 확인:
   ```bash
   git checkout main && git pull
   ```
2. 의미 있는 이름의 브랜치를 생성합니다:
   - 형식: `feat/`, `fix/`, `chore/`, `refactor/` + 소문자 케밥-케이스
   ```bash
   git checkout -b feat/<짧은-설명>
   ```
3. 보고: 브랜치 이름, 베이스 브랜치, 작업 트리 상태.

---

## Phase 2 — Develop (개발)

각 작업 단위마다 아래 이너 루프를 순서대로 실행합니다:

### 2-1. Plan — `/plan-for-codex`
- 요청을 ≤3개의 경계가 명확한 작업 지시서(30–90분 단위)로 분할합니다.
- 각 작업 지시서에는 측정 가능한 완료 기준과 검증 커맨드를 포함해야 합니다.
- API 변경이나 광범위한 리팩터는 명시적 허가 없이는 차단으로 표시합니다.

### 2-2. Implement — `/implement`
- 작업 지시서를 하나씩 실행합니다.
- 범위를 지시서 안에 유지하고, 확장되면 중단 후 재계획합니다.
- 좁은 범위의 검증 실패는 최대 2회까지 재시도합니다.

### 2-3. Review — `/review`
- 커밋 전에 변경 사항을 diff 리뷰합니다.
- 차단 지적 사항을 모두 수정합니다. 리뷰를 통과하기 전에는 커밋하지 않습니다.

### 2-4. Commit (커밋)
리뷰가 통과된 후:

1. 관련 파일만 스테이징합니다 — `git add -A`나 `git add .`를 무분별하게 사용하지 마세요:
   ```bash
   git add <특정-파일들>
   ```
2. Conventional Commits 형식으로 커밋합니다 (`feat:`, `fix:`, `chore:`, `refactor:`, `docs:`):
   - 제목: 명령형, ≤72자.
   - 본문(선택): *왜*를 설명하고, *무엇*은 생략합니다.
   ```bash
   git commit -m "feat: 짧은 설명"
   ```
3. pre-commit 훅 실패 시 최대 1회 재시도 — 근본 원인을 수정하고, `--no-verify`는 사용하지 않습니다.

2-1 → 2-4를 각 작업 지시서마다 반복합니다.

---

## Phase 3 — Push & Pull Request (PR 생성)

1. 브랜치를 푸시합니다:
   ```bash
   git push -u origin <브랜치-이름>
   ```
2. PR을 생성합니다:
   - 제목: ≤70자, 명령형.
   - 본문: Summary(글머리 목록) + Test plan(체크리스트).
   ```bash
   gh pr create --title "..." --body "$(cat <<'EOF'
   ## Summary
   - ...

   ## Test plan
   - [ ] ...
   EOF
   )"
   ```
3. PR URL을 보고합니다.

---

## Phase 4 — Merge (머지)

CI가 통과하고 리뷰가 완료된 후에만 머지합니다.

1. 머지 전략을 선택합니다: `--merge` / `--squash` / `--rebase`
2. 머지하고 원격 브랜치를 삭제합니다:
   ```bash
   gh pr merge <번호> --<전략> --delete-branch
   ```
3. 로컬 main을 동기화합니다:
   ```bash
   git checkout main && git pull
   ```
4. 보고: 머지된 PR, 삭제된 브랜치, main의 현재 HEAD.

---

## Phase 5 — Tag & Release (태그 & 릴리즈, 선택)

버전을 배포할 때만 이 단계를 실행합니다.

1. SemVer 기준으로 새 버전을 결정합니다 (`patch` / `minor` / `major`).
2. 버전 파일(`VERSION.txt`, `package.json` 등)과 `CHANGELOG.md`가 main에 커밋되어 있는지 확인합니다.
3. GitHub 릴리즈를 생성합니다:
   ```bash
   gh release create v<버전> --title "v<버전>" --notes "<릴리즈 노트>"
   ```
4. 릴리즈 URL을 보고합니다.

---

## 규칙

- `main`이나 `master`에 절대 force-push하지 않습니다.
- 명시적 허가 없이 `--no-verify`를 사용하지 않습니다.
- 파괴적인 액션(reset --hard, force-push, 브랜치 삭제) 전에 반드시 확인합니다.
- 특정 파일만 스테이징합니다 — 시크릿이나 바이너리가 포함되지 않도록 주의합니다.
- 논리적 변경 단위당 하나의 PR을 유지합니다.
- 작업이 원래 범위를 벗어나면 중단하고 `/plan-for-codex`로 재계획합니다.

## 각 단계의 출력

- 이 단계에서 수행한 작업
- 현재 상태: 브랜치 이름, PR URL, 또는 릴리즈 URL
- 다음 권장 단계 또는 커맨드
