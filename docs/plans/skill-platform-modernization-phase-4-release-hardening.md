# Phase 4: 크로스플랫폼 배포와 릴리스 정리 — 작업지시서

_작성일: 2026-07-22_
_속한 로드맵: [`skill-platform-modernization-roadmap.md`](./skill-platform-modernization-roadmap.md)_
_예상 소요: 6~8시간_

## 페이즈 목표

Codex와 Claude Code의 최신 설치 경로, MCP 실행 방식, manifest와 README를 일치시킨다. macOS 전용 PATH나 shell 가정을 줄이고, 한 버전 변경으로 모든 배포 metadata가 검증되도록 한다.

## 전제 조건

- [x] Phase 3 완료 및 사용자 승인

## 작업 체크리스트

- [x] Codex `.agents/skills`와 plugin 배포 기준으로 README 갱신
- [x] legacy `${CODEX_HOME}/skills` 경로의 지원 범위와 종료 계획 명시
- [x] Claude MCP launcher에서 고정 macOS PATH와 `bash -c` 의존 재검토
- [x] macOS/Linux/Windows 경로 계약 테스트 또는 smoke matrix 추가
- [x] VERSION, marketplace, plugin manifest, CHANGELOG 동기화 자동 검증
- [x] 설치·업데이트·rollback 문서화

## ✅ Phase 4 Checkpoint

- [x] 전체 테스트 통과
- [x] 두 플랫폼의 설치 문서와 실제 bundle 일치
- [x] version contract 통과
- [x] 지원 플랫폼 smoke 결과 기록
