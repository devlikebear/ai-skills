# Phase 2: Codex 플러그인 통합 — 작업지시서

_작성일: 2026-07-22_
_속한 로드맵: [`skill-platform-modernization-roadmap.md`](./skill-platform-modernization-roadmap.md)_
_예상 소요: 6~10시간_
_상태: 완료_

## 페이즈 목표

Codex 사용자가 개별 복사 스크립트 대신 `code-workflow` 플러그인 하나로 6개 스킬과 선택적 source-analyzer MCP를 설치할 수 있게 한다. 기존 설치기는 즉시 삭제하지 않고 호환 경로로 남긴다.

## 전제 조건

- [x] Phase 1 완료 및 사용자 승인
- [x] 최신 Codex plugin manifest schema 재확인

## 작업 체크리스트

- [x] `plugins/code-workflow/.codex-plugin/plugin.json`과 install-surface metadata 추가
- [x] `plugins/code-workflow/skills/`에 6개 Codex 스킬 bundle 구성
- [x] source-analyzer MCP와 script 경로를 plugin root 기준으로 연결
- [x] `.agents/plugins/marketplace.json`에 `code-workflow` 등록
- [x] bundle과 canonical source의 drift 계약 테스트 추가
- [x] 기존 `install_codex_skill.sh`에 deprecated 안내와 마이그레이션 경로 추가

## ✅ Phase 2 Checkpoint

- [x] marketplace JSON과 plugin manifest 파싱 성공
- [x] 6개 스킬과 MCP entrypoint 존재
- [x] 전체 테스트 통과 — 82 tests
- [x] 로컬 Codex CLI에서 `code-workflow@ai-skills-local` 설치·활성 확인
