#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SOURCE_ROOT="${REPO_ROOT}/claude-code/skills"
TARGET_ROOT="${CLAUDE_HOME:-${HOME}/.claude}/skills"

validate_skill_name() {
  local skill_name="$1"
  if [[ ! "${skill_name}" =~ ^[a-z0-9][a-z0-9-]*$ ]]; then
    echo "error: invalid skill name '${skill_name}'" >&2
    exit 1
  fi
}

validate_language() {
  local language="$1"
  if [[ ! "${language}" =~ ^(ko|en)$ ]]; then
    echo "error: invalid language '${language}'" >&2
    exit 1
  fi
}

usage() {
  cat <<'EOF'
Usage:
  scripts/install_claude_code_skill.sh --list
  scripts/install_claude_code_skill.sh --list-languages <skill-name>
  scripts/install_claude_code_skill.sh <skill-name> <language>
  scripts/install_claude_code_skill.sh --all <language>

Examples:
  scripts/install_claude_code_skill.sh source-analyzer ko
  scripts/install_claude_code_skill.sh source-analyzer en
  CLAUDE_HOME="$HOME/.claude" scripts/install_claude_code_skill.sh --all en
EOF
}

list_skills() {
  find "${SOURCE_ROOT}" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort
}

list_languages() {
  local skill_name="$1"
  validate_skill_name "${skill_name}"
  local source_dir="${SOURCE_ROOT}/${skill_name}"
  if [[ ! -d "${source_dir}" ]]; then
    echo "error: unknown skill '${skill_name}'" >&2
    exit 1
  fi
  find "${source_dir}" -mindepth 1 -maxdepth 1 -type d \( -name ko -o -name en \) -exec basename {} \; | sort
}

copy_skill() {
  local skill_name="$1"
  local language="$2"
  validate_skill_name "${skill_name}"
  validate_language "${language}"
  local source_dir="${SOURCE_ROOT}/${skill_name}"
  local target_dir="${TARGET_ROOT}/${skill_name}"
  local language_dir="${source_dir}/${language}"

  if [[ ! -d "${source_dir}" ]]; then
    echo "error: unknown skill '${skill_name}'" >&2
    exit 1
  fi
  if [[ ! -f "${language_dir}/SKILL.md" ]]; then
    echo "error: language '${language}' is not available for '${skill_name}'" >&2
    exit 1
  fi

  mkdir -p "${TARGET_ROOT}"
  rm -rf "${target_dir}"
  mkdir -p "${target_dir}"
  if [[ -f "${source_dir}/README.md" ]]; then
    cp "${source_dir}/README.md" "${target_dir}/README.md"
  fi
  if [[ -d "${source_dir}/shared" ]]; then
    cp -R "${source_dir}/shared" "${target_dir}/shared"
  fi
  cp "${language_dir}/SKILL.md" "${target_dir}/SKILL.md"
  find "${target_dir}" -type d -name "__pycache__" -prune -exec rm -rf {} +

  echo "installed: ${skill_name}"
  echo "language: ${language}"
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
    --list-languages)
      if [[ $# -ne 2 ]]; then
        usage
        exit 1
      fi
      list_languages "$2"
      ;;
    --all)
      if [[ $# -ne 2 ]]; then
        usage
        exit 1
      fi
      while IFS= read -r skill_name; do
        copy_skill "${skill_name}" "$2"
      done < <(list_skills)
      ;;
    -h|--help)
      usage
      ;;
    *)
      if [[ $# -ne 2 ]]; then
        usage
        exit 1
      fi
      copy_skill "$1" "$2"
      ;;
  esac
}

main "$@"
