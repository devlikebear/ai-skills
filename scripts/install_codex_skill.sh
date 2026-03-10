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
  scripts/install_codex_skill.sh <skill-name>
  scripts/install_codex_skill.sh --all

Examples:
  scripts/install_codex_skill.sh source-analyzer
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

main() {
  case "${1:-}" in
    --list)
      if [[ $# -ne 1 ]]; then
        usage
        exit 1
      fi
      list_skills
      ;;
    --all)
      if [[ $# -ne 1 ]]; then
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
      if [[ $# -ne 1 ]]; then
        usage
        exit 1
      fi
      copy_skill "$1"
      ;;
  esac
}

main "$@"
