#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
ANALYSIS_DIR="${REPO_ROOT}/.analysis"

usage() {
  cat <<'EOF'
Usage:
  scripts/publish_wiki.sh [--session-id <id>] [--dry-run]

Publishes the latest (or specified) .analysis session outputs to the
GitHub wiki of the current repository.

Options:
  --session-id <id>   Publish a specific session (default: latest)
  --dry-run           Prepare wiki pages locally without pushing

Requirements:
  - GitHub wiki must be enabled (create at least one page via GitHub UI first)
  - git push access to the wiki repository

Examples:
  scripts/publish_wiki.sh
  scripts/publish_wiki.sh --session-id analyze-20260308-120027
  scripts/publish_wiki.sh --dry-run
EOF
}

find_latest_session() {
  local sessions_dir="${ANALYSIS_DIR}/sessions"
  if [[ ! -d "${sessions_dir}" ]]; then
    echo "error: no .analysis/sessions directory found" >&2
    exit 1
  fi

  local latest=""
  local latest_time=""
  for state_file in "${sessions_dir}"/*/state.json; do
    [[ -f "${state_file}" ]] || continue
    local updated_at
    updated_at=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['updated_at'])" "${state_file}" 2>/dev/null || echo "")
    if [[ -n "${updated_at}" ]] && [[ "${updated_at}" > "${latest_time}" ]]; then
      latest_time="${updated_at}"
      latest=$(basename "$(dirname "${state_file}")")
    fi
  done

  if [[ -z "${latest}" ]]; then
    echo "error: no analysis session found" >&2
    exit 1
  fi
  echo "${latest}"
}

get_remote_url() {
  local remote_url
  remote_url=$(git -C "${REPO_ROOT}" remote get-url origin 2>/dev/null || echo "")
  if [[ -z "${remote_url}" ]]; then
    echo "error: no git remote 'origin' found" >&2
    exit 1
  fi

  # Convert to wiki URL
  # https://github.com/owner/repo.git -> https://github.com/owner/repo.wiki.git
  # https://github.com/owner/repo     -> https://github.com/owner/repo.wiki.git
  # git@github.com:owner/repo.git     -> git@github.com:owner/repo.wiki.git
  remote_url="${remote_url%.git}"
  echo "${remote_url}.wiki.git"
}

# Wiki page ordering prefix
declare -A PAGE_ORDER=(
  ["overview"]=01
  ["architecture"]=02
  ["technologies"]=03
  ["glossary"]=04
  ["tutorial"]=05
  ["clone-coding"]=06
  ["implementation-checklist"]=07
)

MODULE_ORDER=(
  "source-analyzer"
  "plan"
  "implement"
  "review"
  "refactor"
  "github-flow"
  "plugin"
  "scripts"
  "tests"
  "skill-generator"
)

list_module_files() {
  local modules_dir="$1"
  if [[ ! -d "${modules_dir}" ]]; then
    return 0
  fi

  python3 - "$modules_dir" "${MODULE_ORDER[@]}" <<'PY'
from pathlib import Path
import sys

modules_dir = Path(sys.argv[1])
order = sys.argv[2:]
rank = {name: index for index, name in enumerate(order)}
files = sorted(modules_dir.glob("*.md"))

def sort_key(path):
    stem = path.stem
    if stem in rank:
        return (0, rank[stem], stem)
    return (1, stem, stem)

for path in sorted(files, key=sort_key):
    print(path)
PY
}

module_name_from_file() {
  basename "$1" .md
}

module_title_from_file() {
  python3 - "$1" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
title = path.stem
for line in path.read_text(encoding="utf-8").splitlines():
    if line.startswith("# "):
        title = line[2:].strip()
        break

prefix = "모듈: "
if title.startswith(prefix):
    title = title[len(prefix):]

print(title)
PY
}

module_description_from_file() {
  python3 - "$1" <<'PY'
from pathlib import Path
import sys

lines = Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()
description = "모듈 분석 문서"

for index, line in enumerate(lines):
    if line.strip() != "## 역할":
        continue

    paragraph = []
    cursor = index + 1
    while cursor < len(lines) and not lines[cursor].strip():
        cursor += 1
    while cursor < len(lines):
        current = lines[cursor].strip()
        if not current or current.startswith("#"):
            break
        paragraph.append(current)
        cursor += 1
    if paragraph:
        description = " ".join(paragraph)
    break

print(description)
PY
}

build_sidebar() {
  local wiki_dir="$1"
  local modules_dir="$2"
  {
    cat <<'SIDEBAR'
### 📖 분석 결과

- [[Home]]
- [[01 프로젝트 개요|01-overview]]
- [[02 아키텍처|02-architecture]]
- [[03 사용 기술|03-technologies]]
- [[04 용어 사전|04-glossary]]
- [[05 튜토리얼|05-tutorial]]
- [[06 클론 코딩 가이드|06-clone-coding]]
- [[07 구현 체크리스트|07-implementation-checklist]]

### 📦 모듈 분석
SIDEBAR

    local module_file=""
    local module_name=""
    local module_title=""
    while IFS= read -r module_file; do
      [[ -n "${module_file}" ]] || continue
      module_name=$(module_name_from_file "${module_file}")
      module_title=$(module_title_from_file "${module_file}")
      printf -- '- [[%s|module-%s]]\n' "${module_title}" "${module_name}"
    done < <(list_module_files "${modules_dir}")
  } > "${wiki_dir}/_Sidebar.md"
}

build_home() {
  local wiki_dir="$1"
  local session_id="$2"
  local modules_dir="$3"
  {
    cat <<EOF
# AI Skills 코드베이스 분석

> 세션: \`${session_id}\`
> 생성일: $(date -u +%Y-%m-%d)

이 위키는 \`/code-workflow:source-analyzer\`로 자동 생성된 코드베이스 분석 결과입니다.

## 문서 목록

| 문서 | 설명 |
|------|------|
| [[01 프로젝트 개요\|01-overview]] | 프로젝트 목적, 핵심 가치, 버전 |
| [[02 아키텍처\|02-architecture]] | 3-계층 배포 모델, 데이터 흐름 |
| [[03 사용 기술\|03-technologies]] | Bash, Python, Markdown, YAML, JSON |
| [[04 용어 사전\|04-glossary]] | 핵심 용어 20개 |
| [[05 튜토리얼\|05-tutorial]] | 6단계 입문 가이드 |
| [[06 클론 코딩\|06-clone-coding]] | 처음부터 구축하는 가이드 |
| [[07 구현 체크리스트\|07-implementation-checklist]] | 7 Phase 체크리스트 |

## 모듈 분석

| 모듈 | 설명 |
|------|------|
EOF

    local module_file=""
    local module_name=""
    local module_title=""
    local module_description=""
    local module_title_cell=""
    local module_description_cell=""
    while IFS= read -r module_file; do
      [[ -n "${module_file}" ]] || continue
      module_name=$(module_name_from_file "${module_file}")
      module_title=$(module_title_from_file "${module_file}")
      module_description=$(module_description_from_file "${module_file}")
      module_title_cell=${module_title//|/\\|}
      module_description_cell=${module_description//|/\\|}
      printf '| [[%s\\|module-%s]] | %s |\n' \
        "${module_title_cell}" \
        "${module_name}" \
        "${module_description_cell}"
    done < <(list_module_files "${modules_dir}")
  } > "${wiki_dir}/Home.md"
}

main() {
  local session_id=""
  local dry_run=false

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --session-id)
        session_id="$2"
        shift 2
        ;;
      --dry-run)
        dry_run=true
        shift
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        echo "error: unknown option '$1'" >&2
        usage
        exit 1
        ;;
    esac
  done

  if [[ -z "${session_id}" ]]; then
    session_id=$(find_latest_session)
  fi

  local outputs_dir="${ANALYSIS_DIR}/sessions/${session_id}/outputs"
  if [[ ! -d "${outputs_dir}" ]]; then
    echo "error: outputs directory not found: ${outputs_dir}" >&2
    exit 1
  fi

  echo "session: ${session_id}"
  echo "outputs: ${outputs_dir}"

  local wiki_url
  wiki_url=$(get_remote_url)
  echo "wiki repo: ${wiki_url}"

  local work_dir
  work_dir=$(mktemp -d)
  trap '[[ -n "${work_dir:-}" ]] && rm -rf "${work_dir}"' EXIT

  echo ""
  echo "cloning wiki repository..."
  if ! git clone "${wiki_url}" "${work_dir}/wiki" 2>/dev/null; then
    echo "error: failed to clone wiki repo." >&2
    echo "hint: enable the wiki on GitHub first (Settings > Features > Wikis)" >&2
    echo "hint: create at least one page via the GitHub UI to initialize the wiki repo" >&2
    exit 1
  fi

  local wiki_dir="${work_dir}/wiki"

  # Copy top-level outputs with ordering prefix
  for md_file in "${outputs_dir}"/*.md; do
    [[ -f "${md_file}" ]] || continue
    local basename
    basename=$(basename "${md_file}" .md)
    local prefix="${PAGE_ORDER[${basename}]:-}"
    if [[ -n "${prefix}" ]]; then
      cp "${md_file}" "${wiki_dir}/${prefix}-${basename}.md"
      echo "  page: ${prefix}-${basename}.md"
    fi
  done

  # Copy module outputs with module- prefix
  local modules_dir="${outputs_dir}/modules"
  if [[ -d "${modules_dir}" ]]; then
    for md_file in "${modules_dir}"/*.md; do
      [[ -f "${md_file}" ]] || continue
      local basename
      basename=$(basename "${md_file}" .md)
      cp "${md_file}" "${wiki_dir}/module-${basename}.md"
      echo "  page: module-${basename}.md"
    done
  fi

  # Build Home and Sidebar
  build_home "${wiki_dir}" "${session_id}" "${modules_dir}"
  echo "  page: Home.md"
  build_sidebar "${wiki_dir}" "${modules_dir}"
  echo "  page: _Sidebar.md"

  if [[ "${dry_run}" == true ]]; then
    echo ""
    echo "dry-run: wiki pages prepared at ${wiki_dir}"
    echo "files:"
    ls -1 "${wiki_dir}"/*.md
    # Keep work_dir alive for inspection
    trap - EXIT
    echo ""
    echo "inspect at: ${wiki_dir}"
    return 0
  fi

  # Commit and push
  cd "${wiki_dir}"
  trap 'cd "${REPO_ROOT}" && [[ -n "${work_dir:-}" ]] && rm -rf "${work_dir}"' EXIT
  git add -A
  if git diff --cached --quiet; then
    echo ""
    echo "no changes to publish"
    return 0
  fi

  git commit -m "$(cat <<EOF
docs: publish source-analyzer results (${session_id})

Auto-generated by scripts/publish_wiki.sh
EOF
  )"

  echo ""
  echo "pushing to wiki..."
  git push origin master 2>/dev/null || git push origin main

  echo ""
  echo "done! wiki published successfully."
  local repo_url
  repo_url=$(git -C "${REPO_ROOT}" remote get-url origin)
  repo_url="${repo_url%.git}"
  echo "view at: ${repo_url}/wiki"
}

main "$@"
