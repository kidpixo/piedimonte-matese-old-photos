# ADR-005: Hybrid topic GeoJSON (build-time + runtime fallback)
- **Status:** Active
- **Date:** 2026-03-18
- **Scope:** `scripts/**`, `assets/data/**`, `_layouts/**`
- **Author:** human (mined from `.ai/PROJECT_MAP.md` + `.ai/IMPLEMENTATION_STEPS.md` during Lean SDD v2 migration — confirm)

## Context
Topic pages need map layers filtered to their featured photos. Generating per-topic GeoJSON
at runtime for every visitor is wasteful; generating nothing forced heavy client-side
filtering of the global points file.

## Decision
Hybrid approach: `scripts/process_research.py` generates per-topic GeoJSON at build time
into `assets/maps_data/topics/{slug}/` (origin, fov, lov layers), and the map layout falls
back to runtime filtering of the global GeoJSON when the generated per-topic file is absent.

## Resulting Specification
- Build-time: topic GeoJSON generated from topic `featured_photos` + photo locations into
  `assets/maps_data/topics/{slug}/{origin,fov,lov}.geojson`.
- Validation layer: the pipeline raises `ValueError` when `featured_photos` references a
  non-existent photo slug — mismatches fail the build, never the browser.
- Runtime: missing per-topic data falls back to client-side filtering of the global
  GeoJSON via `window.topicFeaturedPhotos` — never a broken map; the fallback path is
  logged (`console.info`/`console.warn`), not silent.
- No-op safe when a topic has no `featured_photos` (does not render the full dataset).
- `generate_topic_geojson` is covered by pytest (`tests/`).

## Alternatives Considered
- Pure runtime filtering: rejected — repeated client work on every visit, slower topics.
- Pure build-time with no fallback: rejected — new/edited topics break the map until the
  next pipeline run.

## Consequences
- Positive: fast topic maps by default; resilient when data is missing.
- Negative: two code paths to keep consistent; pipeline and layout must agree on the
  `assets/maps_data/topics/{slug}/` contract.

## Verification
- [ ] `python -m pytest` → all tests pass (includes `generate_topic_geojson` module)
- [ ] `python3 scripts/process_research.py --check` → topic GeoJSON audit reports no errors

## Waiver
[None]
