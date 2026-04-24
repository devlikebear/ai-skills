# 모듈: plugin (배포 인프라)

Claude Code 플러그인 마켓플레이스와 Codex 플러그인 배포 인프라.

## 역할

스킬들을 Claude Code 플러그인과 Codex 런타임으로 배포하는 매니페스트, 설정, 설치 스크립트를 관리합니다.

## 핵심 파일

| 파일 | 역할 |
|------|------|
| `.claude-plugin/marketplace.json` | Claude Code 마켓플레이스 매니페스트 (현재 버전: 0.11.0) |
| `claude-code/plugin/.claude-plugin/plugin.json` | code-workflow 플러그인 매니페스트 |
| `claude-code/plugin/.mcp.json` | MCP 서버 설정 |
| `.agents/plugins/marketplace.json` | Codex 로컬 마켓플레이스 |
| `plugins/source-analyzer-tools/` | Codex MCP 플러그인 번들 |
| `scripts/install_codex_skill.sh` | Codex 스킬 인스톨러 |
| `scripts/sync_source_analyzer_mcp.sh` | MCP 소스 동기화 |

## Claude Code 설치 흐름

```
/plugin marketplace add devlikebear/ai-skills
  → .claude-plugin/marketplace.json 읽기
  → source: ./claude-code/plugin 참조
/plugin install code-workflow@ai-skills
  → plugin.json + skills/ + references/ + scripts/ 설치
```

## Codex 설치 흐름

```
scripts/install_codex_skill.sh source-analyzer [--with-mcp]
  → codex/skills/source-analyzer/ → ~/.codex/skills/source-analyzer/ 복사
  → --with-mcp: codex mcp add source-analyzer-search -- python3 server.py
```

## 동기화

`sync_source_analyzer_mcp.sh`가 `servers/source-analyzer-mcp/`의 정식 소스를 5곳에 복사:
- `codex/.../shared/scripts/` (search.py)
- `codex/.../shared/mcp/` (server.py + search.py)
- `claude-code/plugin/scripts/` (search.py)
- `claude-code/plugin/servers/` (server.py + search.py)
- `plugins/source-analyzer-tools/servers/` (server.py + search.py)
