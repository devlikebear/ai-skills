# 모듈: tests

프로젝트의 테스트 스위트.

## 역할

저장소 구조 계약, 릴리스 계약, 기능 동작을 검증하는 6개 테스트 파일로 구성됩니다.

## 핵심 파일

| 파일 | 테스트 수 (대략) | 범위 |
|------|-----------------|------|
| `test_checkpoint_manager.py` | 25+ | 세션 init/checkpoint/sync/publish/migrate |
| `test_skill_repository_contract.py` | 25+ | 구조, 동기화, 마켓플레이스, MCP |
| `test_release_contract.py` | 4 | 버전, changelog, gitignore, 인스톨러 |
| `test_source_analyzer_search.py` | 10+ | 검색 인덱스 생성, 스코어링, 조회 |
| `test_codex_mcp_install.py` | 3+ | Codex MCP 설치 흐름 |
| `test_publish_wiki.py` | 5+ | Wiki 페이지 생성 검증 |

## 테스트 패턴

- `unittest` 프레임워크 (외부 의존성 없음)
- `tempfile.TemporaryDirectory`로 격리된 파일시스템 테스트
- `unittest.mock.patch`로 git 명령 모킹
- `importlib.util`로 checkpoint_manager.py 동적 로드

## 핵심 계약 테스트

- **구조 계약**: 모든 SKILL.md의 frontmatter description이 따옴표로 감싸져 있는지, flat 구조인지, 언어 정책이 올바른지
- **동기화 계약**: `source_analyzer_search.py`가 5곳에서 동일한지, `server.py`가 3곳에서 동일한지
- **마켓플레이스 계약**: marketplace.json, plugin.json이 올바른 구조인지
- **릴리스 계약**: VERSION.txt 형식, CHANGELOG에 버전 포함, 인스톨러가 path traversal 거부

## 실행

```bash
python3 -m unittest discover tests -v
```
