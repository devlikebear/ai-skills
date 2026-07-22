#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SOURCE_SKILLS="${REPO_ROOT}/codex/skills"
PLUGIN_ROOT="${REPO_ROOT}/plugins/code-workflow"
TARGET_SKILLS="${PLUGIN_ROOT}/skills"

if [[ ! -f "${PLUGIN_ROOT}/.codex-plugin/plugin.json" ]]; then
  echo "error: code-workflow plugin manifest not found" >&2
  exit 1
fi

if [[ "${TARGET_SKILLS}" != "${REPO_ROOT}/plugins/code-workflow/skills" ]]; then
  echo "error: unexpected target path: ${TARGET_SKILLS}" >&2
  exit 1
fi

rm -rf "${TARGET_SKILLS}"
mkdir -p "${TARGET_SKILLS}"
cp -R "${SOURCE_SKILLS}/." "${TARGET_SKILLS}/"

ANALYZER_SKILL="${TARGET_SKILLS}/source-analyzer/SKILL.md"
perl -0pi -e 's#\$\{CODEX_HOME:-\$HOME/\.codex\}/skills/source-analyzer#\$\{PLUGIN_ROOT\}/skills/source-analyzer#g' "${ANALYZER_SKILL}"

echo "synced: codex/skills -> plugins/code-workflow/skills"
