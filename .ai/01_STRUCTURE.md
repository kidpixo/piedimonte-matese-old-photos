# Structure
Where things live. Descriptive only; code wins on conflict.
No signatures, line numbers, or invariants.

## Flow
`raw_data/*.md` + images → `scripts/process_research.py` → `_photos/` + `assets/` → Jekyll build → `_site/` → Nginx (Docker) or GitHub Pages

## Modules
- `raw_data/` — master research entries: one `[slug].md` (YAML frontmatter + research text) + primary `[slug].jpg` + optional variant images · human-curated
- `scripts/process_research.py` — data pipeline: validates frontmatter, optimizes images + thumbnails, generates `_photos/` collection, GeoJSON, integrity audit (`--check`) · entry: `scripts/process_research.py`
- `scripts/i18n_report.py` — translation coverage report (per `translation_key` × language), staleness by commit date, `--scaffold` stubs · reuses the pipeline's folder rules
- `scripts/` — pipeline support (tests under `tests/`)
- `_photos/` — generated Jekyll collection (one page per research object); never hand-edited
- `_topics/` — manual editorial essays with `featured_photos` frontmatter joining the photos collection · organized by language folder (`_topics/topics/` = it, `_topics/en/topics/` = en); the collection permalink `/:path/` makes the folder part of the URL
- `_data/i18n.yml` — UI strings per language (labels, nav, index headers); templates carry no interface literals
- root `*.md` pages — one file per language: unprefixed = default language (`it`), `en/…` = English copy sharing the same `translation_key`
- `_layouts/`, `_includes/` — Jekyll layouts (photo, topic, label, map, photos_index) and partials (head, sidebar with collapsible collection nav)
- `assets/` — all public static files: `assets/images/` (optimized), `assets/thumbs/` (150×150), `assets/data/*.geojson`, `assets/js/`, CSS
- `archive/` — private raw scans/notes; never deployed, excluded from Docker context
- `tests/` — pytest suite (`test_process_research_helpers.py`, topic GeoJSON tests)
- `Makefile` — `make build` orchestration (Python pipeline → Jekyll build)
- `Dockerfile` / `docker-compose.yml` — multi-stage deployment (Python → Jekyll → Nginx)
- `_site/` — Jekyll build output (generated)

## External Boundaries
- Map tiles: OpenStreetMap tile servers (Leaflet client-side)
- CDN libraries pinned in `_config.yml` (`cdn_libs`: Leaflet, jQuery, Bootstrap, DataTables, georaster, …)
- Deployment targets: VPS via Docker/Nginx; GitHub Pages as an option
- Geo data source: `public/photos/Photos.csv` (QGIS export) feeding GeoJSON generation

## Geo data model
- QGIS captures 3 points per photo: origin (photographer position) + vertex_left + vertex_right → FOV triangle
- Derived GeoJSON layers, split by geometry/semantics: `photos_origin.geojson` (Points) and `photos_fov.geojson` (Polygons); per-topic subsets in `assets/maps_data/topics/{slug}/{origin,fov,lov}.geojson`
- CSV is the coordinate source of truth; frontmatter carries narrative metadata (title, tags, attribution) — the two are complementary, never duplicated by hand

_Last updated: 2026-11-01 @ 7391398_
