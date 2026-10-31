# ADR-002: One-way generated pipeline
- **Status:** Active
- **Date:** 2026-02-15
- **Scope:** `raw_data/**`, `_photos/**`, `assets/**`, `scripts/**`
- **Author:** human (mined from `.ai/PROJECT_MAP.md` during Lean SDD v2 migration — confirm)

## Context
Research content was originally edited directly in the Jekyll collection, making it unclear
which files were source and which were generated, and losing curation work on regeneration.

## Decision
Strict one-way pipeline: humans edit only `raw_data/`; `scripts/process_research.py`
generates `_photos/`, optimized images, thumbnails, and GeoJSON; Jekyll builds `_site/`.

## Resulting Specification
- Never hand-edit `_photos/*.md` or generated files under `assets/` — they are regenerated.
- All curation changes flow through `raw_data/` + a pipeline run.
- Incremental mode: `python3 scripts/process_research.py changed [--prune]` may be used;
  `--prune` removes stale `_photos/` entries for deleted sources.

## Alternatives Considered
- Two-way editing (hand-tweak generated output): rejected — changes are silently destroyed
  on the next pipeline run.

## Consequences
- Positive: regeneration is always safe; provenance of every public page is a single source
  entry.
- Negative: quick display fixes must be made in the pipeline or templates, not in the
  generated collection.

## Verification
- [ ] `python3 scripts/process_research.py --check` → no errors
- [ ] `python3 scripts/process_research.py --check --json` → valid JSON, `"errors"` empty
- [ ] `python -m pytest` → all tests pass

## Waiver
[None]
