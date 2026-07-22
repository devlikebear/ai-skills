# Phase 3: Source Analyzer 책임 분리 — 작업지시서

_작성일: 2026-07-22_
_속한 로드맵: [`skill-platform-modernization-roadmap.md`](./skill-platform-modernization-roadmap.md)_
_예상 소요: 8~14시간_

## 페이즈 목표

`source-analyzer`의 기본 계약을 `.analysis/` 산출물 생성으로 제한한다. 프로젝트 instruction 파일 등록과 GitHub Wiki 게시는 명시 호출 전용 워크플로로 분리하고, 핵심 `SKILL.md`에는 모드 선택과 필수 절차만 남긴다.

## 전제 조건

- [x] Phase 2 완료 및 사용자 승인

## 작업 체크리스트

- [x] instruction 파일 수정과 `.analysis/` 전용 제약의 충돌을 실패 테스트로 고정
- [x] Wiki 게시를 명시 호출 전용 skill 또는 command로 분리
- [x] analysis context 등록을 명시 호출 전용 skill 또는 산출 snippet으로 분리
- [x] directory schema, migration, CLI 상세를 references로 이동
- [x] analyze/refactor-guide/overhaul 라우팅 경계와 설명을 명확화
- [x] Claude 대용량 분석의 전용 agent 격리 가능성 검증
- [x] 검색·checkpoint·publish 기존 테스트 회귀 확인

## ✅ Phase 3 Checkpoint

- [x] 기본 분석은 `.analysis/` 밖을 수정하지 않음
- [x] 외부 Wiki 게시에는 명시 호출이 필요함
- [x] 두 배포본의 핵심 동작이 동기화됨
- [x] 전체 테스트 통과 (82 tests)
