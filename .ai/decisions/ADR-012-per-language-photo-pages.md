# ADR-012: Per-language photo pages from a single raw_data source
- **Status:** Proposed
- **Date:** 2026-11-17
- **Scope:** `raw_data/**`, `_photos/**`, `scripts/**`, `_config.yml`, `_layouts/photo.html`, `assets/js/myscript.js`, `assets/maps_data/**`, `_data/**`, `tests/**`
- **Source:** Design discussion 2026-11-17, implementing the photo extension that ADR-010 §4
  deferred. Extends ADR-010; does not supersede it.
- **Author:** human + session (fan-out shape proposed by the human, field inventory by the session)

## Context

ADR-010 §4 deferred translated photo pages on the grounds that "`_photos/` remains
language-neutral (coordinates, dates, images are not translatable)". **That premise is false
for this repo's data**, and the human challenged it. Measured on the current tree:

| Fact | Value |
|---|---|
| Photo pages | 12, **all 12 with body text** |
| Italian body words | **2,248** total, median 124, max 427 |
| Carrying `lang` / `translation_key` | **0 of 12** |
| i18n wiring in `_layouts/photo.html` | none (no `i18n`, `page.lang`, `site.default_lang`) |
| Hardcoded Italian chrome in `photo.html` | 5 strings: `Varianti` (l.86), `Provenienza e datazione` (l.118), `Datazione:` (l.121), `Precisione:` (l.124), `Fonte:` (l.126) |
| Hardcoded Italian in `assets/js/photos-index.js` | `Cerca` (l.32), `Nessuna` (l.35/43/242), `Foto` (l.227) |
| `_photos/` coverage in `--check` | **none** — `iter_page_files()` and `iter_topic_files()` exclude it |

So `make i18n-report` reports `FINDINGS: none` while the site's main material is monolingual.
The deferral decision can stand; the stated reason cannot, and ADR-010 §4 must be corrected
before ADR-010 goes `Active`.

Two couplings make this more than "emit another markdown file":

1. **GeoJSON carries language-bearing data and URLs.** `_photo_feature_properties()`
   (`scripts/process_research.py:1538`) bakes `title` (as `text`), `labels`,
   `photo_post_rel_url` and `permalink` into every feature; `derive_photo_post_rel_url()`
   (l.1396) hardcodes `/photos/{slug}/`. `buildPopupContent()` (`assets/js/myscript.js:516`)
   renders `props.text` as the popup label and links via `SITE_BASE.origin + permalink`.
   An English reader's map popup therefore shows an Italian title and links to the Italian
   page.
2. **`_photos/` is generated** (ADR-002, one-way pipeline), so translations cannot be
   hand-written into it. They must originate in `raw_data/` and be fanned out by the script.

The human's constraint, which shapes every choice below: **do not duplicate the source entry
per language.** Geometry, image lists and map config must stay single-sourced.

## Decision

### D1 — One source entry, fan-out at build time
`raw_data/<slug>.md` remains the only source of geometry, images, dates and labels. The
pipeline emits one `_photos/` page per available language. A per-language clone of the whole
entry is forbidden (see Alternatives).

### D2 — Per-language frontmatter inline, images keyed by filename
```yaml
# raw_data/Piazza_Carmine-anni-1940-1950.md  (default language `it`, unchanged)
title: "Convento del Carmine ruderi, 1940-1950"
labels: [piazza carmine, convento del carmine, cotonificio, commerci storici]
images:
  - file: Piazza_Carmine-anni-1940-1950-restored.jpg
    is_primary: true
    note: "Main historical shot"
i18n:
  en:
    title: "Convento del Carmine ruins, 1940-1950"
    images:
      Piazza_Carmine-anni-1940-1950-restored.jpg:
        note: "Main historical shot"
        alt: "Piazza Carmine, ruins of the cotton mill, 1940s"
```
Keys under `i18n` must be members of `SUPPORTED_LANGS`. **Field-level fallback**: a language
block may set only `title`; every unset field falls back to the default-language value.
Translation is therefore incremental and can never render empty.

Images are keyed by **filename, never array index** — an index-keyed block silently
misaligns when an image is inserted or reordered, the drift ADR-001 exists to prevent.

### D3 — Body prose in body-only sidecars
Default-language body stays inline (unchanged). Translations go in
`raw_data/<slug>.<lang>.md` containing **body only, no frontmatter**.

Rationale: the median page is 124 words and the largest 427. Folding that much markdown into
`i18n.en.body: |` is unmaintainable — YAML escaping eats blockquotes and colons, and
translations become unreadable in review. The sidecar keeps prose editable and diffs legible
while still duplicating nothing but prose.

### D4 — `labels` stay a language-neutral controlled vocabulary
`labels` are **not** translated in `raw_data/`. Display is translated via a
`_data/labels.yml` map at render time.

`_layouts/label.html` builds the tag cloud by collecting `photo.labels`, deduping, and
filtering on `?tag=<slug>`. Forking labels per language would split `commerci storici` and
`historical trades` into two tags: two clouds, split counts, and `?tag=` filters that stop
working across languages. One vocabulary, N renderings.

### D5 — URLs follow ADR-010 §1; `_photos/` gains language subfolders
The photos collection permalink changes from `/photos/:slug/` to `/:path/`, mirroring topics:

| Source | URL |
|---|---|
| `_photos/photos/<slug>.md` | `/photos/<slug>/` (default language, unchanged) |
| `_photos/en/photos/<slug>.md` | `/en/photos/<slug>/` |

**Prerequisite, carried over from ADR-010 §4 and now mandatory:** every `_photos/` glob and
expected-path check must become recursive first — `PHOTOS_OUTPUT_DIR.glob("*.md")` at
`process_research.py:1200`, the expected/orphan paths at l.1271/1294/1353, and
`prune_deleted_photos()` at l.838. A non-recursive glob after the move would see zero photos
and silently skip the audit, exactly the failure ADR-010 §4 warned about for topics.

Listings must filter `site.photos` by `page.lang`, as ADR-010 §4 already requires for topics.

### D6 — GeoJSON stays single; language resolves in the client
Per-language GeoJSON is rejected: `assets/maps_data/` is 102 MB and the benefit is popup text
only. Instead each feature gains three compact properties and keeps its existing ones:

- `slug` — language-neutral identifier
- `langs` — list of languages that actually have a generated page
- `titles` — `{it: "...", en: "..."}` (short strings; negligible size)

`permalink` / `photo_post_rel_url` **keep their current meaning: the default-language URL**,
so existing consumers are unaffected. `buildPopupContent()` resolves at render time: if the
current page language is in `langs`, insert the `/<lang>` prefix; otherwise use the default.
Popup text becomes `titles[lang] || titles[default]`.

`extractPhotoSlugFromFeature()` (`myscript.js:484`) matches `/\/photos\/([^/]+)\//`, which
still matches `/en/photos/<slug>/` — verified, so slug extraction survives the prefix.

The language prefix and URL shape must arrive via the `window.i18n` channel (ADR-010 §3),
**not** as string literals in JS — `00_CONSTRAINTS.md` forbids hardcoding paths in JS.

### D7 — Photo chrome moves to `_data/i18n.yml`
The 5 strings in D-context move under a `photo:` dictionary per language, and
`_layouts/photo.html` gains the lookup `_includes/head.html:2` already uses:
`{% assign t = site.data.i18n[page.lang] | default: site.data.i18n[site.default_lang] %}`.
`assets/js/photos-index.js` reads the same strings from `window.i18n`.

### D8 — Schema and audit extend (ADR-008, ADR-006)
`i18n` is validated against a per-language sub-schema. `--check` additionally rejects: unknown
language keys; a sidecar with no matching default-language entry; an `i18n.<lang>.images` key
matching no `images[].file`; and asserts folder language == `lang` for `_photos/`, which is
today entirely unaudited.

## Resulting Specification
- One `raw_data/<slug>.md` per research object; no per-language clones of it.
- `i18n.<lang>` keys ⊆ `SUPPORTED_LANGS`; unset fields fall back to the default language.
- `i18n.<lang>.images` is keyed by image filename; every key must match an `images[].file`.
- Body translations live in `raw_data/<slug>.<lang>.md`, body-only, no frontmatter.
- `labels` are never language-qualified; display translation resolves through `_data/labels.yml`.
- Photos collection permalink is `/:path/`; default language at `_photos/photos/`,
  translations at `_photos/<lang>/photos/`.
- All `_photos/` globs and expected-path checks are recursive.
- GeoJSON geometry is byte-identical to today's; features carry `slug`, `langs`, `titles` in
  addition to the existing properties, and `permalink` still means the default-language URL.
- No Italian UI literals remain in `_layouts/photo.html` or `assets/js/photos-index.js`.
- `--check` audits `_photos/` for `lang`, folder agreement, and translation-graph integrity.
- `make i18n-report` includes photo pages in the coverage matrix.

## Alternatives Considered
- **`raw_data/<slug>.<lang>.md` as a full clone** (the option ADR-010 listed): rejected —
  duplicates coordinates, FOV polygons, image lists and map config, all of which must stay in
  lockstep. Guaranteed drift, and the human explicitly ruled it out.
- **Per-language GeoJSON**: rejected — multiplies 102 MB of `assets/maps_data/` to translate
  a popup label.
- **One page, client-side language toggle**: rejected — no `/en/photos/<slug>/` URL, no
  per-page `<html lang>`, no `hreflang`, no shareable English link. Defeats ADR-010 §1.
- **Translating `labels` per language**: rejected — forks the `/labels/` vocabulary, splits
  tag counts, breaks `?tag=` filtering across languages.
- **Body prose inline as `i18n.<lang>.body`**: rejected — 124–427 words of markdown per page
  inside YAML; editing and review cost outweighs the one extra file.
- **Flat lang-suffixed files (`_photos/<slug>.en.md`) with a `:name` permalink**: rejected —
  cannot produce a `/en/photos/...` URL, violating ADR-010 §1's folder-driven rule.

## Consequences
- **Positive:** geometry, images and dates stay single-sourced, so a translation cannot
  contradict the data; translating a photo is an editorial act on two small artefacts; image
  processing stays language-agnostic so build cost is near-flat; field-level fallback means a
  half-translated photo still renders correctly; `--check` and `i18n-report` stop being blind
  to the site's main material.
- **Negative:** `_photos/photos/` reads oddly, inherited from ADR-010's `_topics/topics/`
  shape. Making `_photos/` globs recursive is the riskiest change here — it touches the
  ADR-006 audit, orphan detection and `prune_deleted_photos()`, and a mistake fails silently
  rather than loudly. The baseline must be regenerated (ADR-007). Popup language resolution
  adds JS complexity. 2,248 words of prose is real editorial work, and it does not shrink.
- **Editorial:** sidecars must be deleted when a photo is removed; `--check` flags orphans.
  Every photo page translation is content the human writes and keeps current.
- **Cross-ADR:** ADR-010 §4's justification must be corrected before ADR-010 goes `Active`.
  ADR-008's schema gains `i18n` (its own summary already anticipates extension). ADR-009's
  `dating` and `precision` are controlled vocabularies and should render through
  `_data/i18n.yml` keys rather than be stored translated.

## Verification
- [ ] `python scripts/process_research.py --check` → `errors=0 warnings=0` on the migrated tree
- [ ] `--check` with `_photos/en/photos/x.md` declaring `lang: it` → error naming the folder/lang mismatch
- [ ] `--check` with `i18n.fr:` → error naming `fr` as an unsupported language
- [ ] `--check` with `i18n.en.images.nosuchfile.jpg:` → error naming the unknown image key
- [ ] `--check` with `raw_data/orphan.en.md` and no `raw_data/orphan.md` → error
- [ ] `python scripts/process_research.py geo` → geometry byte-identical to pre-change output;
      features additionally contain `slug`, `langs`, `titles`
- [ ] `make build-site` → both `/photos/<slug>/` and `/en/photos/<slug>/` exist; `<html lang>`
      differs between them; all pre-existing Italian URLs unchanged
- [ ] `make i18n-report` → photo rows appear in the matrix (absent today)
- [ ] `make test` → baseline diff limited to the expected new photo counts, then
      `make update-baseline` → passes
- [ ] `python -m pytest` → all pass, including new fan-out and fallback tests
- [ ] `grep -nE "Varianti|Provenienza|Datazione|Precisione|Fonte" _layouts/photo.html` → no matches
- [ ] manual: on `/en/...`, open a map popup → English title, link lands on `/en/photos/<slug>/`;
      on the Italian root, popup stays Italian
- [ ] manual: `/labels/` shows one tag per concept with translated display text, and `?tag=`
      filtering still works in both languages

## Waiver
[None. ADR-010 is `Proposed` and therefore not yet normative, so D5's change to the flat
`_photos/` layout needs no waiver — but ADR-010 §4 must be amended as stated in Consequences
before either ADR is activated. No constraint in `00_CONSTRAINTS.md` is relaxed; D6 explicitly
honours the ban on hardcoded paths in JS by routing the language prefix through `window.i18n`.]
