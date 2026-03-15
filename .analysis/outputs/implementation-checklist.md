# 구현 체크리스트

## Phase 1. 저장소 골격

- [ ] `codex/skills/`, `claude-code/plugin/`, `.claude-plugin/`, `.analysis/outputs/`, `.analysis/sessions/`, `scripts/`, `tests/` 디렉터리를 만든다.
- [ ] `README.md`, `CLAUDE.md`, `CHANGELOG.md`, `VERSION.txt`, `LICENSE`, `.gitignore`를 만든다.
- [ ] `.gitignore`에 `.analysis/sessions/`, `.install_test_home`, `__pycache__/`를 넣는다.

## Phase 2. 공개 Codex 스킬

- [ ] 공개할 스킬별로 `codex/skills/<skill>/SKILL.md`를 만든다.
- [ ] 각 스킬에 `agents/openai.yaml`을 둔다.
- [ ] 재사용 자료는 `codex/skills/<skill>/shared/`로 분리한다.
- [ ] `SKILL.md` frontmatter의 `description` 값을 항상 쌍따옴표로 감싼다.
- [ ] 언어별 `ko/`, `en/` 디렉터리를 만들지 않는다.

## Phase 3. Claude Code 플러그인

- [ ] `claude-code/plugin/.claude-plugin/plugin.json`을 만든다.
- [ ] `claude-code/plugin/skills/` 아래에 플러그인 스킬을 만든다.
- [ ] 공용 참조 문서를 `claude-code/plugin/references/`에 모은다.
- [ ] 플러그인 스킬에는 bilingual language policy를 적는다.
- [ ] 플러그인 스킬이 `CODEX_HOME`을 참조하지 않게 한다.

## Phase 4. source-analyzer 세션 도구

- [ ] `checkpoint_manager.py`에 `init`, `sync`, `checkpoint`, `status`, `publish`, `generate-summary`를 구현한다.
- [ ] 필요하면 구형 산출물 호환용 `migrate`를 추가한다.
- [ ] 세션 디렉터리에 `state.json`, `index.md`, `checkpoints/`, `outputs/`를 만든다.
- [ ] publish 대상 디렉터리인 `.analysis/outputs/`를 별도로 유지한다.
- [ ] `RESUME.md`와 `AI_CONTEXT.md`를 최신 상태로 유지한다.
- [ ] `sync`가 저장된 커밋과 현재 HEAD를 비교하도록 만든다.
- [ ] 커밋된 파일만 분석하도록 `git ls-tree -r HEAD --name-only`를 사용한다.

## Phase 5. 구조화 출력

- [ ] 사람용 문서 `overview.md`, `architecture.md`, `technologies.md`, `glossary.md`를 만든다.
- [ ] `modules/*.md`를 만들어 논리 모듈별 책임을 설명한다.
- [ ] `SUMMARY.json`, `dependency-graph.json`, `module-map.json`을 만든다.
- [ ] 분석 결과에서 `issue-candidates.md`를 뽑아 다음 리팩터링 입력으로 남긴다.

## Phase 6. 운영 스크립트

- [ ] `scripts/install_codex_skill.sh`를 만들어 `--list`, `--all`, `<skill-name>`을 지원한다.
- [ ] 설치 스크립트에서 스킬 이름을 정규식으로 검증한다.
- [ ] 설치 시 `SKILL.md`, `shared/`, `agents/`만 복사한다.
- [ ] 필요하다면 `.analysis` 산출물을 게시하는 `scripts/publish_wiki.sh`를 만든다.

## Phase 7. 테스트

- [ ] `tests/test_skill_repository_contract.py`로 구조 계약을 검증한다.
- [ ] `tests/test_checkpoint_manager.py`로 체크포인트 도구를 검증한다.
- [ ] `tests/test_release_contract.py`로 릴리스 메타데이터와 설치 보안을 검증한다.
- [ ] 게시 스크립트가 있으면 별도 테스트를 둔다.
- [ ] `python3 -m unittest discover -s tests`가 통과하는지 확인한다.

## Phase 8. 릴리스

- [ ] `VERSION.txt`를 SemVer 형식으로 유지한다.
- [ ] `CHANGELOG.md`에 현재 버전과 변경 사항을 적는다.
- [ ] `README.md`에 Codex 설치와 Claude Code 플러그인 설치 방법을 모두 적는다.
- [ ] 분석 진입점인 `AI_CONTEXT.md`를 프로젝트 지침 파일에서 발견 가능하게 만든다.
