# AI Skills — 튜토리얼

이 튜토리얼은 AI Skills 저장소를 처음 사용하는 개발자를 위한 단계별 가이드입니다.

## 1. 프로젝트 이해하기

AI Skills는 AI 에이전트(Codex, Claude Code)가 코드 작업을 수행할 때 사용하는 **표준화된 워크플로 스킬** 저장소입니다. 스킬은 SKILL.md 파일로 정의되며, 에이전트에게 "어떻게 작업해야 하는지"를 지시합니다.

### 핵심 개념

- **스킬 = SKILL.md**: 에이전트가 읽고 따르는 지침서
- **두 배포판**: 같은 스킬이 Codex용과 Claude Code용으로 각각 존재
- **source-analyzer**: 코드베이스를 분석하여 문서를 자동 생성하는 가장 복잡한 스킬

## 2. 스킬 사용해보기

### Codex에서 사용

```bash
# 스킬 설치
scripts/install_codex_skill.sh source-analyzer

# Codex에서 /source-analyzer 실행
```

### Claude Code에서 사용

```bash
# 마켓플레이스 추가
/plugin marketplace add devlikebear/ai-skills

# 플러그인 설치
/plugin install code-workflow@ai-skills

# 사용 예시
/code-workflow:source-analyzer   # 코드베이스 분석
/code-workflow:plan              # 작업 계획
/code-workflow:implement         # 구현 실행
/code-workflow:review            # 코드 리뷰
/code-workflow:refactor          # 리팩토링
/code-workflow:github-flow       # GitHub Flow
```

## 3. source-analyzer 워크플로

가장 복잡하고 기능이 많은 스킬입니다.

### 분석 시작

```bash
CHECKPOINT_SCRIPT="path/to/checkpoint_manager.py"
COMMIT=$(git rev-parse HEAD)
python3 "$CHECKPOINT_SCRIPT" init --mode analyze --scope "." --commit "$COMMIT"
```

### 분석 재개 (sync)

```bash
python3 "$CHECKPOINT_SCRIPT" sync
```

### 결과 검색

```bash
python3 "$CHECKPOINT_SCRIPT" search "authentication" --top-k 5
python3 "$CHECKPOINT_SCRIPT" get-module auth
python3 "$CHECKPOINT_SCRIPT" trace-deps src/auth.py --depth 2
python3 "$CHECKPOINT_SCRIPT" get-issues --type SEC
```

### 결과 발행

```bash
python3 "$CHECKPOINT_SCRIPT" publish
# 또는 GitHub Wiki로
bash publish_wiki.sh
```

## 4. 스킬 워크플로 체인

스킬들은 서로 연결되어 하나의 완전한 워크플로를 구성합니다:

```
source-analyzer (분석)
  → issue-candidates.md
    → refactor (리팩토링)

plan (계획)
  → work orders
    → implement (구현)
      → review (리뷰)

github-flow (전체 흐름)
  └─ plan → implement → review → commit (내부 루프)
```

## 5. 새 스킬 추가하기

`.codex/skills/skill-generator`를 사용하여 새 스킬을 생성할 수 있습니다.

필수 구조:
```
<skill-name>/
  SKILL.md              # 자동 언어 감지 정책 포함
  agents/openai.yaml    # Codex 에이전트 설정
  shared/               # 공유 리소스 (선택)
```

규칙:
- 단일 `SKILL.md` 파일 (ko/, en/ 디렉토리 불가)
- YAML frontmatter의 description은 반드시 따옴표로 감싸기
- 재사용 가능한 내용은 `shared/`에 배치
