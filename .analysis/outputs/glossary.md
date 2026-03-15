# 용어 사전

| 용어 | 설명 |
|------|------|
| 스킬 | AI 에이전트가 읽는 작업 절차 정의다. 보통 `SKILL.md`로 표현된다. |
| `SKILL.md` | YAML frontmatter와 Markdown 워크플로우 본문을 함께 가진 핵심 파일이다. |
| Flat skill layout | Codex 스킬이 단일 `SKILL.md`, `agents/`, `shared/`만 갖는 현재 구조를 말한다. |
| `agents/openai.yaml` | Codex에서 스킬 이름, 설명, 기본 프롬프트를 노출하는 메타데이터다. |
| Bilingual policy | Claude Code 플러그인 스킬이 사용자 언어를 감지해 같은 언어로 응답하는 규칙이다. |
| Marketplace | Claude Code가 플러그인을 찾는 저장소 목록이다. 이 저장소는 `.claude-plugin/marketplace.json`으로 등록된다. |
| Plugin manifest | `claude-code/plugin/.claude-plugin/plugin.json` 파일이다. 플러그인 이름, 버전, 설명을 담는다. |
| Work order | 구현 또는 리팩터링 작업을 작게 나눈 실행 문서다. |
| Contract test | 파일 구조와 릴리스 규칙을 깨지 않았는지 검사하는 테스트다. |
| Checkpoint | `source-analyzer`가 청크별 진행 상황을 남기는 기록 단위다. |
| Session | 한 번의 분석 실행 전체를 말한다. `.analysis/sessions/<session-id>/`에 저장된다. |
| `state.json` | 세션의 현재 상태, frontier, visited, outputs, checkpoints를 저장하는 파일이다. |
| Frontier | 아직 분석하지 않았지만 다음에 볼 후보 파일 목록이다. |
| Visited | 이미 분석했다고 기록된 파일 목록이다. |
| `RESUME.md` | 가장 최근 재개 포인터를 가리키는 파일이다. |
| `sync` | 저장된 커밋과 현재 HEAD를 비교해 frontier를 갱신하는 하위 명령이다. |
| `publish` | 세션 산출물을 `.analysis/outputs/`로 복사해 Git 추적 가능한 안정 결과로 만드는 하위 명령이다. |
| `migrate` | 구형 `.analysis/sessions/<id>/outputs/` 레이아웃을 새 `.analysis/outputs/` 구조로 복사하는 하위 명령이다. |
| `SUMMARY.json` | 세션의 모듈 목록과 출력 파일 요약을 담는 AI용 JSON이다. |
| `dependency-graph.json` | 파일 단위의 내부 참조 관계를 간단히 정리한 JSON이다. |
| `module-map.json` | 논리 모듈 이름과 책임, 핵심 파일을 매핑한 JSON이다. |
| `issue-candidates.md` | 분석 결과에서 추출한 `DUP/SEC/TIDY` 후보 목록이다. |
| `AI_CONTEXT.md` | 다른 AI 에이전트가 먼저 읽도록 만든 분석 진입점 문서다. |
| `git ls-tree -r HEAD` | 커밋된 파일만 열거해 미커밋 변경을 분석에서 제외하는 Git 명령 패턴이다. |
| `CLAUDE_PLUGIN_ROOT` | Claude Code 플러그인 내부에서 스크립트와 참조 파일의 기준 경로로 쓰는 변수다. |
| `CODEX_HOME` | Codex 스킬 설치 대상 루트를 가리키는 환경 변수다. |
| `github-flow` | 브랜치부터 릴리스까지 전체 절차를 묶은 운영 스킬이다. |
| skill-generator | 이 저장소 규칙에 맞는 새 Codex 스킬 생성을 돕는 로컬 래퍼 스킬이다. |
