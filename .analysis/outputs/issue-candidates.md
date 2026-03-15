### TIDY-001: README 버전과 레이아웃 설명 동기화

- Module: `.`
- Type: `TIDY`
- Evidence: `README.md`는 현재 릴리스를 `0.4.0`으로 적고 있고 `.codex/skills/skill-generator/README.md`, `ko/`, `en/` 구조를 예시로 보여 준다. 하지만 실제 기준 파일인 `VERSION.txt`와 현재 트리는 `0.6.1` 및 flat layout을 사용한다.
- Suggested action: `README.md`의 현재 버전, 저장소 레이아웃 스니펫, skill-generator 설명을 `VERSION.txt`와 실제 디렉터리 구조에 맞게 갱신한다.

### TIDY-002: 위키 게시 입력을 안정 산출물로 전환

- Module: `scripts/`
- Type: `TIDY`
- Evidence: `scripts/publish_wiki.sh`는 `.analysis/sessions/<session-id>/outputs/`를 직접 읽는다. 반면 `source-analyzer`의 현재 publish 모델은 `.analysis/outputs/`를 Git 추적용 안정 결과로 사용한다.
- Suggested action: 위키 게시 스크립트가 기본적으로 `.analysis/outputs/`를 읽고, 필요하면 구형 세션 출력만 fallback 하도록 정리한다.

### DUP-001: 체크포인트 매니저 단일 소스 강제

- Module: `codex/skills/source-analyzer/shared/scripts`
- Type: `DUP`
- Evidence: `codex/skills/source-analyzer/shared/scripts/checkpoint_manager.py`와 `claude-code/plugin/scripts/checkpoint_manager.py`는 현재 동일하지만 수동으로 두 벌 유지된다. `CLAUDE.md`도 두 파일을 항상 동일하게 유지하라고 별도 규칙으로 강제한다.
- Suggested action: 한 파일을 원본으로 생성하거나, 최소한 두 파일의 바이트 단위 동일성을 검증하는 전용 계약 테스트를 추가한다.
