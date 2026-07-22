# AI Skills 플랫폼 현대화 로드맵

_작성일: 2026-07-22_
_예상 전체 소요: 24~40시간_
_페이즈 수: 4개_

## Overview

현재 저장소는 Codex용 독립 스킬과 Claude Code 플러그인을 함께 제공하고, 구조·릴리스·복제본 동기화를 85개 테스트로 검증한다. 이번 개선은 최신 플랫폼 흐름에 맞춰 배포 단위를 플러그인으로 통합하고, 외부 변경을 수행하는 스킬의 자동 발동을 차단하며, 실제 스킬 라우팅과 결과 품질을 반복 평가할 수 있게 만들었다.

구현은 기존 배포 사용자를 한 번에 깨뜨리지 않는다. 안전 정책과 평가 기반을 먼저 만들고, Codex 플러그인 배포를 추가한 뒤, `source-analyzer`의 책임과 컨텍스트 비용을 줄이고 마지막으로 크로스플랫폼 설치·릴리스 계약을 정리한다.

## 완료 조건

- [x] 외부 변경 스킬이 Codex와 Claude Code에서 명시 호출로만 실행된다.
- [x] positive/negative/confusion 프롬프트로 스킬 라우팅을 평가할 수 있다.
- [x] 8개 워크플로 스킬과 MCP를 하나의 Codex 플러그인으로 설치할 수 있다.
- [x] `source-analyzer` 기본 실행은 `.analysis/` 밖을 수정하거나 외부 Wiki를 게시하지 않는다.
- [x] macOS, Linux, Windows에 대한 설치·경로 계약이 문서와 테스트에 반영된다.
- [x] 모든 버전 파일과 배포 manifest가 동일한 SemVer를 사용한다.

## 기술 스택 / 환경

- **스킬 형식**: Agent Skills `SKILL.md`, Codex `agents/openai.yaml`, Claude Code 확장 frontmatter
- **플러그인**: `.codex-plugin/plugin.json`, `.claude-plugin/plugin.json`, marketplace JSON
- **스크립트 / 테스트**: Python 3 `unittest`, POSIX shell
- **검증 명령**: `python3 -m unittest discover tests -v`
- **기존 분석**: [`.analysis/AI_CONTEXT.md`](../../.analysis/AI_CONTEXT.md)

## Out of Scope

- 공식 OpenAI/Anthropic 마켓플레이스 제출: 로컬 배포와 저장소 계약 안정화 후 별도 진행한다.
- 모든 스킬의 전면 재작성: 각 페이즈에서 필요한 경계와 플랫폼 확장만 변경한다.
- 모델별 품질 순위 벤치마크: 라우팅과 필수 결과 충족 여부만 평가한다.
- PR 생성·merge·공개 release: 각 단계는 별도 사용자 승인 후 진행한다.

## 페이즈 구성

### Phase 1: 안전 호출과 평가 기반

- **목표**: 위험한 GitHub Flow가 자동 발동하지 않고, preflight와 라우팅 계약을 테스트로 검증한다.
- **포함 기능**: 명시 호출 정책, dirty-tree 우선 확인, 행동 평가 fixture 및 계약 테스트
- **예상 소요**: 4~8시간
- **작업지시서**: [`skill-platform-modernization-phase-1-safety-evals.md`](./skill-platform-modernization-phase-1-safety-evals.md)
- **Checkpoint**: 전체 테스트 통과와 두 플랫폼의 명시 호출 정책 확인

### Phase 2: Codex 플러그인 통합

- **목표**: 워크플로 스킬과 source-analyzer MCP를 `code-workflow` Codex 플러그인 하나로 설치한다.
- **포함 기능**: 플러그인 bundle, marketplace 등록, 기존 설치기 호환 경로
- **예상 소요**: 6~10시간
- **작업지시서**: [`skill-platform-modernization-phase-2-codex-plugin.md`](./skill-platform-modernization-phase-2-codex-plugin.md)
- **Checkpoint**: 로컬 marketplace에서 플러그인이 발견되고 bundle 계약 테스트 통과

### Phase 3: Source Analyzer 책임 분리

- **목표**: 기본 분석과 instruction 등록·Wiki 게시를 분리하고 on-invoke 컨텍스트를 줄인다.
- **포함 기능**: 명시적 게시/등록 워크플로, reference 분리, 분석 전용 실행 경계
- **예상 소요**: 8~14시간
- **작업지시서**: [`skill-platform-modernization-phase-3-analyzer-boundaries.md`](./skill-platform-modernization-phase-3-analyzer-boundaries.md)
- **Checkpoint**: 기본 분석이 `.analysis/`만 수정하고 기존 검색·checkpoint 테스트 통과

### Phase 4: 크로스플랫폼 배포와 릴리스 정리

- **목표**: 설치 경로, MCP 실행, 문서와 버전 계약이 최신 배포 방식에 맞게 일치한다.
- **포함 기능**: 플랫폼별 설치 계약, README 마이그레이션, release metadata 자동 검증
- **예상 소요**: 6~8시간
- **작업지시서**: [`skill-platform-modernization-phase-4-release-hardening.md`](./skill-platform-modernization-phase-4-release-hardening.md)
- **Checkpoint**: 전체 테스트와 배포 smoke test 통과

## 페이즈 간 의존성

```text
Phase 1 안전 계약
  └─→ Phase 2 Codex 플러그인
        └─→ Phase 3 분석 책임 분리
              └─→ Phase 4 배포·릴리스 정리
```

Phase 1의 정책·평가 fixture를 이후 페이즈의 회귀 기준으로 사용하므로 순차 진행한다.

## 페이즈 간 전환 규칙

1. 해당 작업지시서의 체크박스와 자동 검증을 모두 완료한다.
2. diff 기반 리뷰에서 blocking finding이 없어야 한다.
3. 사용자에게 구현 결과와 남은 위험을 보고한다.
4. 사용자가 다음 페이즈 진행을 승인한 뒤 이동한다.

## 최종 완료 체크리스트

- [x] 모든 페이즈 Checkpoint 통과
- [x] `python3 -m unittest discover tests -v` 통과 (85 tests)
- [x] Codex와 Claude Code 플러그인 manifest/version 일치
- [x] 명시 호출 전용 스킬의 정책 회귀 테스트 통과
- [x] 기존 수동 설치 사용자를 위한 마이그레이션 안내 제공
- [x] README와 CHANGELOG 업데이트
