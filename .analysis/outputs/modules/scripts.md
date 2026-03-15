# 모듈: scripts

## 역할

저장소의 공개 배포와 분석 결과 게시를 운영하는 Bash 스크립트 모음이다.

## 파일

### `scripts/install_codex_skill.sh`

Codex 공개 스킬을 `${CODEX_HOME:-$HOME/.codex}/skills`에 설치한다.

- `--list`: 공개 스킬 목록 출력
- `--all`: 모든 공개 스킬 설치
- `<skill-name>`: 하나의 스킬 설치

보안상 스킬 이름은 `^[a-z0-9][a-z0-9-]*$` 정규식으로 검증한다. 설치 시에는 `SKILL.md`, `shared/`, `agents/`를 복사하고 `__pycache__`를 제거한다.

### `scripts/publish_wiki.sh`

가장 최근 또는 지정한 `.analysis` 세션의 산출물을 GitHub Wiki 페이지로 변환해 푸시한다.

- 기본 입력: `.analysis/sessions/<session-id>/outputs/`
- 옵션: `--session-id <id>`, `--dry-run`
- 동작: 위키 저장소 clone -> 문서 복사 및 `Home.md`/`_Sidebar.md` 생성 -> Git commit -> push

이 스크립트는 분석 문서 파일 이름과 각 모듈 문서의 `## 역할` 단락을 기준으로 위키 네비게이션을 만든다.

## 입문자가 먼저 볼 파일

1. `scripts/install_codex_skill.sh`
2. `scripts/publish_wiki.sh`
3. `tests/test_release_contract.py`
4. `tests/test_publish_wiki.py`
