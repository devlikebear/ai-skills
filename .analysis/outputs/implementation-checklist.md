# AI Skills — 구현 체크리스트

## 새 스킬 추가 체크리스트

- [ ] `codex/skills/<name>/SKILL.md` 생성 (YAML frontmatter + description 따옴표)
- [ ] `codex/skills/<name>/agents/openai.yaml` 생성
- [ ] `codex/skills/<name>/shared/` 디렉토리 생성
- [ ] `claude-code/plugin/skills/<name>/SKILL.md` 생성 (bilingual policy)
- [ ] Codex SKILL.md에 `shared/references/...` 경로 사용
- [ ] Claude SKILL.md에 `../../references/...` 경로 사용
- [ ] `test_skill_repository_contract.py`에 새 스킬 추가
- [ ] README.md에 스킬 설명 추가
- [ ] VERSION.txt 버전 범프 (minor)
- [ ] CHANGELOG.md 엔트리 추가

## 버전 범프 체크리스트

- [ ] `VERSION.txt`
- [ ] `.claude-plugin/marketplace.json` (version × 2)
- [ ] `claude-code/plugin/.claude-plugin/plugin.json` (version × 1)
- [ ] `plugins/source-analyzer-tools/.codex-plugin/plugin.json` (Codex 번들 변경 시)
- [ ] `CHANGELOG.md` (날짜 + 변경사항)

## 공유 스크립트 수정 체크리스트

- [ ] `checkpoint_manager.py` 수정 시 양쪽 동일하게 유지:
  - `codex/skills/source-analyzer/shared/scripts/checkpoint_manager.py`
  - `claude-code/plugin/scripts/checkpoint_manager.py`
- [ ] `source_analyzer_search.py` 수정 시 canonical → 5곳 동기화:
  - `scripts/sync_source_analyzer_mcp.sh` 실행
- [ ] `server.py` 수정 시 canonical → 3곳 동기화
- [ ] 동기화 후 `test_skill_repository_contract.py` 통과 확인

## 테스트 실행

```bash
python3 -m unittest discover tests -v
```

## 릴리스 체크리스트

- [ ] 모든 테스트 통과
- [ ] 버전 파일 동기화 완료
- [ ] CHANGELOG.md 업데이트
- [ ] 커밋 메시지: `feat:` (minor) / `fix:` (patch) / `chore:` (메타)
