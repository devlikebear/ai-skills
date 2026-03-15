# 모듈: 릴리스/온보딩 문서

## 역할

저장소의 버전, 설치 경로, 운영 규칙, 라이선스, 마켓플레이스 진입점을 사람과 AI 모두가 빠르게 찾을 수 있게 정리한다.

## 핵심 경로

- `README.md`
- `CLAUDE.md`
- `CHANGELOG.md`
- `VERSION.txt`
- `LICENSE`
- `.claude-plugin/marketplace.json`

## 구조적 특징

1. 실제 버전 진실 공급원은 `VERSION.txt`와 두 JSON 매니페스트다.
2. `CHANGELOG.md`는 릴리스별 기능 추가와 구조 변경 배경을 설명한다.
3. `CLAUDE.md`는 개발 시 반드시 지켜야 할 버전 동기화와 배포 동기화 규칙을 적는다.
4. `.claude-plugin/marketplace.json`은 이 저장소를 Claude Code 플러그인 마켓플레이스로 노출한다.

## 입문자가 먼저 볼 파일

1. `VERSION.txt`
2. `CHANGELOG.md`
3. `README.md`
4. `CLAUDE.md`
