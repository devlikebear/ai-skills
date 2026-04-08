# AI Skills — 용어집

| 용어 | 설명 |
|------|------|
| **Skill** | AI 에이전트에게 특정 워크플로를 지시하는 SKILL.md 기반 지침 |
| **Work Order (WO)** | 30-90분 단위의 구체적 작업 지시서. plan 스킬이 생성하고 implement 스킬이 실행 |
| **Checkpoint** | source-analyzer의 분석 진행 스냅샷. 상태, 방문 파일, 프론티어, 결과물 포함 |
| **Session** | source-analyzer의 분석 단위. `.analysis/sessions/<id>/`에 상태 저장 |
| **BFS** | Breadth-First Search. source-analyzer가 파일을 순회하는 방식 |
| **Frontier** | BFS에서 아직 방문하지 않은 파일 목록 |
| **Publish** | 세션 outputs를 `.analysis/outputs/`로 복사하여 git 추적 가능하게 만드는 과정 |
| **Sync** | 이전 커밋 이후 변경된 파일을 감지하여 frontier에 추가하는 과정 |
| **MCP** | Model Context Protocol. AI 에이전트가 외부 도구와 통신하는 JSON-RPC 2.0 프로토콜 |
| **Marketplace** | Claude Code 플러그인 배포를 위한 매니페스트 시스템 |
| **Plugin** | Claude Code에서 설치 가능한 스킬 묶음 (code-workflow) |
| **DUP/SEC/TIDY** | refactor-guide 모드의 이슈 분류 코드 (중복/보안/정리) |
| **ARCH/DEAD/OVER/DEBT** | overhaul 모드의 이슈 분류 코드 (아키텍처/불필요/과잉/부채) |
| **Inner Loop** | github-flow Phase 2의 반복 구조: plan → implement → review → commit |
| **Canonical Source** | `servers/source-analyzer-mcp/`의 정식 MCP 소스. 다른 위치는 이것의 복사본 |
| **Flat Layout** | Codex 스킬의 구조 규칙: `SKILL.md` + `agents/` + `shared/` (언어별 디렉토리 없음) |
| **Bilingual** | Claude Code 스킬의 언어 정책: 사용자 언어를 자동 감지하여 응답 |
