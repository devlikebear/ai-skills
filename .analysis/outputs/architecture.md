# AI Skills — 아키텍처

## 전체 구조

```
┌─────────────────────────────────────────────────────┐
│                   ai-skills (repo root)             │
├─────────────┬──────────────────┬────────────────────┤
│  Codex      │  Claude Code     │  Canonical MCP     │
│  Distribution│  Distribution    │  Sources           │
├─────────────┼──────────────────┼────────────────────┤
│ codex/      │ claude-code/     │ servers/            │
│  skills/    │  plugin/         │  source-analyzer-   │
│   6 skills  │   skills/ (6)    │  mcp/               │
│   shared/   │   references/    │   server.py         │
│   agents/   │   scripts/       │   search.py         │
│             │   servers/       │                     │
├─────────────┼──────────────────┼────────────────────┤
│ plugins/    │ .claude-plugin/  │ .agents/plugins/    │
│ source-     │  marketplace.json│  marketplace.json   │
│ analyzer-   │                  │                     │
│ tools/      │                  │                     │
├─────────────┴──────────────────┴────────────────────┤
│  scripts/    tests/    .analysis/                    │
│  (installer, sync, wiki)  (6 test suites)           │
└─────────────────────────────────────────────────────┘
```

## 계층 구조

### 1. 스킬 계층 (Skill Layer)

각 스킬은 독립적인 SKILL.md 파일로 정의되며, 에이전트에게 워크플로를 지시합니다.

- **Codex 스킬**: `codex/skills/<name>/SKILL.md` + `agents/openai.yaml` + `shared/`
- **Claude Code 스킬**: `claude-code/plugin/skills/<name>/SKILL.md`
- 스킬 간 참조: `github-flow` → `plan` → `implement` → `review` (내부 루프)

### 2. 공유 리소스 계층 (Shared Resources Layer)

- **Codex**: 각 스킬의 `shared/references/`, `shared/scripts/`
- **Claude Code**: 플러그인 레벨 `references/`, `scripts/`
- 14개 레퍼런스 템플릿 (work-order, review-checklist, refactor-template 등)

### 3. 인프라 계층 (Infrastructure Layer)

- **checkpoint_manager.py** (~900줄): 세션 관리, 체크포인트, 발행, CLI 검색
- **source_analyzer_search.py** (~614줄): 검색 인덱스 생성, 스코어링, 의존성 추적
- **MCP 서버** (server.py): JSON-RPC stdio 프로토콜, 9개 도구 노출
- **publish_wiki.sh**: GitHub Wiki 페이지 생성 및 푸시

### 4. 배포/설치 계층 (Distribution Layer)

- **Claude Code 마켓플레이스**: `.claude-plugin/marketplace.json` → `code-workflow` 플러그인
- **Codex 로컬 설치**: `scripts/install_codex_skill.sh`
- **Codex MCP 플러그인**: `plugins/source-analyzer-tools/`
- **동기화**: `scripts/sync_source_analyzer_mcp.sh`가 정식 소스를 5곳에 배포

## 핵심 데이터 흐름

### 분석 흐름 (source-analyzer)

```
사용자 요청 → init(세션) → BFS 파일 순회 → 청크별 분석
→ checkpoint 기록 → outputs 발행(.analysis/outputs/)
→ 검색 인덱스 생성(cache/) → AI_CONTEXT.md 갱신
```

### 코드 워크플로 흐름 (github-flow)

```
Phase 1: Branch → Phase 2: Plan → Implement → Review → Commit (반복)
→ Phase 3: Push & PR → Phase 4: Merge → Phase 5: Tag/Release
```

### 배포 동기화 흐름

```
servers/source-analyzer-mcp/ (canonical)
  ↓ sync_source_analyzer_mcp.sh
  ├─ codex/.../shared/scripts/
  ├─ codex/.../shared/mcp/
  ├─ claude-code/plugin/scripts/
  ├─ claude-code/plugin/servers/
  └─ plugins/source-analyzer-tools/servers/
```

## Codex vs Claude Code 차이점

| 항목 | Codex | Claude Code |
|------|-------|-------------|
| 레퍼런스 경로 | `shared/references/...` | `../../references/...` |
| 스크립트 경로 | `$CODEX_HOME` 기반 | `$CLAUDE_PLUGIN_ROOT` 기반 |
| 도구 선호 | `rg, sed, head, tail, cat, find, ls` 명시 | 생략 (Claude Code 자체 도구 사용) |
| 폴백 파일 | `AGENTS.md` 생성 | `CLAUDE.md` 생성 |
| Plan 스킬명 | `plan-for-codex` | `plan` |
| 설치 방식 | `install_codex_skill.sh` | 플러그인 마켓플레이스 |
