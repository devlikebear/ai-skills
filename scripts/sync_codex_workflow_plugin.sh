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

# Generate Claude Code copies of skills whose Codex source is canonical.
# Each skill's shared/ resources move to claude-code/plugin/references/<skill>/
# and SKILL.md links are rewritten from shared/ to ../../references/<skill>/.
CLAUDE_PLUGIN_ROOT="${REPO_ROOT}/claude-code/plugin"
GENERATED_CLAUDE_SKILLS=(
  app-service-planning
  verify-own-work
  correction-ladder
  garden-antipatterns
)

for skill_name in "${GENERATED_CLAUDE_SKILLS[@]}"; do
  skill_source="${SOURCE_SKILLS}/${skill_name}"
  skill_refs="${CLAUDE_PLUGIN_ROOT}/references/${skill_name}"
  skill_dir="${CLAUDE_PLUGIN_ROOT}/skills/${skill_name}"

  rm -rf "${skill_refs}"
  mkdir -p "${skill_refs}" "${skill_dir}"
  cp -R "${skill_source}/shared/." "${skill_refs}/"
  perl -pe "s#shared/#../../references/${skill_name}/#g" \
    "${skill_source}/SKILL.md" > "${skill_dir}/SKILL.md"

  echo "synced: codex/skills/${skill_name} -> claude-code/plugin"
done
