# AI Skills — 클론 코딩 가이드

이 가이드는 AI Skills와 유사한 구조의 AI 에이전트 스킬 저장소를 처음부터 만드는 방법을 설명합니다.

## Phase 1: 기본 구조 설정

### 1.1 저장소 초기화

```bash
mkdir my-ai-skills && cd my-ai-skills
git init
```

### 1.2 핵심 파일 생성

```
VERSION.txt          → 0.1.0
CHANGELOG.md         → 릴리스 노트
CLAUDE.md            → 개발 가이드
LICENSE              → MIT
.gitignore           → __pycache__/, .analysis/sessions/
```

## Phase 2: 첫 번째 Codex 스킬

### 2.1 스킬 디렉토리 생성

```
codex/skills/my-skill/
  SKILL.md
  agents/openai.yaml
  shared/references/
```

### 2.2 SKILL.md 작성

```markdown
---
name: my-skill
description: "My first AI skill"
---

# My Skill

## Language policy
- Respond in the same language the user writes in.

## Workflow
1. ...
2. ...

## Output
- ...
```

### 2.3 에이전트 설정

```yaml
# agents/openai.yaml
display_name: "My Skill"
```

## Phase 3: Claude Code 플러그인 추가

### 3.1 플러그인 구조

```
claude-code/plugin/
  .claude-plugin/plugin.json
  skills/my-skill/SKILL.md
  references/
```

### 3.2 마켓플레이스 매니페스트

```json
// .claude-plugin/marketplace.json
{
  "name": "my-skills",
  "owner": {"name": "your-name"},
  "plugins": [{
    "name": "my-plugin",
    "source": "./claude-code/plugin"
  }]
}
```

## Phase 4: 설치 스크립트

### 4.1 Codex 인스톨러

`scripts/install_codex_skill.sh` 구현:
- 스킬 이름 검증 (path traversal 방어)
- `SKILL.md` + `agents/` + `shared/` 복사
- `$CODEX_HOME/skills/<name>/`에 설치

## Phase 5: source-analyzer 추가 (고급)

가장 복잡한 스킬. 다음 컴포넌트가 필요합니다:

1. **checkpoint_manager.py**: 세션 init/sync/checkpoint/publish CLI
2. **source_analyzer_search.py**: 검색 인덱스 빌더
3. **SKILL.md**: BFS 워크플로, 3개 모드 정의
4. **레퍼런스 템플릿**: refactor-template, overhaul-template 등

### 핵심 구현 순서

1. `init_session()` / `load_state()` / `save_state()`
2. `add_checkpoint()` with markdown 생성
3. `sync_session()` with git diff 연동
4. `publish_outputs()` — session → published 복사
5. `generate_search_index()` — JSONL 문서 생성
6. CLI `parse_args()` + `cli()` 함수

## Phase 6: 테스트

최소 3개 테스트 스위트:
- **구조 계약 테스트**: 모든 스킬이 올바른 구조를 따르는지 검증
- **릴리스 계약 테스트**: 버전 일관성, 인스톨러 작동
- **기능 테스트**: checkpoint_manager 세션 라이프사이클

## Phase 7: 배포 동기화

공유 스크립트를 여러 배포판에 복사해야 하는 경우:
- 정식 소스(canonical) 위치를 하나 정하고
- 동기화 스크립트로 다른 위치에 복사
- 테스트에서 동기화 상태를 검증

## 핵심 설계 원칙

1. **스킬은 지침서**: 코드가 아닌 워크플로 설명
2. **듀얼 배포**: 하나의 소스에서 Codex + Claude Code 모두 지원
3. **점진적 분석**: 대규모 코드베이스를 청크 단위로 분석하고 재개 가능
4. **zero 외부 의존성**: Python 표준 라이브러리만 사용
