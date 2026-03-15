# 모듈: tests

## 역할

이 저장소가 약속한 파일 구조, 릴리스 메타데이터, 체크포인트 세션 동작, 위키 게시 흐름을 자동으로 검증한다.

## 실제 실행 결과

`python3 -m unittest discover -s tests`를 실행해 `48`개 테스트가 통과했다.

## 파일별 책임

### `tests/test_skill_repository_contract.py`

`15`개 테스트가 공개 Codex 스킬, 로컬 skill-generator, Claude Code 플러그인, 마켓플레이스 JSON의 구조 계약을 검증한다.

핵심 검증:

- 모든 `SKILL.md`의 `description` frontmatter가 쌍따옴표인지
- 공개 Codex 스킬 6개가 평평한 구조를 지키는지
- 플러그인 스킬 6개가 존재하고 bilingual 정책을 가지는지
- 플러그인 스킬이 `CODEX_HOME`을 참조하지 않는지
- `source-analyzer`가 `CLAUDE_PLUGIN_ROOT`를 사용하는지

### `tests/test_checkpoint_manager.py`

`28`개 테스트가 `checkpoint_manager.py`의 세션 생성, 체크포인트 기록, Git helper, exclude 규칙, `sync`, `publish`, `migrate`, `generate-summary`를 검증한다.

### `tests/test_release_contract.py`

`4`개 테스트가 `VERSION.txt`, `CHANGELOG.md`, `LICENSE`, `.gitignore`, 설치 스크립트 보안 규칙을 검증한다.

### `tests/test_publish_wiki.py`

`1`개 테스트가 `scripts/publish_wiki.sh`가 세션 outputs에서 모듈 링크와 Home/Sidebar를 올바르게 생성하는지 검증한다.

## 입문자가 먼저 볼 파일

1. `tests/test_skill_repository_contract.py`
2. `tests/test_checkpoint_manager.py`
3. `tests/test_release_contract.py`
4. `tests/test_publish_wiki.py`

## 테스트 철학

이 저장소는 애플리케이션 런타임보다 배포 구조가 중요하므로, 테스트도 기능 테스트보다 계약 테스트 비중이 높다.
