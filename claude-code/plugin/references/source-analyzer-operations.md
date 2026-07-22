# Source Analyzer Operations

## Layout

Keep stable tracked results in `.analysis/outputs/`, transient work in `.analysis/sessions/<session-id>/`, and retrieval indexes in `.analysis/cache/source-analyzer-search/`. Track `.analysis/RESUME.md`, `.analysis/AI_CONTEXT.md`, and stable outputs; ignore sessions and cache.

## Commands

```bash
python3 "$CHECKPOINT_SCRIPT" init --mode analyze --scope "." --commit "$COMMIT"
python3 "$CHECKPOINT_SCRIPT" sync
python3 "$CHECKPOINT_SCRIPT" checkpoint --title "module analyzed" --status paused
python3 "$CHECKPOINT_SCRIPT" publish
python3 "$CHECKPOINT_SCRIPT" generate-summary
python3 "$CHECKPOINT_SCRIPT" generate-search-index
```

Paused and completed checkpoints automatically publish within `.analysis/`. Migrate older session-only results once with `python3 "$CHECKPOINT_SCRIPT" migrate --analysis-dir .analysis`.

## Resume

Start with `brief`, then run `sync`. Return changed committed files to the BFS frontier, update affected module documents, and checkpoint before ending. Use snippet search for focused recall.

## Structured outputs

Maintain relative dependencies in `dependency-graph.json`, module responsibilities and key files in `module-map.json`, and the generated project summary in `SUMMARY.json`.
