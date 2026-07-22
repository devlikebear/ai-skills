# System Overhaul Proposal Template

Use this exact structure when writing `.analysis/outputs/overhaul-*.md` (or `.analysis/sessions/<id>/outputs/overhaul-*.md` during active sessions).
Each section is mandatory. Write in the active skill language by default.

## Template

```markdown
# 시스템 오버홀 제안서: <Scope>
# System Overhaul Proposal: <Scope>

> **생성일 / Created At**: YYYY-MM-DD
> **세션 ID / Session ID**: `<session-id>`
> **체크포인트 / Checkpoint**: `checkpoint-XXX`
> **대상 / Target**: `<분석 범위 / analysis scope>`
> **기준 커밋 / Base Commit**: `<commit hash>`
> **소스 / Source**: analyze 산출물 기반 / Based on analyze outputs

---

## 현행 시스템 진단 (Current System Diagnosis) / Current System Diagnosis

### 아키텍처 개요 / Architecture Overview

> analyze 산출물의 `architecture.md`와 `module-map.json`을 기반으로 현행 아키텍처를 요약합니다.
> Summarize the current architecture based on `architecture.md` and `module-map.json` from analyze outputs.

- **계층 구조 / Layer structure**: <현행 계층 요약>
- **모듈 수 / Module count**: <N>개
- **핵심 데이터 흐름 / Key data flows**: <주요 흐름 1-3개>

### 근본 문제 (Root Problems) / Root Problems

아키텍처 수준의 근본 문제를 식별합니다. 증상이 아닌 원인에 집중합니다.
Identify root problems at the architecture level. Focus on causes, not symptoms.

| # | 문제 코드 | 문제 유형 | 요약 | 영향 범위 | 심각도 |
|---|-----------|-----------|------|-----------|--------|
| 1 | `ARCH-001` | 잘못된 계층 분리 | <요약> | <모듈/기능> | 높음/중간/낮음 |
| 2 | `DEAD-001` | 불필요한 기능 | <요약> | <모듈/기능> | 높음/중간/낮음 |
| 3 | `OVER-001` | 과도한 추상화 | <요약> | <모듈/기능> | 높음/중간/낮음 |
| 4 | `DEBT-001` | 누적 기술 부채 | <요약> | <모듈/기능> | 높음/중간/낮음 |

### 문제 분류 코드 / Problem Classification Codes

- `ARCH-*`: 아키텍처 설계 결함 — 계층 분리 오류, 순환 의존성, 책임 혼재, 잘못된 추상화 경계
- `DEAD-*`: 불필요한 기능/코드 — 사용되지 않는 모듈, 더 이상 의미 없는 기능, 레거시 호환층
- `OVER-*`: 과잉 설계 — 불필요한 추상화, 과도한 설정 가능성, 미래 요구사항을 위한 과잉 구현
- `DEBT-*`: 누적 기술 부채 — 오래된 패턴, deprecated API 사용, 일관성 없는 관례

---

## 오버홀 목표 (Overhaul Goals) / Overhaul Goals

이번 오버홀이 달성하려는 목표를 명확히 합니다.
Clearly state the goals this overhaul aims to achieve.

1. **<목표 1>**: <설명>
2. **<목표 2>**: <설명>
3. **<목표 3>**: <설명>

### 의도적으로 깨는 것들 (Intentional Breaking Changes) / Intentional Breaking Changes

하위 호환성을 깨더라도 올바른 설계를 우선합니다. 깨지는 항목을 명시합니다.
Correct design takes priority over backward compatibility. List what breaks.

| # | 깨지는 항목 | 이유 | 대안/마이그레이션 경로 |
|---|-------------|------|------------------------|
| 1 | <API/인터페이스/포맷> | <왜 깨야 하는지> | <마이그레이션 방법 또는 "없음 — 새로 구현"> |

---

## 목표 아키텍처 (Target Architecture) / Target Architecture

### 설계 원칙 / Design Principles

오버홀된 시스템이 따를 핵심 설계 원칙을 정의합니다.
Define the core design principles the overhauled system will follow.

1. **<원칙 1>**: <설명>
2. **<원칙 2>**: <설명>
3. **<원칙 3>**: <설명>

### 새 아키텍처 개요 / New Architecture Overview

```
<텍스트 기반 아키텍처 다이어그램>
<Text-based architecture diagram>
```

### 모듈 재설계 / Module Redesign

각 모듈에 대해 현행 → 목표 상태를 정의합니다.
Define current → target state for each module.

#### <모듈명 / Module Name>

- **현행 상태 / Current**: <현재 역할과 문제점>
- **목표 상태 / Target**: <새로운 역할과 설계>
- **변경 유형 / Change Type**: 재설계 / 제거 / 통합 / 분리 / 유지
- **관련 문제 / Related Problems**: `ARCH-001`, `DEAD-002`
- **Breaking**: Yes / No

*(모듈 수만큼 반복 / Repeat for each module)*

### 제거 대상 / To Be Removed

불필요하다고 판단되어 완전히 제거할 항목을 나열합니다.
List items to be completely removed as unnecessary.

| # | 대상 | 유형 | 제거 근거 | 현재 의존 관계 |
|---|------|------|-----------|----------------|
| 1 | `<경로/모듈/기능>` | 모듈/파일/함수/설정 | <왜 불필요한지> | <이것에 의존하는 것들> |

---

## 오버홀 작업 지시서 (Overhaul Work Orders) / Overhaul Work Orders

각 작업은 독립적으로 실행 가능하거나, 선행 작업이 명시되어야 합니다.
Each work order should be independently executable, or have prerequisites stated.

### OH-001: <작업 제목>

**문제 코드 / Problem Code**: `ARCH-001`
**변경 유형 / Change Type**: 재설계 / 제거 / 통합 / 분리
**Breaking**: Yes / No
**심각도 / Severity**: 높음 / 중간 / 낮음
**선행 작업 / Prerequisite**: 없음 (또는 OH-XXX 완료 후)
**근거 / Evidence**: `<analyze 산출물에서의 근거>`

**현재 상태 / Current State**
- 현재 코드 위치와 구조를 설명합니다.
- `<file>:<line-range>` 형식으로 참조합니다.

**목표 상태 / Target State**
- 오버홀 후 코드가 어떤 구조와 역할을 갖는지 설명합니다.
- 새 파일 경로, 인터페이스, 데이터 흐름을 구체적으로 기술합니다.

**마이그레이션 경로 / Migration Path**
- 기존 사용자/코드가 새 구조로 전환하는 방법을 기술합니다.
- Breaking change인 경우 전환 가이드를 포함합니다.
- "없음 — 깨끗하게 새로 구현"도 유효한 선택입니다.

**지시 사항 / Instructions**
1. <단계별 지시>
2. <단계별 지시>
3. <단계별 지시>

**완료 기준 / Completion Criteria**
- [ ] 목표 상태의 구조가 구현됨
- [ ] 관련 문제 코드로 정의한 근본 원인이 해소됨
- [ ] 테스트가 새 구조를 검증함

**테스트 기준 / Test Criteria**
- [ ] 단위 테스트: 새 구조의 핵심 동작 검증
- [ ] 통합 테스트: 새 데이터 흐름 검증
- [ ] 마이그레이션 테스트: 전환 경로 검증 (해당 시)

---

### OH-002: <작업 제목>

*(위 OH-001 형식 반복 / Repeat OH-001 format)*

---

## 실행 순서 (Execution Order) / Execution Order

의존 관계를 고려한 실행 순서입니다.
Execution order considering dependencies.

```
Phase 1: 제거 (Removal)
  OH-003 (불필요한 모듈 제거)
  OH-005 (레거시 호환층 제거)

Phase 2: 기반 재설계 (Foundation Redesign)
  OH-001 (핵심 아키텍처 재설계)
    └─ OH-002 (모듈 분리, OH-001 완료 후)

Phase 3: 통합 및 마무리 (Integration & Finalization)
  OH-004 (새 인터페이스 통합)
  OH-006 (마이그레이션 가이드 작성)
```

### 실행 원칙 / Execution Principles

1. **제거 우선**: 불필요한 것을 먼저 걷어내어 작업 범위를 줄입니다.
2. **기반부터**: 핵심 아키텍처를 먼저 잡고 세부 모듈을 맞춥니다.
3. **단계 검증**: 각 Phase 완료 후 전체 테스트를 실행합니다.

---

## 리스크 평가 (Risk Assessment) / Risk Assessment

| 리스크 | 발생 가능성 | 영향도 | 대응 방안 |
|--------|-------------|--------|-----------|
| <리스크 1> | 높음/중간/낮음 | 높음/중간/낮음 | <대응 방안> |
| <리스크 2> | 높음/중간/낮음 | 높음/중간/낮음 | <대응 방안> |

---

## 체크포인트 진행 로그 (Checkpoint Progress Log) / Checkpoint Progress Log

| Checkpoint | 상태 | 변경된 OH | 진행 현황 | 메모 |
|------------|------|-----------|-----------|------|
| checkpoint-001 | in_progress | OH-001~003 초안 | ARCH 2/3, DEAD 1/2 | 핵심 모듈 분석 완료 |

---

## 다음 세션 재개 지점 (Resume Point) / Resume Point

- **다음 시작 OH**: `OH-XXX`
- **남은 선행 작업**: `<예: OH-001 완료 후 OH-002 진행>`
- **우선 재검토 대상**: `<path1>, <path2>`
- **재개 순서 / Resume Steps**
  1. 마지막 체크포인트 로그 행 확인
  2. analyze 산출물 변경 여부 확인 (sync 실행)
  3. 미완료 OH의 근거를 재검증 후 계속

---

## 완료 검증 체크리스트 / Completion Verification Checklist

- [ ] 모든 `ARCH-*` 문제에 대해 목표 아키텍처에서 해소 방안이 제시됨
- [ ] 모든 `DEAD-*` 항목에 대해 제거 근거와 의존 관계가 확인됨
- [ ] 모든 `OVER-*` 항목에 대해 단순화 방향이 제시됨
- [ ] 모든 `DEBT-*` 항목에 대해 현대화 방안이 제시됨
- [ ] 모든 Breaking Change에 마이그레이션 경로가 기재됨
- [ ] 실행 순서가 의존 관계를 준수함
- [ ] 리스크 평가가 완료됨
- [ ] 각 OH에 완료 기준과 테스트 기준이 포함됨
```
