# Current Status

## NOW
- [ ] Phase 4: Docker multi-stage build (Python pipeline stage → Jekyll build stage → Nginx serve)
- [ ] Manual browser fallback verification of topic GeoJSON (build-time hybrid + runtime fallback) still pending

## NEXT
- [ ] Continue processing `raw_data/` entries (recent work: video_cotonificio-anni_1920-1930)
- [ ] Human review of migrated `.ai/` files (Lean SDD v2 migration 2026-10-31)

## KNOWN_ISSUES
- Bug: possible boresight miscalculation in geo export — legacy note says it may use the global dataframe instead of per-row values — verify in `scripts/` — Impact: medium
- Debt: `PROJECT_MAP.md`-era docs referenced `site_source/_photos/`, but the real layout keeps source at repo root (`_photos/`), output in `_site/` — migrated docs describe the real layout — Impact: low
- Bug: duplicate pytest discovery from generated `_site/` output — Workaround: `pytest.ini` pins `testpaths = tests` and `norecursedirs` — Impact: low

_Last updated: 2026-10-31 @ 0c053d5_
