# Phase 1: 안전 호출과 평가 기반 — 작업지시서

_작성일: 2026-07-22_
_속한 로드맵: [`skill-platform-modernization-roadmap.md`](./skill-platform-modernization-roadmap.md)_
_예상 소요: 4~8시간_
_상태: 구현 및 자동 검증 완료, 사용자 승인 대기_

## 페이즈 목표

GitHub push, PR, merge, release로 이어질 수 있는 `github-flow`를 두 플랫폼 모두 명시 호출 전용으로 만든다. 또한 dirty working tree를 먼저 확인하도록 preflight를 고치고, 이후 스킬 변경에서 라우팅 경계를 검증할 평가 fixture와 계약 테스트를 마련한다.

## 전제 조건

- [x] 현재 테스트 74개 통과
- [x] 기존 미추적 `AGENTS.md` 보존
- [x] 작업 브랜치 `codex/skill-platform-modernization` 생성

## 이 페이즈에서 하지 않는 것

- Codex 플러그인 bundle 추가 → Phase 2
- `source-analyzer` 모드 분리 → Phase 3
- MCP 실행 방식 변경 → Phase 4

## 작업 체크리스트

### 작업 그룹 A: 호출 정책 계약

- [x] **T1.A.1** — 실패하는 정책 테스트 작성
  - 파일: `tests/test_skill_repository_contract.py`
  - Codex `github-flow`에 `allow_implicit_invocation: false`가 없으면 실패
  - Claude `github-flow`에 `disable-model-invocation: true`가 없으면 실패
  - 검증: `python3 -m unittest tests.test_skill_repository_contract -v`

- [x] **T1.A.2** — 두 배포본에 명시 호출 정책 적용
  - 파일: `codex/skills/github-flow/agents/openai.yaml`
  - 파일: `claude-code/plugin/skills/github-flow/SKILL.md`

### 작업 그룹 B: Git 안전 preflight

- [x] **T1.B.1** — `git status`가 checkout/pull보다 먼저라는 계약 테스트 작성
  - 파일: `tests/test_skill_repository_contract.py`

- [x] **T1.B.2** — Codex와 Claude 스킬의 Phase 1 순서를 `status → 판단 → update`로 변경
  - 파일: `codex/skills/github-flow/SKILL.md`
  - 파일: `claude-code/plugin/skills/github-flow/SKILL.md`
  - dirty tree에서 pull/checkout하지 않고 사용자 변경을 보존

### 작업 그룹 C: 행동 평가 seed

- [x] **T1.C.1** — 스킬별 positive/negative/confusion prompt fixture 추가
  - 파일: `evals/skill-routing.json`
  - 최소 각 스킬 2개 positive와 인접 스킬 confusion 사례 포함

- [x] **T1.C.2** — fixture 구조·대상 스킬·중복 ID 계약 테스트 추가
  - 파일: `tests/test_skill_routing_evals.py`

- [x] **T1.C.3** — `0.12.0` MINOR 버전과 CHANGELOG 갱신
  - 모든 release manifest를 같은 버전으로 유지

## ✅ Phase 1 Checkpoint

**구현 확인:**
- [x] `github-flow`가 양쪽 플랫폼에서 명시 호출 전용
- [x] dirty tree 확인이 checkout/pull보다 선행
- [x] 6개 스킬의 라우팅 fixture 존재

**자동 검증:**
- [x] `python3 -m unittest tests.test_skill_repository_contract tests.test_skill_routing_evals -v`
- [x] `python3 -m unittest discover tests -v` — 79 tests passed

**수동 확인:**
- [x] `github-flow` 문서에 PR·merge·release가 별도 명시 의도를 요구한다고 명시됨

**완료 처리:** 모든 항목 통과 후 결과를 보고하고 Phase 2 진행 승인을 받는다.
