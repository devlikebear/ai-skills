# 모듈: release-docs (릴리스 문서)

버전 관리 및 릴리스 관련 파일 모음.

## 역할

프로젝트의 버전, 변경 이력, 라이선스를 관리합니다.

## 핵심 파일

| 파일 | 역할 |
|------|------|
| `VERSION.txt` | 단일 버전 소스 (현재: 0.11.0) |
| `CHANGELOG.md` | 전체 릴리스 히스토리 (0.1.0 ~ 0.11.0) |
| `LICENSE` | MIT 라이선스 |
| `CLAUDE.md` | 개발 가이드 (버전 범프 체크리스트, 커밋 규칙) |
| `.gitignore` | 분석 세션/cache 등 로컬 산출물 무시 규칙 |

## 버전 관리 규칙

- **PATCH** (0.x.Y): 버그 수정, 문구 변경
- **MINOR** (0.X.0): 새 기능, 새 출력, 새 CLI 명령
- **MAJOR** (X.0.0): 스킬 인터페이스/체크포인트 형식 호환성 변경

## 동기화 필수 파일 (5곳)

1. `VERSION.txt`
2. `.claude-plugin/marketplace.json` (version × 2)
3. `claude-code/plugin/.claude-plugin/plugin.json`
4. `plugins/source-analyzer-tools/.codex-plugin/plugin.json` (Codex 번들 변경 시)
5. `CHANGELOG.md`

## 커밋 규칙

- `feat:` → minor 범프
- `fix:` → patch 범프
- `chore:` → 버전 범프 커밋 자체 또는 docs-only
