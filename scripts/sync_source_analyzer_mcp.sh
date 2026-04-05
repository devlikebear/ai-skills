#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
CANONICAL_ROOT="${REPO_ROOT}/servers/source-analyzer-mcp"

copy_file() {
  local source_path="$1"
  local target_path="$2"
  mkdir -p "$(dirname "${target_path}")"
  cp "${source_path}" "${target_path}"
  echo "synced: ${target_path#${REPO_ROOT}/}"
}

copy_file "${CANONICAL_ROOT}/source_analyzer_search.py" "${REPO_ROOT}/codex/skills/source-analyzer/shared/scripts/source_analyzer_search.py"
copy_file "${CANONICAL_ROOT}/source_analyzer_search.py" "${REPO_ROOT}/claude-code/plugin/scripts/source_analyzer_search.py"
copy_file "${CANONICAL_ROOT}/source_analyzer_search.py" "${REPO_ROOT}/codex/skills/source-analyzer/shared/mcp/source-analyzer-mcp/source_analyzer_search.py"
copy_file "${CANONICAL_ROOT}/source_analyzer_search.py" "${REPO_ROOT}/claude-code/plugin/servers/source-analyzer-mcp/source_analyzer_search.py"
copy_file "${CANONICAL_ROOT}/source_analyzer_search.py" "${REPO_ROOT}/plugins/source-analyzer-tools/servers/source-analyzer-mcp/source_analyzer_search.py"
copy_file "${CANONICAL_ROOT}/server.py" "${REPO_ROOT}/codex/skills/source-analyzer/shared/mcp/source-analyzer-mcp/server.py"
copy_file "${CANONICAL_ROOT}/server.py" "${REPO_ROOT}/claude-code/plugin/servers/source-analyzer-mcp/server.py"
copy_file "${CANONICAL_ROOT}/server.py" "${REPO_ROOT}/plugins/source-analyzer-tools/servers/source-analyzer-mcp/server.py"
