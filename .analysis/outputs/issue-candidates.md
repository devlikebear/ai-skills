# Issue Candidates

source-analyzer analyze 모드에서 발견한 리팩토링/정리 후보입니다.

### DUP-001: checkpoint_manager.py 듀얼 배포 중복

- Module: `claude-code/plugin/scripts/`
- Type: `DUP`
- Evidence: checkpoint_manager.py가 codex와 claude-code 두 곳에 동일한 내용으로 유지되어야 하며, CLAUDE.md에서 수동 동기화를 요구합니다. sync 스크립트가 search/server만 커버하고 checkpoint_manager는 커버하지 않습니다.
- Suggested action: sync_source_analyzer_mcp.sh를 확장하여 checkpoint_manager.py��� canonical source에서 동기화하거나, 두 배포판이 동일 파일을 심볼릭 링크로 참조하도록 변경.

### DUP-002: MCP server.py 5곳 복사

- Module: `servers/source-analyzer-mcp/`
- Type: `DUP`
- Evidence: server.py와 source_analyzer_search.py가 각각 3곳, 5곳에 동일하게 복사됩니다. sync 스크립트가 있지만 수동 실행이 필요하며, 동기화 누락 시 drift 발생 가능.
- Suggested action: CI/pre-commit hook에서 sync 상태를 자동 검증하거나, 번들 복사 수를 줄이는 방안 검토.

### TIDY-001: .gitignore에 .analysis/cache/ 누락

- Module: `.gitignore`
- Type: `TIDY`
- Evidence: SKILL.md에서 cache/ 디렉토리는 git-ignored여야 한다고 명시하지만, .gitignore에 `.analysis/cache/` 패턴이 없습니다. 현재 `.analysis/sessions/`만 무시됩니다.
- Suggested action: `.gitignore`에 `.analysis/cache/` 추가.

### TIDY-002: Codex source-analyzer SKILL.md의 Prefer rg 라인

- Module: `codex/skills/source-analyzer/`
- Type: `TIDY`
- Evidence: CLAUDE.md에서 "Codex SKILL.md includes Prefer rg, sed... in constraints"라고 명시하지만, 실제 Codex SKILL.md에서 이 라인이 Constraints 섹션 내에 포함되어 있는지 확인 필요.
- Suggested action: Codex와 Claude SKILL.md의 Constraints 섹션 diff를 검증하는 계약 테스트 추가 검토.

### TIDY-003: publish_wiki.sh에서 outputs fallback 경로 로직

- Module: `claude-code/plugin/scripts/publish_wiki.sh`
- Type: `TIDY`
- Evidence: wiki 발행 스크립트가 세션 outputs → published outputs 두 단계로 폴백하는데, 0.6.0 이후 outputs가 항상 `.analysis/outputs/`에 publish되므로 세션 내부 outputs 경로를 먼저 시도하는 로직은 불필요할 수 있음.
- Suggested action: 세션 outputs 직접 참조를 제거하고 published outputs만 사용하도록 단순화.
