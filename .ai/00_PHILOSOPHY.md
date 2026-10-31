# Design Philosophy
Guidance, not rules. These evolve as the project matures.

## Core Principles
- High-integrity research database: every public photo page traces back to one curated master entry in `raw_data/` (frontmatter + primary image + variants)
- One-way pipeline: humans curate sources; code generates everything downstream (`raw_data/` → `_photos/` → `_site/`)
- Single source of truth: configuration (CDN URLs, collection paths, permalinks) lives in `_config.yml`, never scattered in layouts
- No silent failures: log every error to console with graceful fallbacks; a missing asset degrades, it never vanishes quietly

## Architectural Style
- Explicit over implicit: the Parent-Variant pattern makes "same object, multiple views" a data structure, not a convention
- Static-first: state in URLs (`?param=value`), localStorage for session, client-side only
- Boring build chain: Jekyll + Python + Docker/Nginx; no build pipeline beyond the two

## What We Optimise For
- Correctness of the historical record (locations, dates, provenance of scans)
- Reproducibility: a fresh `make build` regenerates the whole site from `raw_data/`
- Geospatial fidelity: coordinates and FOV data flow QGIS/CSV → GeoJSON → Leaflet without manual re-entry

## What We Accept as Trade-offs
- Fully regenerating `_photos/` on each build instead of incremental updates (except `changed` mode) to keep the pipeline simple
- CDN dependence (pinned, SRI-checked) instead of vendoring libraries

_Last updated: 2026-10-31 @ 0c053d5_
