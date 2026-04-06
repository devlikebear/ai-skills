# Source Analyzer Tools

Codex plugin bundle that exposes the `source-analyzer-search` MCP server.

Recommended path for day-to-day use is still:

```bash
scripts/install_codex_skill.sh source-analyzer --with-mcp
codex mcp list
```

If registration worked, `codex mcp list` should include `source-analyzer-search`.

Typical runtime flow:

```bash
python3 ~/.codex/skills/source-analyzer/shared/scripts/checkpoint_manager.py generate-search-index
```

Then ask Codex to use:

- `analysis.search`
- `analysis.get_module`
- `analysis.trace_dependencies`

This plugin bundle exists so the repository can also publish a Codex plugin/marketplace artifact for the same MCP server.
The bundle source is declared in `.agents/plugins/marketplace.json`.
