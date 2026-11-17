# ADR-007: Baseline and regression testing
- **Status:** Active
- **Date:** 2026-10-31
- **Scope:** `tests/**`, `scripts/**`, `Makefile`
- **Author:** human
- **Source:** Claude action-item list, id **AI-002**

## Context
Planned changes (schema validation, provenance fields, i18n) will alter frontmatter,
pipeline output, and page generation. Today regressions in URLs, record counts, and
GeoJSON features are caught only by manual browsing. The pytest suite covers script
helpers; there is no output-level baseline.

## Decision
Establish a build/test baseline before any model-data change:

1. Golden snapshots of pipeline output: number of `_photos/*.md`, GeoJSON feature
   counts per layer, and the set of generated permalinks/URLs.
2. A `make test` target that runs pytest plus the snapshot comparison.
3. Documented build+test procedure (`make build`, `make test`, `--check`) in the
   Makefile help or `01_STRUCTURE.md`.

## Resulting Specification
- A snapshot file (e.g. `tests/baseline.json`) records counts and URL sets; regenerated
  deliberately when output legitimately changes (`make update-baseline`).
- `make test` fails if current output diverges from the baseline without an intentional
  update.
- No change to data or pipeline behavior in this item — it only observes.

## Alternatives Considered
- Full end-to-end Jekyll build comparison: heavier; deferred until Docker build (Phase 4)
  exists.
- No baseline, rely on `--check`: insufficient — `--check` audits consistency, not
  regressions against a previous state.

## Consequences
- Positive: every later item (ADR-008..011) has an objective before/after signal.
- Negative: baseline must be consciously updated when output changes legitimately; risk
  of rubber-stamping updates.

## Verification
- [ ] `python -m pytest` → all pass, including new baseline test
- [ ] `make test` (or documented equivalent) → passes on an untouched tree
- [ ] Deliberately break one `raw_data/` entry in a scratch copy → `make test` fails

## Waiver
[None]
