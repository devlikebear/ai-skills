# Security Triage Checklist (Fallback)

Use this file when language-specific references from `security-best-practices` are unavailable.
Do not require external SAST tools by default.
Write findings in the active skill language by default.

## 1) Scope and Language Identification / 범위와 언어 식별

- Identify primary language and framework from:
  - file extensions (`.go`, `.py`, `.ts`, `.js`)
  - manifests (`go.mod`, `pyproject.toml`, `requirements*.txt`, `package.json`)
- Limit triage to files reached by current BFS scope plus direct neighbors.

## 2) High-Impact Security Checks / 고영향 보안 점검

### Input and Injection / 입력과 인젝션
- Unvalidated user input passed to SQL/OS command/template/runtime eval
- Dynamic query/command composition from raw request values

### AuthN/AuthZ / 인증과 인가
- Missing authorization checks on privileged handlers/services
- Trusting client-provided identity/role without server-side verification

### Secrets and Sensitive Data / 비밀정보와 민감데이터
- Hardcoded credentials/tokens/keys
- Logging secrets, PII, session tokens, or full request bodies containing secrets

### File/Path/Serialization / 파일 경로와 직렬화
- Unsafe file path joins without normalization
- Untrusted deserialization without allowlist/validation

### Crypto and Transport Defaults / 암호화와 전송 기본값
- Weak or custom crypto primitives
- Disabled certificate validation or insecure defaults in production paths

## 3) Severity Heuristic / 심각도 기준

- **높음**: 인증 우회, 임의 코드 실행, SQL/명령 주입, 민감정보 대량 노출
- **중간**: 권한검사 누락 가능성, 부분 데이터 노출, 취약 기본값
- **낮음**: 보안 로깅 부족, 방어적 검증 누락(직접 악용 난이도 높음)

## 4) `SEC-*` Work Order Requirements / `SEC-*` 작업 지시 필수 항목

For every `SEC-*` issue and WO, include:
- 취약 시나리오
- 악용 전제
- 완화 방향
- 테스트 기준 (정상/공격 입력, 회귀)

## 5) Output Convention / 출력 규칙

- Use issue codes like `SEC-001`, `SEC-002`.
- Include file path and line references whenever possible.
- Record unresolved items in checkpoint `DUP/SEC/TIDY Progress`.
