# 모듈: scripts (공유 스크립트)

프로젝트 전반에서 사용되는 Python/Bash 스크립트 모음.

## 역할

체크포인트 관리, 검색 인덱스, Wiki 발행, 스킬 설치, MCP 동기화 기능을 제공합니다.

## 핵심 파일

### checkpoint_manager.py (~900줄)

source-analyzer의 핵심 인프라. 세션 관리와 CLI 검색을 모두 처리합니다.

주요 함수:
- `init_session()`: 세션 생성 또는 기존 세션 재개
- `add_checkpoint()`: 체크포인트 markdown 생성 + 상태 업데이트
- `sync_session()`: git diff로 변경 파일 감지, frontier 업데이트
- `publish_outputs()`: 세션 outputs → `.analysis/outputs/` 복사
- `generate_summary()`: SUMMARY.json 생성
- `generate_search_index_for_session()`: 검색 인덱스 생성
- `migrate_layout()`: 구 레이아웃 마이그레이션
- `cli()`: 전체 CLI 엔트리포인트

### source_analyzer_search.py (~614줄)

검색 인덱스 빌더 겸 MCP 서버 백엔드.

주요 함수:
- `build_documents()`: 모든 outputs에서 검색 문서 추출
- `generate_search_index()`: JSONL + 매니페스트 파일 생성
- `search_analysis()`: 키워드 기반 스코어링 검색
- `trace_dependencies()`: 의존성 그래프 BFS 추적
- `get_module()`, `get_overview()`, `get_issue_candidates()`: 직접 조회

### publish_wiki.sh (~450줄)

GitHub Wiki 발행 스크립트.
- `find_latest_session()`: 최신 세션 탐색
- `build_sidebar()` / `build_home()`: Wiki 네비게이션 생성
- 페이지 정렬 (01-overview, 02-architecture 등)
- `--dry-run` / `--project-dir` / `--session-id` 옵션

### install_codex_skill.sh (~140줄)

Codex 스킬 인스톨러.
- `validate_skill_name()`: path traversal 방어
- `copy_skill()`: SKILL.md + agents + shared 복사
- `register_source_analyzer_mcp()`: `--with-mcp` 옵션으로 MCP 서버 등록

### sync_source_analyzer_mcp.sh (~25줄)

정식 MCP 소스(`servers/source-analyzer-mcp/`)를 5개 배포 위치에 동기화.
