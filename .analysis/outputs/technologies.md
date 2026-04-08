# AI Skills — 기술 스택

## 언어

| 언어 | 용도 | 파일 |
|------|------|------|
| Python 3 | 체크포인트 관리, 검색 인덱스, MCP 서버, 테스트 | `checkpoint_manager.py`, `source_analyzer_search.py`, `server.py`, `tests/` |
| Bash | 설치, 동기화, Wiki 발행 | `install_codex_skill.sh`, `sync_source_analyzer_mcp.sh`, `publish_wiki.sh` |
| Markdown | 스킬 정의, 레퍼런스 템플릿, 분석 결과물 | `SKILL.md`, `references/`, `.analysis/outputs/` |
| JSON | 상태 관리, 매니페스트, 구조화된 출력 | `state.json`, `plugin.json`, `marketplace.json`, `SUMMARY.json` |
| YAML | Codex 에이전트 설정 | `agents/openai.yaml` |

## 프레임워크 및 프로토콜

| 기술 | 용도 |
|------|------|
| MCP (Model Context Protocol) | 분석 결과 검색 서버 (JSON-RPC 2.0 over stdio) |
| unittest (Python) | 모든 테스트 (구조 계약, 릴리스 계약, 기능 테스트) |
| git CLI | 커밋 추적, 파일 변경 감지, incremental sync |
| GitHub CLI (`gh`) | PR 생성, 릴리스, Wiki 푸시 |

## 외부 의존성

프로젝트는 **외부 패키지 의존성이 없습니다**. Python 표준 라이브러리만 사용합니다:
- `argparse`, `json`, `pathlib`, `subprocess`, `unittest`, `importlib.util`, `shutil`, `re`, `datetime`, `tempfile`

MCP 서버를 `uvx`로 실행할 때만 `hatchling` 빌드 시스템이 사용됩니다 (`pyproject.toml`).

## 도구 체인

| 도구 | 역할 |
|------|------|
| `git` | 버전 관리, 변경 파일 감지 (sync), 커밋된 파일 열거 |
| `python3` | 스크립트 실행, MCP 서버, 테스트 |
| `bash` | 설치/동기화/발행 스크립트 |
| `uvx` | MCP 서버 패키지 실행 (선택적) |
