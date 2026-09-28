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

PUBLISH_SKILL="${TARGET_SKILLS}/publish-analysis-wiki/SKILL.md"
perl -0pi -e 's#\$\{CODEX_HOME:-\$HOME/\.codex\}/skills/publish-analysis-wiki#\$\{PLUGIN_ROOT\}/skills/publish-analysis-wiki#g' "${PUBLISH_SKILL}"

echo "synced: codex/skills -> plugins/code-workflow/skills"

# Generate the Claude Code copy of app-service-planning from the canonical skill.
PLANNING_SOURCE="${SOURCE_SKILLS}/app-service-planning"
CLAUDE_PLUGIN_ROOT="${REPO_ROOT}/claude-code/plugin"
PLANNING_REFS="${CLAUDE_PLUGIN_ROOT}/references/app-service-planning"
PLANNING_SKILL_DIR="${CLAUDE_PLUGIN_ROOT}/skills/app-service-planning"

rm -rf "${PLANNING_REFS}"
mkdir -p "${PLANNING_REFS}" "${PLANNING_SKILL_DIR}"
cp -R "${PLANNING_SOURCE}/shared/." "${PLANNING_REFS}/"
perl -pe 's#shared/#../../references/app-service-planning/#g' \
  "${PLANNING_SOURCE}/SKILL.md" > "${PLANNING_SKILL_DIR}/SKILL.md"

echo "synced: codex/skills/app-service-planning -> claude-code/plugin"
