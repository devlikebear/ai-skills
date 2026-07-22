# Source Analyzer Tutorial Template

Use this template for:
- `.analysis/sessions/<session-id>/outputs/tutorial.md`
- `.analysis/sessions/<session-id>/outputs/clone-coding.md`

Write for beginners. Keep paragraphs short. Use real repo file paths.
Write in the active skill language by default.
Localize section titles and examples to match the active skill language.

## Template

```markdown
# 튜토리얼: <프로젝트/스코프 이름>
# Tutorial: <Project/Scope Name>

> 대상 독자 / Audience: 코드베이스에 처음 들어오는 개발자 / Developers new to the codebase
> 목표 시간 / Estimated Time: <예: 90분 / e.g. 90 minutes>
> 기준 세션 / Reference Session: `<session-id>` / `checkpoint-XXX`

---

## 학습 목표 / Learning Objectives

- 이 튜토리얼을 완료하면 `<핵심 목표>`를 설명하고 구현할 수 있다.
- 핵심 모듈 `<module-a>`, `<module-b>`의 책임을 구분할 수 있다.
- 최소 기능을 직접 클론코딩하고 실행 검증할 수 있다.
- After this tutorial, the reader can explain and implement `<core goal>`.
- The reader can distinguish responsibilities of `<module-a>` and `<module-b>`.
- The reader can clone the minimum viable flow and verify it runs.

---

## 사전지식/실행환경 / Prerequisites and Runtime

- 필수 사전지식: `<언어/프레임워크 기본>`
- 런타임: `<예: Node.js 22, Python 3.12>`
- 필수 명령: `<설치/실행/테스트 커맨드>`
- 시작 파일: `<entrypoint path>`
- Required background: `<language/framework basics>`
- Runtime: `<e.g. Node.js 22, Python 3.12>`
- Required commands: `<install/run/test commands>`
- Entry file: `<entrypoint path>`

---

## 아키텍처 한눈에 보기 / Architecture at a Glance

### 레이어 요약 / Layer Summary

| 레이어 | 경로 | 책임 |
|--------|------|------|
| API | `src/api/*` | 요청 수신/응답 |
| Service | `src/service/*` | 유스케이스 |
| Repository | `src/repo/*` | 데이터 접근 |

### 데이터/호출 흐름 / Data and Call Flow

```text
Client -> API Handler -> Service -> Repository -> DB
                   <- Response Mapping <-
```

---

## 단계별 클론코딩 / Step-by-Step Clone Coding

### Step 1. 프로젝트 골격 준비 / Prepare the Project Skeleton

- 작업 순서
  1. `<파일/디렉터리>` 생성
  2. `<기본 인터페이스/타입>` 정의
- 확인 포인트
  - [ ] `npm test` 또는 `make test` 기본 통과
  - [ ] 엔트리포인트에서 모듈 로딩 성공
- 참고 파일
  - `src/main.ts`
  - `src/config.ts`

### Step 2. 핵심 유스케이스 구현 / Implement the Core Use Case

- 작업 순서
  1. `<Service 함수>` 구현
  2. `<Repository 호출>` 연결
- 확인 포인트
  - [ ] 정상 입력/예외 입력 테스트 통과
  - [ ] 반환 타입/에러 경로 일치
- 참고 파일
  - `src/service/<name>.ts`
  - `src/repo/<name>.ts`

### Step 3. API/입출력 연결 / Connect API and I/O

- 작업 순서
  1. `<Handler>` 구현
  2. `<Validator/Middleware>` 연결
- 확인 포인트
  - [ ] 로컬 실행 후 주요 엔드포인트 응답 확인
  - [ ] 실패 케이스에서 기대한 에러 코드 반환
- 참고 파일
  - `src/api/<name>.ts`

---

## 자가검증 체크리스트 / Self-Verification Checklist

- [ ] 주요 모듈 책임을 1-2문장으로 설명할 수 있다.
- [ ] 호출 흐름을 파일 경로 기준으로 추적할 수 있다.
- [ ] 최소 기능 클론코딩 결과가 테스트로 검증된다.
- [ ] 변경 없이 원본 동작을 재현한다.
- [ ] I can explain each major module in 1-2 sentences.
- [ ] I can trace the call flow using concrete file paths.
- [ ] The clone-coded minimum flow is verified by tests.
- [ ] The original behavior is reproduced without unintended changes.

---

## 확장 미션 / Extension Missions

1. `<기능 확장 A>`를 기존 레이어 분리 원칙대로 추가한다.
2. `<기능 확장 B>`에 대한 테스트를 먼저 작성하고 구현한다.
3. 중복 로직 1개를 찾아 공통 모듈로 추출한다.
1. Add `<feature extension A>` while preserving the existing layer boundaries.
2. Write tests first for `<feature extension B>`, then implement it.
3. Find one duplicated logic path and extract it into a shared module.
```
