# Current Status

## NOW
- [ ] Phase 4: Docker multi-stage build (Python pipeline stage → Jekyll build stage → Nginx serve)
- [ ] Manual browser fallback verification of topic GeoJSON (build-time hybrid + runtime fallback) still pending

## NEXT
- [ ] Continue processing `raw_data/` entries (recent work: video_cotonificio-anni_1920-1930)
- [ ] Human review of migrated `.ai/` files (Lean SDD v2 migration 2026-10-31)
- [ ] Author `en/` and `de/` translations — `index` is done in all three languages, 7 keys remain (`about`, `labels`, `map`, `photos`, `storia`, `topics`, and the topic); `make i18n-report` shows the gaps, `make i18n-scaffold LANG=en` writes the stubs
- [ ] Extract remaining Italian literals from `assets/js` and DataTables config into `_data/i18n.yml`
- [ ] Flip ADR-010 Proposed → Active once the first real translation lands — **but first correct §4**: its "`_photos/` is language-neutral (coordinates, dates, images are not translatable)" premise is false (12/12 photo pages carry Italian prose, 2,248 words); ADR-012 records the correction
- [ ] Human decision on ADR-012 (per-language photo pages): approve to `Active` or `Rejected` — the fan-out design replaces ADR-010's `raw_data/<slug>.<lang>.md` sketch
- [ ] Human decision on ADR-011 (vertical prototype): approve to `Active` or `Rejected` — it has sat at `Proposed` past the 14-day WARN threshold, as has ADR-010

## KNOWN_ISSUES
- Bug: possible boresight miscalculation in geo export — legacy note says it may use the global dataframe instead of per-row values — verify in `scripts/` — Impact: medium
- Debt: `PROJECT_MAP.md`-era docs referenced `site_source/_photos/`, but the real layout keeps source at repo root (`_photos/`), output in `_site/` — migrated docs describe the real layout — Impact: low
- Debt: `_includes/head.html` hardcodes a Google Fonts URL outside `cdn_libs` — not caught by the ADR-004 grep — Impact: low
- Change: `_config.yml` `exclude` now covers repo docs, `tests/` and build files — `/README.md`, `/AGENTS/`, `/LICENSE.md` and `/tests/*` are no longer published URLs (nothing linked to them), and `.ai/`/`.agents/` no longer trigger `jekyll serve --watch` rebuilds — Impact: low
- Debt: photo and label indexes list language-neutral items everywhere; they need the ADR-010 `lang` filter once `_photos/` carries `lang` — Impact: low
- Bug: the i18n audit is blind to `_photos/` — `iter_page_files()` and `iter_topic_files()` exclude it, so `--check` and `make i18n-report` report `FINDINGS: none` while 12/12 photo pages hold untranslated Italian prose (2,248 words) and 0/12 declare `lang` — Workaround: none; fixed by ADR-012 D8 — Impact: medium
- Debt: `_layouts/photo.html` has no i18n wiring and hardcodes 5 Italian strings (`Varianti`, `Provenienza e datazione`, `Datazione:`, `Precisione:`, `Fonte:`); `assets/js/photos-index.js` hardcodes `Cerca`/`Nessuna`/`Foto`, and the ADR-010 §3 `window.i18n` channel is not implemented — Impact: medium
- Bug: duplicate pytest discovery from generated `_site/` output — Workaround: `pytest.ini` pins `testpaths = tests` and `norecursedirs` — Impact: low

_Last updated: 2026-11-17 @ 7391398_
