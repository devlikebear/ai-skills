#!/usr/bin/env bash

set -euo pipefail

REPO_ROOT="$(pwd)"
ANALYSIS_DIR="${REPO_ROOT}/.analysis"

usage() {
  cat <<'EOF'
Usage:
  publish_wiki.sh [--project-dir <path>] [--session-id <id>] [--dry-run]

Publishes the latest (or specified) .analysis session outputs to the
GitHub wiki of the current repository.

Options:
  --project-dir <path>  Project root directory (default: current directory)
  --session-id <id>     Publish a specific session (default: latest)
  --dry-run             Prepare wiki pages locally without pushing

Requirements:
  - GitHub wiki must be enabled (create at least one page via GitHub UI first)
  - git push access to the wiki repository

Examples:
  publish_wiki.sh
  publish_wiki.sh --session-id analyze-20260308-120027
  publish_wiki.sh --dry-run
  publish_wiki.sh --project-dir /path/to/project
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

get_project_name() {
  local remote_url
  remote_url=$(git -C "${REPO_ROOT}" remote get-url origin 2>/dev/null || echo "")
  if [[ -n "${remote_url}" ]]; then
    remote_url="${remote_url%.git}"
    basename "${remote_url}"
  else
    basename "${REPO_ROOT}"
  fi
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

list_module_files() {
  local modules_dir="$1"
  if [[ ! -d "${modules_dir}" ]]; then
    return 0
  fi

  python3 - "$modules_dir" <<'PY'
from pathlib import Path
import sys

modules_dir = Path(sys.argv[1])
files = sorted(modules_dir.glob("*.md"), key=lambda p: p.stem)

for path in files:
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

# Strip common module prefixes
for prefix in ["모듈: ", "Module: "]:
    if title.startswith(prefix):
        title = title[len(prefix):]
        break

print(title)
PY
}

module_description_from_file() {
  python3 - "$1" <<'PY'
from pathlib import Path
import sys

lines = Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()
description = ""

# Try known section headers for role/description
role_headers = {"## 역할", "## Role", "## Description", "## Overview"}
for index, line in enumerate(lines):
    if line.strip() not in role_headers:
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

# Fallback: use first non-heading, non-empty line
if not description:
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and not stripped.startswith(">"):
            description = stripped
            break

if not description:
    description = "Module analysis document"

print(description)
PY
}

detect_page_titles() {
  local outputs_dir="$1"
  # Extract H1 titles from output files for sidebar/home display
  python3 - "$outputs_dir" <<'PY'
from pathlib import Path
import json, sys

outputs_dir = Path(sys.argv[1])
titles = {}

for md_file in sorted(outputs_dir.glob("*.md")):
    stem = md_file.stem
    title = stem.replace("-", " ").title()
    for line in md_file.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break
    titles[stem] = title

print(json.dumps(titles))
PY
}

build_sidebar() {
  local wiki_dir="$1"
  local modules_dir="$2"
  local page_titles="$3"
  {
    echo "### Analysis Results"
    echo ""
    echo "- [[Home]]"

    # Add ordered pages
    for key in overview architecture technologies glossary tutorial clone-coding implementation-checklist; do
      local prefix="${PAGE_ORDER[${key}]:-}"
      if [[ -f "${wiki_dir}/${prefix}-${key}.md" ]]; then
        local title
        title=$(python3 -c "import json,sys; d=json.loads(sys.argv[1]); print(d.get(sys.argv[2], sys.argv[2].replace('-',' ').title()))" "${page_titles}" "${key}")
        printf -- '- [[%s|%s-%s]]\n' "${title}" "${prefix}" "${key}"
      fi
    done

    echo ""
    echo "### Modules"

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
  local page_titles="$4"
  local project_name="$5"
  {
    cat <<EOF
# ${project_name} — Codebase Analysis

> Session: \`${session_id}\`
> Generated: $(date -u +%Y-%m-%d)

Auto-generated by \`source-analyzer\`.

## Documents

| Document | Description |
|----------|-------------|
EOF

    # Add ordered pages with descriptions from first paragraph
    for key in overview architecture technologies glossary tutorial clone-coding implementation-checklist; do
      local prefix="${PAGE_ORDER[${key}]:-}"
      if [[ -f "${wiki_dir}/${prefix}-${key}.md" ]]; then
        local title
        title=$(python3 -c "import json,sys; d=json.loads(sys.argv[1]); print(d.get(sys.argv[2], sys.argv[2].replace('-',' ').title()))" "${page_titles}" "${key}")
        local title_cell=${title//|/\\|}
        printf '| [[%s\\|%s-%s]] | %s |\n' \
          "${title_cell}" "${prefix}" "${key}" "${key//-/ }"
      fi
    done

    cat <<'EOF'

## Modules

| Module | Description |
|--------|-------------|
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
      --project-dir)
        REPO_ROOT="$(cd "$2" && pwd)"
        ANALYSIS_DIR="${REPO_ROOT}/.analysis"
        shift 2
        ;;
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
    # Fallback: try published outputs
    outputs_dir="${ANALYSIS_DIR}/outputs"
    if [[ ! -d "${outputs_dir}" ]]; then
      echo "error: no outputs directory found for session ${session_id}" >&2
      echo "hint: run a checkpoint with status 'paused' or 'completed' first" >&2
      exit 1
    fi
    echo "note: using published outputs from ${outputs_dir}"
  fi

  echo "session: ${session_id}"
  echo "outputs: ${outputs_dir}"

  local project_name
  project_name=$(get_project_name)

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

  # Detect page titles from output files
  local page_titles
  page_titles=$(detect_page_titles "${outputs_dir}")

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
  build_home "${wiki_dir}" "${session_id}" "${modules_dir}" "${page_titles}" "${project_name}"
  echo "  page: Home.md"
  build_sidebar "${wiki_dir}" "${modules_dir}" "${page_titles}"
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

Auto-generated by publish_wiki.sh
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
