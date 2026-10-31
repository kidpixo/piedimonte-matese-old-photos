# Lanyon Research Database

Cotonificio Piedmonte research archive: a Lanyon-based Jekyll site being refactored into a
high-integrity research database. A Python pipeline (`scripts/process_research.py`) turns
curated master entries in `raw_data/` (YAML frontmatter + primary image + variants) into the
generated `_photos/` collection, optimized images/thumbnails, and GeoJSON for Leaflet maps;
editorial essays live in `_topics/`. Deployed as a static build via Docker (Python → Jekyll →
Nginx) or GitHub Pages.

## Files at a glance

- `raw_data/` — the only hand-curated layer; everything else is generated or editorial
- `scripts/process_research.py` — the pipeline (modes: `all`, `geo`, `changed [--prune]`, `--check [--json|--strict-warnings|--clean]`)
- `_photos/` — generated Jekyll collection (never hand-edit)
- `_topics/` — manual essays joined to photos via `featured_photos`
- `assets/` — optimized images, 150×150 thumbs, `assets/data/*.geojson`, JS/CSS
- `archive/` — private source material, never deployed
- `Makefile` / `Dockerfile` — build and deploy

This file is for humans. Agents: start at `03_CURRENT_STATUS.md` per `AGENTS.md`.

---

## Historical seed note (original refactor prompt, 2026-02)

The original refactor briefing that started this pipeline is archived at
[archive/2026-02-refactor-brief.md](archive/2026-02-refactor-brief.md). It predates the
current layout (`site_source/_photos/` mentioned there is now `_photos/` at the repo root).
