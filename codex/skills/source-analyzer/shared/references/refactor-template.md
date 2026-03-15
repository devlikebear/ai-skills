# Refactoring Work Order Template

Use this exact structure when writing `.analysis/outputs/refactor-*.md` (or `.analysis/sessions/<id>/outputs/refactor-*.md` during active sessions).
Each section is mandatory. Write in the active skill language by default.

## Template

```markdown
# 리팩토링 지시서: <Scope>
# Refactoring Work Order: <Scope>

> **생성일 / Created At**: YYYY-MM-DD
> **세션 ID / Session ID**: `<session-id>`
> **체크포인트 / Checkpoint**: `checkpoint-XXX`
> **대상 / Target**: `<파일 경로 또는 모듈명 / file path or module name>`
> **분석 범위 / Analysis Scope**: 진입점 BFS / 파일 전체 / 특정 함수
> **우선순위 / Priority**: 높음 / 중간 / 낮음
> **소스 / Source**: `issue-candidates.md` 또는 직접 분석 / `issue-candidates.md` or direct analysis

---

## 요약 (Summary) / Summary

이 지시서는 `<대상>`에서 발견된 코드 품질/보안/구조 문제를 해결하기 위한 리팩토링 작업을 정의합니다.
총 <N>개의 이슈가 발견되었으며 (`DUP` <A>건 / `SEC` <B>건 / `TIDY` <C>건), 아래 작업 목록을 순서대로 실행하십시오.
This work order defines the refactoring tasks required to address code quality, security, and structural issues found in `<target>`.
There are <N> issues in total (`DUP` <A> / `SEC` <B> / `TIDY` <C>), and the work orders below should be executed in sequence.

---

## 발견된 이슈 목록 (Issues Found) / Issues Found

| # | 분류 코드 | 이슈 유형 | 위치 | 근거 | 위험도 | 영향 범위 |
|---|-----------|-----------|------|------|--------|-----------|
| 1 | `DUP-001` | 중복 로직 | `handler_a.go:32`, `handler_b.go:88` | 동일 검증 분기 반복 | 중간 | API 핸들러 |
| 2 | `SEC-001` | 입력 검증 누락 | `api/login.ts:54-91` | 사용자 입력 미검증 | 높음 | 인증 경로 |
| 3 | `TIDY-001` | 구조/동작 혼합 | `service/order.go:40-240` | I/O + 도메인 로직 혼재 | 중간 | 주문 처리 |

---

## 작업 지시서 (Work Orders) / Work Orders

각 작업은 독립적으로 실행 가능해야 합니다.
의존 관계가 있는 경우 "선행 작업" 필드를 채웁니다.
Each work order should be executable independently.
If there is a dependency, fill in the "Prerequisite" field.

---

### WO-001: <작업 제목>

**분류 코드 / Classification Code**: `DUP-001 | SEC-001 | TIDY-001`
**유형 / Type**: Extract Function / Rename / Move / Split File / Add Error Handling / Extract Constant / ...
**심각도 / Severity**: 높음 / 중간 / 낮음
**선행 작업 / Prerequisite**: 없음 (또는 WO-XXX 완료 후)
**근거 / Evidence**: `<정적 분석/코드 근거를 1-2문장으로 기술>`
**소스 이슈 / Source Issue**: `<issue-candidates.md의 이슈 코드, 있으면 기재 / issue code from issue-candidates.md if applicable>`
**영향 범위 / Impact Area**: `<모듈/기능>`

**문제 설명 / Problem**
현재 `<파일>:<줄 범위>` 에서 `<함수명>`이 다중 책임을 수행하거나, 중복 로직을 포함하거나, 보안상 취약한 처리를 포함합니다.
문제가 유지되면 유지보수성/안정성/보안성이 저하됩니다.
At `<file>:<line-range>`, `<function name>` has multiple responsibilities, duplicated logic, or insecure handling.
If left unchanged, maintainability, reliability, or security will degrade.

**현재 코드 위치 / Current Code Location**
- `internal/foo/handler.go` 라인 45-120

**SEC 상세 / SEC Details (`SEC-*`인 경우 필수 / required for `SEC-*`)**
- **취약 시나리오**: `<공격자가 어떤 입력/행동으로 문제를 유발하는지>`
- **악용 전제**: `<인증 상태, 접근 경로, 필요한 권한>`
- **완화 방향**: `<검증/권한체크/인코딩/격리 등>`

**TIDY 상세 / TIDY Details (`TIDY-*`인 경우 필수 / required for `TIDY-*`)**
- **적용 룰**: `<references/tidy-first-rules.md의 룰명>`
- **구조 변경 단계**: `<동작을 바꾸지 않는 정리 작업>`
- **동작 변경 단계**: `<필요한 동작 변경. 구조 변경 완료 후 수행>`

**지시 사항 / Instructions**
1. `parseRequest(r *http.Request) (*Payload, error)` 함수를 추출하여 `internal/foo/parser.go`로 이동하십시오.
2. `sendNotification(email string, payload *Payload) error` 함수를 추출하여 `internal/notify/email.go`로 이동하십시오.
3. 원래 함수는 추출된 함수를 호출하는 형태로만 남깁니다.
4. 분류 코드에 해당하는 문제(`DUP`/`SEC`/`TIDY`)를 직접 제거하는 변경만 포함하십시오.
5. 변경 후 테스트를 추가/보강하십시오.

**완료 기준 / Completion Criteria**
- [ ] 분류 코드로 정의한 문제 원인이 제거됨
- [ ] 수정한 코드 경로와 책임 분리가 문서와 일치함
- [ ] 회귀 없이 기존 동작이 유지되거나 승인된 방식으로 변경됨

**테스트 기준 / Test Criteria**
- [ ] 단위 테스트: 변경 함수/컴포넌트 커버
- [ ] 통합 테스트: 주요 호출 흐름 검증
- [ ] 회귀 테스트: 기존 실패 사례 재현 불가 확인

---

### WO-002: <작업 제목>

*(위 WO-001 형식 반복)*

---

## 켄트 백(Tidy First) 룰 매핑 테이블 / Kent Beck (Tidy First) Rule Mapping

| WO ID | 적용 룰 | 기대 효과 |
|-------|---------|-----------|
| WO-001 | 구조 변경과 동작 변경 분리 | 리뷰/롤백 위험 감소 |
| WO-003 | 작은 단계로 이동 | 배포 리스크 축소 |
| WO-004 | 국소 정리 우선 | 이해도 향상 |

---

## 리팩토링 순서 (Recommended Order) / Recommended Order

의존 관계 없는 작업은 병렬 실행 가능합니다.
Work orders without dependencies can be executed in parallel.

```
WO-001 (파일 분리)
  └- WO-003 (인터페이스 추출, WO-001 완료 후)
WO-002 (중복 제거) <- 독립 실행 가능
WO-004 (상수 추출) <- 독립 실행 가능
```

---

## 체크포인트 진행 로그 (Checkpoint Progress Log) / Checkpoint Progress Log

중단/재개 가능하도록 아래 표를 반드시 유지합니다.
Keep this table updated so the work can be paused and resumed safely.

| Checkpoint | 상태 | 변경된 WO | DUP/SEC/TIDY 진행 현황 | 메모 |
|------------|------|-----------|-------------------------|------|
| checkpoint-001 | in_progress | WO-001, WO-002 초안 | DUP 1/3, SEC 0/2, TIDY 1/2 | 엔트리/서비스 계층 분석 완료 |
| checkpoint-002 | paused | WO-001 상세 보강 | DUP 2/3, SEC 1/2, TIDY 1/2 | 저장소 계층 검토 필요 |

---

## 다음 세션 재개 지점 (Resume Point) / Resume Point

- **다음 시작 WO**: `WO-XXX`
- **남은 선행 작업**: `<예: WO-001 완료 후 WO-003 진행>`
- **우선 재검토 파일**: `<path1>, <path2>`
- **재개 순서 / Resume Steps**
  1. 마지막 체크포인트 로그 행 확인
  2. 미완료 WO의 "완료 기준"부터 충족 여부 점검
  3. 신규 변경사항을 반영해 체크포인트 번호를 증가시켜 업데이트

---

## 완료 검증 체크리스트 / Completion Verification Checklist

- [ ] `make test` 전체 통과
- [ ] `make lint` 경고 없음 (새로 추가된 파일 포함)
- [ ] 변경된 파일의 최대 줄 수가 300줄 이하
- [ ] 이슈 목록의 모든 항목이 `DUP-*`, `SEC-*`, `TIDY-*` 중 하나로 분류됨
- [ ] 이슈 목록의 모든 항목이 WO로 처리됨
- [ ] `SEC-*` 항목마다 취약 시나리오/악용 전제/완화 방향이 기재됨
- [ ] `TIDY-*` 항목마다 적용 룰과 단계 분리가 기재됨
```
