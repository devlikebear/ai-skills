# 튜토리얼: AI Skills 저장소 이해하기

> 대상 독자: 이 저장소에 처음 들어온 개발자
> 예상 시간: 45-60분
> 기준 세션: `analyze-20260310-133920` / `checkpoint-004`

## 학습 목표

- 이 저장소가 왜 Codex와 Claude Code를 함께 지원하는지 설명할 수 있다.
- `codex/skills/`와 `claude-code/plugin/`의 역할 차이를 설명할 수 있다.
- `source-analyzer` 세션이 어떻게 publish 가능한 결과로 이어지는지 파일 경로 기준으로 추적할 수 있다.
- 설치 명령과 테스트 명령을 직접 실행해 저장소 상태를 검증할 수 있다.

## 사전지식과 실행환경

- 필수 사전지식: Git, Bash, Markdown, Python `unittest` 기초
- 런타임: Git, Bash 또는 Zsh, Python 3
- 먼저 써볼 명령:
  - `scripts/install_codex_skill.sh --list`
  - `python3 -m unittest discover -s tests`
- 시작 파일: `README.md`

## 아키텍처 한눈에 보기

| 레이어 | 경로 | 책임 |
|--------|------|------|
| 공개 Codex 스킬 | `codex/skills/*` | Codex가 직접 설치해 읽는 스킬 소스 |
| 로컬 작성 보조 | `.codex/skills/skill-generator/*` | 저장소 작성자용 래퍼 스킬 |
| Claude Code 플러그인 | `claude-code/plugin/*` | `code-workflow` 플러그인과 공용 참조 |
| 분석 런타임 | `.analysis/sessions/*`, `.analysis/outputs/*` | 증분 분석 상태와 안정 산출물 |
| 운영 자동화 | `scripts/*`, `tests/*` | 설치, 위키 게시, 계약 검증 |

```text
User request
  -> SKILL.md
  -> shared references or plugin references
  -> optional scripts/tests
  -> source-analyzer only:
     .analysis/sessions/<session-id>/outputs/*
     -> .analysis/outputs/*
     -> .analysis/AI_CONTEXT.md
```

## Step 1. 릴리스 기준 파일 읽기

`VERSION.txt`와 `CHANGELOG.md`를 먼저 읽는다. 현재 실제 릴리스 기준은 `0.6.1`이며, `publish`, `migrate`, 구조 JSON 출력이 최근 변화의 핵심이다.

`README.md`는 큰 그림을 설명하는 문서로 유용하지만, 버전이나 일부 레이아웃 설명은 `VERSION.txt`와 `CHANGELOG.md`보다 덜 신뢰할 수 있다.

확인 포인트:

- [ ] 실제 현재 버전이 `0.6.1`이라는 점을 찾았다.
- [ ] `0.6.x`에서 `.analysis/outputs/` 개념이 추가된 점을 찾았다.

참고 파일:

- `VERSION.txt`
- `CHANGELOG.md`
- `README.md`

## Step 2. Codex 스킬 하나를 깊게 보기

가장 먼저 `codex/skills/source-analyzer/SKILL.md`를 읽는다. 그다음 `codex/skills/source-analyzer/shared/scripts/checkpoint_manager.py`와 `codex/skills/source-analyzer/shared/references/tutorial-template.md`를 보면 스킬 설명, 보조 템플릿, 실제 도구가 어떻게 나뉘는지 보인다.

확인 포인트:

- [ ] 단일 `SKILL.md`와 `shared/` 구조를 이해했다.
- [ ] `init -> sync -> checkpoint -> publish -> generate-summary` 흐름을 말로 설명할 수 있다.

참고 파일:

- `codex/skills/source-analyzer/SKILL.md`
- `codex/skills/source-analyzer/shared/scripts/checkpoint_manager.py`
- `codex/skills/source-analyzer/shared/references/tutorial-template.md`

## Step 3. Claude Code 플러그인 구조 보기

`claude-code/plugin/.claude-plugin/plugin.json`과 `claude-code/plugin/skills/source-analyzer/SKILL.md`를 읽는다. Codex와 달리 `agents/openai.yaml`이 없고, 공용 참조 파일이 `claude-code/plugin/references/` 한 곳에 모여 있다는 점이 핵심이다.

확인 포인트:

- [ ] plugin 매니페스트와 marketplace 등록 파일의 역할을 구분할 수 있다.
- [ ] 플러그인 스킬이 왜 bilingual 정책을 직접 문서화하는지 이해했다.

참고 파일:

- `.claude-plugin/marketplace.json`
- `claude-code/plugin/.claude-plugin/plugin.json`
- `claude-code/plugin/skills/source-analyzer/SKILL.md`

## Step 4. 분석 세션과 publish 결과 추적하기

`.analysis/RESUME.md`, `.analysis/sessions/analyze-20260310-133920/state.json`, `.analysis/outputs/`, `.analysis/AI_CONTEXT.md`를 열어 본다. 그러면 작업 중 세션 상태와 공유 가능한 안정 산출물이 분리돼 있다는 점이 보인다.

확인 포인트:

- [ ] checkpoint 파일이 어떤 요약을 남기는지 이해했다.
- [ ] `state.json.frontier`, `visited`, `.analysis/outputs/`의 차이를 설명할 수 있다.

참고 파일:

- `.analysis/RESUME.md`
- `.analysis/sessions/analyze-20260310-133920/state.json`
- `.analysis/outputs/SUMMARY.json`
- `.analysis/AI_CONTEXT.md`

## Step 5. 설치와 테스트를 직접 실행하기

아래 명령을 실행해 공개 스킬 목록과 테스트 상태를 확인한다.

```bash
scripts/install_codex_skill.sh --list
python3 -m unittest discover -s tests
```

이 분석 세션에서는 첫 번째 명령이 공개 Codex 스킬 6개를 출력했고, 두 번째 명령은 48개 테스트를 통과했다.

확인 포인트:

- [ ] 설치 스크립트가 현재 어떤 스킬을 공개하는지 알 수 있다.
- [ ] 테스트가 구조 계약과 게시 도구까지 검증한다는 점을 이해했다.

참고 파일:

- `scripts/install_codex_skill.sh`
- `tests/test_skill_repository_contract.py`
- `tests/test_checkpoint_manager.py`
- `tests/test_publish_wiki.py`

## 자가검증 체크리스트

- [ ] `codex/skills/`와 `claude-code/plugin/`의 차이를 2문장 안에 설명할 수 있다.
- [ ] `source-analyzer`의 재개와 publish 흐름을 파일 경로 기준으로 추적할 수 있다.
- [ ] `scripts/install_codex_skill.sh --list`와 `python3 -m unittest discover -s tests`를 실행할 수 있다.
- [ ] `.analysis/AI_CONTEXT.md`가 왜 필요한지 설명할 수 있다.

## 확장 미션

1. `codex/skills/github-flow/SKILL.md`를 읽고 `plan -> implement -> review`가 어느 단계에 묶이는지 도식으로 그려본다.
2. `scripts/publish_wiki.sh --dry-run`을 실행해 분석 산출물이 위키로 어떻게 변환되는지 본다.
3. `.codex/skills/skill-generator/SKILL.md`를 읽고 새 Codex 스킬 골격을 직접 설계해 본다.
