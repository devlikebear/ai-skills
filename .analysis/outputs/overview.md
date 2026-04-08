# AI Skills — 프로젝트 개요

AI Skills는 코드 워크플로 자동화를 위한 재사용 가능한 AI 에이전트 스킬 저장소입니다. Codex와 Claude Code 두 가지 런타임을 동시에 지원하며, 현재 버전은 **0.10.8**입니다.

## 핵심 목적

- 코드베이스 분석, 계획, 구현, 리뷰, 리팩토링, GitHub Flow를 AI 에이전트 스킬로 표준화
- 하나의 소스에서 Codex 스킬과 Claude Code 플러그인 두 배포판을 동시 관리
- `source-analyzer` 스킬로 프로젝트 아키텍처 문서, 리팩토링 제안, 시스템 오버홀 계획을 자동 생성

## 배포 구조

| 배포판 | 경로 | 설치 방법 |
|--------|------|-----------|
| Codex 스킬 | `codex/skills/` | `scripts/install_codex_skill.sh <skill>` |
| Claude Code 플러그인 | `claude-code/plugin/` | `/plugin marketplace add devlikebear/ai-skills` |
| Codex MCP 플러그인 | `plugins/source-analyzer-tools/` | `--with-mcp` 플래그 또는 별도 설치 |

## 포함된 스킬 (6개)

| 스킬 | 역할 |
|------|------|
| `plan` / `plan-for-codex` | 요청을 ≤3개 작업 지시서로 분할 |
| `implement` | 작업 지시서를 직접 실행 |
| `review` | diff 기반 코드 리뷰 (회귀, 보안, 테스트) |
| `refactor` | 동작 보존 리팩토링 |
| `source-analyzer` | BFS 코드베이스 분석 (3개 모드) |
| `github-flow` | 전체 GitHub Flow 라이프사이클 |

## 주요 인프라

- **checkpoint_manager.py**: 세션 기반 점진적 분석, git 연동 sync, CLI 검색 명령
- **source_analyzer_search.py**: 키워드 검색 인덱스 빌더 및 MCP 서버 백엔드
- **publish_wiki.sh**: GitHub Wiki로 분석 결과 자동 발행
- **sync_source_analyzer_mcp.sh**: 정식 MCP 소스를 5개 배포 위치에 동기화
