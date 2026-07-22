# Source Analyzer Operations

## Directory layout

`.analysis/outputs/` contains stable, tracked results. `.analysis/sessions/<session-id>/` contains transient checkpoints and work-in-progress outputs. `.analysis/cache/source-analyzer-search/` contains the generated retrieval index. Track `.analysis/RESUME.md`, `.analysis/AI_CONTEXT.md`, and stable outputs; ignore `.analysis/sessions/` and `.analysis/cache/`.

## Session commands

```bash
python3 "$CHECKPOINT_SCRIPT" init --mode analyze --scope "." --commit "$COMMIT"
python3 "$CHECKPOINT_SCRIPT" sync
python3 "$CHECKPOINT_SCRIPT" checkpoint --title "module analyzed" --status paused
python3 "$CHECKPOINT_SCRIPT" publish
python3 "$CHECKPOINT_SCRIPT" generate-summary
python3 "$CHECKPOINT_SCRIPT" generate-search-index
```

Paused and completed checkpoints automatically copy work-in-progress outputs to `.analysis/outputs/`. For older repositories whose outputs exist only under a session, run `python3 "$CHECKPOINT_SCRIPT" migrate --analysis-dir .analysis` once.

## Resume and incremental analysis

Start with `brief`, then run `sync`. Changed committed files return to the BFS frontier. Mark affected module documents as pending re-analysis, remove the notice after revisiting them, and checkpoint before ending. Use snippet search to recall focused topics instead of re-reading all generated documentation.

## Structured outputs

- `dependency-graph.json`: relative file-to-import arrays.
- `module-map.json`: module path, responsibility, and key files.
- `SUMMARY.json`: generated project summary, modules, and known issues.

The search index is refreshed during stable output publication and may be rebuilt manually.
