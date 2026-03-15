# 사용 기술

## 언어와 포맷

| 기술 | 용도 | 대표 경로 |
|------|------|-----------|
| Markdown | 스킬 정의, 참조 문서, 분석 산출물 | `README.md`, `codex/skills/*/SKILL.md`, `claude-code/plugin/references/*`, `.analysis/outputs/*` |
| YAML | Codex 에이전트 메타데이터 | `codex/skills/*/agents/openai.yaml`, `.codex/skills/skill-generator/agents/openai.yaml` |
| JSON | 플러그인 매니페스트, 마켓플레이스, 분석 상태와 구조 출력 | `.claude-plugin/marketplace.json`, `claude-code/plugin/.claude-plugin/plugin.json`, `.analysis/sessions/*/state.json`, `.analysis/outputs/*.json` |
| Bash | 설치와 위키 게시 자동화 | `scripts/install_codex_skill.sh`, `scripts/publish_wiki.sh` |
| Python 3 | 체크포인트 관리와 테스트 | `codex/skills/source-analyzer/shared/scripts/checkpoint_manager.py`, `tests/*.py` |

## Python 표준 라이브러리 사용처

| 모듈 | 사용 이유 | 대표 파일 |
|------|-----------|-----------|
| `argparse` | CLI 하위 명령 파싱 | `codex/skills/source-analyzer/shared/scripts/checkpoint_manager.py` |
| `json` | 상태 파일과 요약 JSON 저장/로드 | `codex/skills/source-analyzer/shared/scripts/checkpoint_manager.py`, `tests/test_publish_wiki.py` |
| `pathlib` | 경로 조작 | `codex/skills/source-analyzer/shared/scripts/checkpoint_manager.py`, `tests/*.py` |
| `subprocess` | Git 호출과 프로세스 실행 | `codex/skills/source-analyzer/shared/scripts/checkpoint_manager.py`, `tests/*.py` |
| `shutil` | publish/migrate 시 파일 복사 | `codex/skills/source-analyzer/shared/scripts/checkpoint_manager.py`, `tests/test_publish_wiki.py` |
| `datetime` | UTC 타임스탬프 생성 | `codex/skills/source-analyzer/shared/scripts/checkpoint_manager.py` |
| `re` | resume 포인터 파싱과 테스트 검증 | `codex/skills/source-analyzer/shared/scripts/checkpoint_manager.py`, `tests/test_skill_repository_contract.py` |
| `unittest` | 계약 테스트 실행 | `tests/test_checkpoint_manager.py`, `tests/test_release_contract.py`, `tests/test_skill_repository_contract.py`, `tests/test_publish_wiki.py` |

## 런타임과 도구

| 도구 | 역할 |
|------|------|
| Git | 커밋 해시 추적, 변경 파일 계산, 저장소 파일 열거, 위키 원격 push |
| Codex | `codex/skills/*` 런타임 대상 |
| Claude Code Plugin System | `code-workflow` 플러그인 설치 대상 |
| Shell 환경 | 설치 및 게시 스크립트 실행 환경 |

## 외부 의존성

패키지 매니저 파일이 없고, Python 코드도 표준 라이브러리만 사용한다. 이 저장소는 애플리케이션보다 배포 아티팩트와 규약 저장소에 가깝다.

## 실제 검증한 명령

```bash
scripts/install_codex_skill.sh --list
python3 -m unittest discover -s tests
```

첫 번째 명령은 공개 Codex 스킬 `6`개를 출력했다. 두 번째 명령은 현재 커밋에서 `48`개 테스트를 실행해 모두 통과했다.
