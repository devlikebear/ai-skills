# 프로젝트 개요

## 프로젝트명

AI Skills Repository (`ai-skills`)

## 한줄 요약

Codex 스킬과 Claude Code 플러그인을 한 저장소에서 함께 관리하고, `source-analyzer`로 그 구조를 재개 가능하게 문서화하는 리포지토리다.

## 현재 기준

- 버전: `0.6.1`
- 기준 커밋: `03eff382a1ef50e97ede4efbdf51331ba7b38439`
- 분석 범위: 저장소 루트 `.`

## 무엇을 담고 있나

- `codex/skills/`: 공개 Codex 스킬 6개를 보관한다.
- `claude-code/plugin/`: Claude Code용 `code-workflow` 플러그인과 공용 참조 문서를 보관한다.
- `.claude-plugin/marketplace.json`: 이 저장소를 Claude Code 마켓플레이스로 등록하는 메타데이터다.
- `.codex/skills/skill-generator/`: 이 저장소 전용 로컬 스킬 생성 래퍼다.
- `.analysis/`: 재개 가능한 분석 세션 상태와 Git 추적용 안정 산출물을 함께 보관한다.
- `scripts/`: Codex 설치와 분석 위키 게시를 담당하는 운영 스크립트가 있다.
- `tests/`: 구조 계약, 릴리스 규격, 체크포인트 매니저, 위키 게시 흐름을 검증한다.

## 0.6.x 기준 핵심 변화

1. 분석 세션 임시 상태는 `.analysis/sessions/`에 남기고, 안정 산출물은 `.analysis/outputs/`로 publish한다.
2. `source-analyzer`는 `SUMMARY.json`, `dependency-graph.json`, `module-map.json`, `issue-candidates.md`, `AI_CONTEXT.md`까지 만든다.
3. `checkpoint_manager.py`는 `publish`, `generate-summary`, `migrate`를 지원해 구형 세션 레이아웃도 흡수한다.
4. 테스트 스위트는 현재 `48`개 테스트로 저장소 구조와 릴리스 워크플로를 검증한다.

## 핵심 가치

1. 하나의 스킬 세트를 두 런타임에 맞게 재배포한다.
2. Codex 배포는 평평한 `SKILL.md + agents/ + shared/` 구조를 유지한다.
3. Claude Code 배포는 플러그인 매니페스트와 중앙 `references/` 디렉터리로 묶는다.
4. `source-analyzer`는 Git 커밋 기준의 증분 분석과 publish 가능한 문서 세트를 함께 제공한다.
5. 계약 테스트가 파일 구조, 버전 메타데이터, 스크립트 동작의 일관성을 지킨다.

## 처음 보는 사람이 먼저 읽을 곳

1. `VERSION.txt`와 `CHANGELOG.md`: 실제 릴리스 기준과 최근 변경을 확인한다.
2. `README.md`: 저장소의 큰 그림과 설치 경로를 빠르게 이해한다.
3. `codex/skills/source-analyzer/SKILL.md`: 가장 복잡한 스킬의 규칙을 본다.
4. `claude-code/plugin/.claude-plugin/plugin.json`: Claude Code 플러그인 포맷을 본다.
5. `tests/test_skill_repository_contract.py`: 이 저장소가 무엇을 계약으로 보는지 확인한다.

## 실제로 확인한 명령

- `scripts/install_codex_skill.sh --list`
- `python3 -m unittest discover -s tests`
- `python3 /Users/changheonshin/.codex/skills/source-analyzer/shared/scripts/checkpoint_manager.py sync --analysis-dir .analysis`

위 세 명령은 현재 커밋에서 정상 동작했고, 테스트는 `48`개가 통과했다.
