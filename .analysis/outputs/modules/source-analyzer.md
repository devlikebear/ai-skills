# 모듈: source-analyzer

BFS 기반 코드베이스 분석 스킬. 소스 파일을 수정하지 않고 아키텍처 문서, 리팩토링 제안, 시스템 오버홀 계획을 생성합니다.

## 역할

- 3가지 분석 모드: `analyze` (아키텍처 문서), `refactor-guide` (리팩토링 WO), `overhaul` (시스템 재설계)
- git 연동 점진적 분석: commit 기반 sync, 변경 파일 자동 재분석
- 검색 가능한 인덱스 생성 (CLI + MCP)
- GitHub Wiki 자동 발행

## 핵심 파일

| 파일 | 역할 |
|------|------|
| `claude-code/plugin/skills/source-analyzer/SKILL.md` | Claude Code 스킬 정의 |
| `codex/skills/source-analyzer/SKILL.md` | Codex 스킬 정의 |
| `claude-code/plugin/scripts/checkpoint_manager.py` | 세션/체크포인트/발행/CLI 검색 |
| `claude-code/plugin/scripts/source_analyzer_search.py` | 검색 인덱스 빌더 |
| `claude-code/plugin/scripts/publish_wiki.sh` | Wiki 발행 |
| `servers/source-analyzer-mcp/server.py` | MCP 서버 (정식 소스) |

## 세션 라이프사이클

```
init → [sync] → BFS 분석 → checkpoint(in_progress) → ... 
→ checkpoint(paused/completed) → auto-publish → search index 생성
```

## 출력물

- Markdown: overview, architecture, technologies, glossary, tutorial, clone-coding, implementation-checklist, modules/*
- JSON: SUMMARY.json, dependency-graph.json, module-map.json
- Bridge: issue-candidates.md (analyze → refactor 연결)
- Cache: search-documents.jsonl + 매니페스트 (CLI/MCP 검색용)

## CLI 명령

`checkpoint_manager.py` 하위 명령: `init`, `sync`, `checkpoint`, `status`, `publish`, `migrate`, `generate-summary`, `generate-search-index`, `search`, `get-overview`, `get-module`, `trace-deps`, `get-issues`
