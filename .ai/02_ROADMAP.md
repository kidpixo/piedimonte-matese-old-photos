# Roadmap

## Current Phase: Phase 4 — Docker Deployment
**Goal:** Multi-stage Docker build (Python pipeline → Jekyll build → Nginx serve) deployed on the VPS.
**Target date:** —
### In scope
- Dockerfile: stage 1 Python environment running `scripts/process_research.py` (GeoJSON + `_photos/` + image assets), stage 2 Ruby/Jekyll build, stage 3 minimal Nginx serving `_site/`
- `.dockerignore` excluding `archive/` (private research material)
- `make build` orchestration (Python script, then Jekyll build)
### Out of scope
- New `raw_data/` content processing (ongoing editorial work, separate track)
- Backend features of any kind

## Upcoming Phases
- Phase 5b: continued asset/CDN hygiene (verify SRI hashes, CORS on all pinned CDN libs)

## Completed Phases
- Phase 1: Python data pipeline (`scripts/process_research.py`) — completed 2026-02
- Phase 2: Jekyll configuration (collections + paths, CDN centralization) — completed 2026-02-25
- Phase 3: Layout templates (photo.html, topic.html, label.html) — completed 2026-02-25
- Phase 3.7: Topic-specific GeoJSON filtering (hybrid build-time + runtime fallback) — completed 2026-03-18
- Phase 5: Asset migration (`public/` → `assets/`) — completed 2026-03

_Last updated: 2026-11-01 @ 7391398_
