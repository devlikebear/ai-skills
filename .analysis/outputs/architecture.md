# 아키텍처

## 최상위 구조

```text
ai-skills/
├── .analysis/                      # 분석 세션 상태와 publish 산출물
├── .claude-plugin/                 # Claude Code 마켓플레이스 등록 정보
├── .codex/skills/skill-generator/  # 저장소 전용 로컬 래퍼 스킬
├── claude-code/plugin/             # Claude Code 플러그인 배포본
├── codex/skills/                   # 공개 Codex 스킬 소스
├── scripts/                        # 설치/게시 자동화
├── tests/                          # 계약 테스트와 스크립트 테스트
├── README.md
├── CLAUDE.md
├── CHANGELOG.md
├── VERSION.txt
└── LICENSE
```

## 설계 레이어

| 레이어 | 경로 | 책임 |
|--------|------|------|
| 릴리스/온보딩 | `README.md`, `CLAUDE.md`, `CHANGELOG.md`, `VERSION.txt`, `.claude-plugin/marketplace.json` | 버전, 설치 방법, 운영 규칙, 마켓플레이스 진입점 제공 |
| 공개 Codex 배포 | `codex/skills/*` | Codex가 읽는 스킬 정의, 에이전트 메타데이터, 공용 참조 파일 제공 |
| 로컬 작성 보조 | `.codex/skills/skill-generator/` | 이 저장소 규칙에 맞는 새 Codex 스킬 생성을 돕는 래퍼 제공 |
| Claude Code 플러그인 배포 | `claude-code/plugin/*` | `code-workflow` 플러그인, 공용 참조 문서, 플러그인용 스크립트 제공 |
| 분석 런타임 | `.analysis/sessions/*`, `.analysis/outputs/*` | 증분 분석 상태와 Git 추적용 안정 결과를 분리 저장 |
| 운영 보조 | `scripts/*`, `tests/*` | 설치, 위키 게시, 구조 검증, 릴리스 계약 검증 제공 |

## 핵심 흐름 1: Codex 설치

```text
codex/skills/<skill>/
  -> scripts/install_codex_skill.sh
  -> ${CODEX_HOME:-$HOME/.codex}/skills/<skill>/
  -> Codex가 SKILL.md + shared/ + agents/ 를 로드
```

설치 스크립트는 스킬 이름을 검증한 뒤 `SKILL.md`, `shared/`, `agents/`만 복사한다. 이 과정에서 `__pycache__`는 제거된다.

## 핵심 흐름 2: Claude Code 플러그인 설치

```text
.claude-plugin/marketplace.json
  -> claude-code/plugin/.claude-plugin/plugin.json
  -> claude-code/plugin/skills/*
  -> /plugin install code-workflow@ai-skills
```

Claude Code는 개별 `agents/openai.yaml` 대신 플러그인 매니페스트와 단일 bilingual `SKILL.md`를 사용한다. 공용 문서는 `claude-code/plugin/references/`에서 한 번만 유지한다.

## 핵심 흐름 3: source-analyzer 세션과 publish

```text
git rev-parse HEAD
  -> checkpoint_manager.py init --commit <sha>
  -> git ls-tree -r HEAD --name-only -- <scope>
  -> BFS 청크별 분석
  -> .analysis/sessions/<session-id>/{state.json,index.md,checkpoints/,outputs/}
  -> checkpoint --status paused|completed
  -> .analysis/outputs/*
  -> generate-summary + AI_CONTEXT.md
```

세션 중간 상태는 `.analysis/sessions/`에 남고, 사람이 다시 읽거나 커밋할 안정 산출물은 `.analysis/outputs/`에 복사된다. `migrate`는 pre-0.6.0 세션 출력만 있던 레이아웃을 현재 구조로 끌어올린다.

## 핵심 흐름 4: 위키 게시

```text
.analysis session outputs
  -> scripts/publish_wiki.sh
  -> Home.md / _Sidebar.md / module-*.md
  -> GitHub wiki remote
```

위키 게시 스크립트는 분석 문서 파일명을 기반으로 페이지 순서를 정하고, 각 모듈 문서의 `## 역할` 단락을 Home 설명으로 재사용한다.

## 디렉터리별 관찰 포인트

- `codex/skills/source-analyzer/shared/scripts/checkpoint_manager.py`와 `claude-code/plugin/scripts/checkpoint_manager.py`는 현재 바이트 단위로 동일하다.
- `codex/skills/*/shared/references/`는 스킬별로 필요한 템플릿만 두고, 플러그인 쪽은 `claude-code/plugin/references/`에 공용 템플릿을 중앙화한다.
- `.analysis/outputs/`는 `overview.md`, `modules/*.md`, `SUMMARY.json` 같은 안정 결과를 담고, `.analysis/sessions/`는 작업 중 상태를 담는다.
- `tests/`는 애플리케이션 런타임보다 저장소 구조와 배포 계약을 더 강하게 검증한다.

## 입문자에게 중요한 설계 결정

1. Codex는 설치 가능한 파일 트리를 직접 복사하는 모델이다.
2. Claude Code는 플러그인 메타데이터와 공용 `references/` 디렉터리로 묶어 배포한다.
3. `source-analyzer`는 분석 결과 자체뿐 아니라 재개 안전성과 publish 가능한 산출물 모델을 핵심 가치로 둔다.
4. 저장소의 진짜 복잡도는 코드량보다 문서 규약, 버전 메타데이터, 테스트 계약에서 나온다.
