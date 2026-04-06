#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SOURCE_ROOT="${REPO_ROOT}/codex/skills"
TARGET_ROOT="${CODEX_HOME:-${HOME}/.codex}/skills"

validate_skill_name() {
  local skill_name="$1"
  if [[ ! "${skill_name}" =~ ^[a-z0-9][a-z0-9-]*$ ]]; then
    echo "error: invalid skill name '${skill_name}'" >&2
    exit 1
  fi
}

usage() {
  cat <<'EOF'
Usage:
  scripts/install_codex_skill.sh --list
  scripts/install_codex_skill.sh <skill-name> [--with-mcp]
  scripts/install_codex_skill.sh --all

Examples:
  scripts/install_codex_skill.sh source-analyzer
  scripts/install_codex_skill.sh source-analyzer --with-mcp
  CODEX_HOME="$HOME/.codex" scripts/install_codex_skill.sh --all
EOF
}

list_skills() {
  find "${SOURCE_ROOT}" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort
}

copy_skill() {
  local skill_name="$1"
  validate_skill_name "${skill_name}"
  local source_dir="${SOURCE_ROOT}/${skill_name}"
  local target_dir="${TARGET_ROOT}/${skill_name}"

  if [[ ! -d "${source_dir}" ]]; then
    echo "error: unknown skill '${skill_name}'" >&2
    exit 1
  fi
  if [[ ! -f "${source_dir}/SKILL.md" ]]; then
    echo "error: SKILL.md not found for '${skill_name}'" >&2
    exit 1
  fi

  mkdir -p "${TARGET_ROOT}"
  rm -rf "${target_dir}"
  mkdir -p "${target_dir}"
  if [[ -d "${source_dir}/shared" ]]; then
    cp -R "${source_dir}/shared" "${target_dir}/shared"
  fi
  if [[ -d "${source_dir}/agents" ]]; then
    mkdir -p "${target_dir}/agents"
    cp -R "${source_dir}/agents/." "${target_dir}/agents/"
  fi
  cp "${source_dir}/SKILL.md" "${target_dir}/SKILL.md"
  find "${target_dir}" -type d -name "__pycache__" -prune -exec rm -rf {} +

  echo "installed: ${skill_name}"
  echo "source: ${source_dir}"
  echo "target: ${target_dir}"
}

register_source_analyzer_mcp() {
  local target_dir="$1"
  local server_name="${CODEX_SOURCE_ANALYZER_MCP_NAME:-source-analyzer-search}"
  local server_path="${target_dir}/shared/mcp/source-analyzer-mcp/server.py"

  if [[ ! -f "${server_path}" ]]; then
    echo "error: MCP server entrypoint not found at '${server_path}'" >&2
    exit 1
  fi
  if ! command -v codex >/dev/null 2>&1; then
    echo "error: 'codex' command not found; cannot register MCP server" >&2
    exit 1
  fi

  codex mcp add "${server_name}" -- python3 "${server_path}"
  echo "registered_mcp: ${server_name}"
  echo "mcp_entrypoint: ${server_path}"
}

main() {
  local with_mcp=0
  local positional=()
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --with-mcp)
        with_mcp=1
        shift
        ;;
      *)
        positional+=("$1")
        shift
        ;;
    esac
  done

  case "${positional[0]:-}" in
    --list)
      if [[ ${#positional[@]} -ne 1 || ${with_mcp} -ne 0 ]]; then
        usage
        exit 1
      fi
      list_skills
      ;;
    --all)
      if [[ ${#positional[@]} -ne 1 || ${with_mcp} -ne 0 ]]; then
        usage
        exit 1
      fi
      while IFS= read -r skill_name; do
        copy_skill "${skill_name}"
      done < <(list_skills)
      ;;
    -h|--help)
      usage
      ;;
    *)
      if [[ ${#positional[@]} -ne 1 ]]; then
        usage
        exit 1
      fi
      local skill_name="${positional[0]}"
      copy_skill "${skill_name}"
      if [[ ${with_mcp} -eq 1 ]]; then
        if [[ "${skill_name}" != "source-analyzer" ]]; then
          echo "error: --with-mcp is only supported for source-analyzer" >&2
          exit 1
        fi
        register_source_analyzer_mcp "${TARGET_ROOT}/${skill_name}"
      fi
      ;;
  esac
}

main "$@"
