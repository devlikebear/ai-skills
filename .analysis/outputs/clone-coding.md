# 클론 코딩 가이드: 비슷한 AI 스킬 저장소 만들기

> 대상 독자: 현재 저장소를 참고해 유사한 저장소를 새로 만들 개발자
> 예상 시간: 90분
> 기준 세션: `analyze-20260310-133920` / `checkpoint-004`

## 목표

Codex와 Claude Code 플러그인을 함께 지원하고, 분석 결과를 publish 가능한 문서로 남기는 최소 스킬 저장소를 직접 만든다.

## 준비물

- Git
- Bash 또는 Zsh
- Python 3
- 참고 파일:
  - `codex/skills/source-analyzer/SKILL.md`
  - `claude-code/plugin/skills/source-analyzer/SKILL.md`
  - `scripts/install_codex_skill.sh`
  - `tests/test_skill_repository_contract.py`

## Step 1. 저장소 뼈대 만들기

```bash
mkdir my-ai-skills
cd my-ai-skills
git init
mkdir -p codex/skills
mkdir -p claude-code/plugin/.claude-plugin
mkdir -p claude-code/plugin/skills
mkdir -p claude-code/plugin/references
mkdir -p claude-code/plugin/scripts
mkdir -p .claude-plugin
mkdir -p .analysis/outputs
mkdir -p .analysis/sessions
mkdir -p scripts
mkdir -p tests
```

다음 기본 파일도 만든다.

```bash
printf '0.1.0\n' > VERSION.txt
touch README.md CHANGELOG.md LICENSE .gitignore CLAUDE.md
```

`.gitignore`에는 최소한 `.analysis/sessions/`, `.install_test_home`, `__pycache__/`를 넣는다.

## Step 2. Codex 스킬 하나를 평평한 구조로 만들기

예를 들어 `plan` 성격의 스킬을 만든다면 아래처럼 시작한다.

```text
codex/skills/plan/
  SKILL.md
  agents/openai.yaml
  shared/references/work-order.md
```

핵심 규칙:

- `SKILL.md`는 하나만 둔다.
- language policy는 사용자 언어 자동 대응 규칙을 적는다.
- 공용 템플릿은 `shared/`로 뺀다.

## Step 3. 같은 기능을 Claude Code 플러그인으로도 패키징하기

플러그인 쪽은 같은 역할을 하되 `agents/openai.yaml` 없이 단일 `SKILL.md`만 둔다.

```text
claude-code/plugin/
  .claude-plugin/plugin.json
  skills/plan/SKILL.md
  references/work-order.md
```

그리고 저장소 루트에는 마켓플레이스 등록 파일을 둔다.

```text
.claude-plugin/marketplace.json
```

## Step 4. source-analyzer 스타일의 세션 도구 추가하기

분석 스킬을 만들 계획이라면 `checkpoint_manager.py` 같은 보조 스크립트를 두는 편이 좋다. 최소한 아래 파일과 명령 흐름은 갖춰야 한다.

```text
.analysis/
  RESUME.md
  AI_CONTEXT.md
  outputs/
    overview.md
    architecture.md
    SUMMARY.json
    dependency-graph.json
    module-map.json
    modules/
  sessions/<session-id>/
    state.json
    index.md
    checkpoints/
    outputs/
```

스크립트는 최소한 아래 명령을 제공하게 만든다.

- `init`
- `sync`
- `checkpoint`
- `status`
- `publish`
- `generate-summary`
- `migrate`(구형 레이아웃 호환이 필요하면)

## Step 5. 운영 스크립트와 계약 테스트 추가하기

최소 두 가지 자동화가 있으면 좋다.

1. Codex 설치 스크립트
2. 저장소 구조를 검증하는 테스트

분석 산출물을 공유할 계획이라면 위키 게시 스크립트도 별도 두는 편이 좋다.

## Step 6. 실제 검증 명령 준비하기

현재 저장소에서는 아래 두 명령이 가장 기본이다.

```bash
scripts/install_codex_skill.sh --list
python3 -m unittest discover -s tests
```

클론 코딩 결과도 최소한 같은 종류의 명령을 제공해야 온보딩이 쉽다.

## 자가검증 체크리스트

- [ ] Codex와 Claude Code 배포 구조를 둘 다 만들었다.
- [ ] 하나 이상의 `shared/references/*` 문서를 두었다.
- [ ] 설치 스크립트가 스킬 이름을 검증한다.
- [ ] 분석형 스킬이라면 `.analysis/sessions/`와 `.analysis/outputs/`를 분리했다.
- [ ] 테스트가 파일 구조와 릴리스 메타데이터를 검사한다.

## 확장 미션

1. `github-flow`와 같은 상위 오케스트레이션 스킬을 추가한다.
2. 분석 산출물을 위키로 게시하는 `publish_wiki.sh`와 비슷한 스크립트를 만든다.
3. 저장소 전용 작성 보조 스킬을 `.codex/skills/` 아래에 따로 둔다.
