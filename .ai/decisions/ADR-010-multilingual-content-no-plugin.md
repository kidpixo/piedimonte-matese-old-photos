# ADR-010: Multilingual content without plugins
- **Status:** Proposed
- **Date:** 2026-10-31
- **Scope:** `_config.yml`, `_layouts/**`, `_includes/**`, `_topics/**`, `*.md`, `en/**`, `raw_data/**`, `scripts/**`, `assets/js/**`
- **Source:** Claude action-item list, ids **AI-007, AI-008, AI-009, AI-010** (adopted in reduced form: no i18n of `raw_data/` photo pages initially, no SEO work)
- **Author:** human

## Context
The human will create multilingual editorial content (Italian default + translations).
The site is built for GitHub Pages; adding plugins (e.g. jekyll-polyglot) is undesirable.
SEO is explicitly not a goal. The existing UI has Italian strings hardcoded in layouts and
`assets/js/` (DataTables already localizes to Italian).

## Decision
Hand-rolled i18n using only stock Jekyll (Liquid + `_data/` + frontmatter):

1. **Languages and URLs — folder-driven.** The URL language prefix comes from the file's
   **directory**, never from a permalink written per file. Jekyll 3.9.3 substitutes only a
   fixed placeholder set (`:collection`, `:path`, `:name`, `:slug`, `:title`,
   `:output_ext`, date tokens); a frontmatter key such as `:lang` is not one of them and
   aborts the build (`"The URL template doesn't have lang keys"` — verified against the
   project's `jekyll-lanyon` image). Therefore:
   - Collections: `_config.yml` collection permalink becomes `/:path/`, and `:path`
     (subdirectory + filename) carries the language segment.
     `_topics/topics/x.md` → `/topics/x/`, `_topics/en/topics/x.md` → `/en/topics/x/`.
   - Plain pages: the existing `permalink: pretty` already derives the URL from the
     directory — `storia.md` → `/storia/`, `en/storia.md` → `/en/storia/`.
   - Italian (default) keeps the unprefixed URLs (`/storia/`, `/topics/…`), so existing
     links keep working.
   - `lang` frontmatter is still required on every page: the folder gives the URL, the
     frontmatter gives the semantics (layout filtering, switcher, `html lang`).
   - `:path` does **not** slugify, so filenames must already be URL-safe
     (lowercase, hyphens).
   - Rationale for folders over per-file `permalink` overrides: forgetting a permalink line
     silently publishes a translation at the wrong URL; a missing language folder is
     structurally impossible.
2. **Translation grouping.** Pages sharing a `translation_key` are translations of each
   other; `id` (slug/permalink) and `translation_key` are distinct concepts. Italian
   pages carry `translation_key` too, so grouping is uniform. Under the folder convention
   the same source file name is reused in each language directory
   (`topics/x.md`, `en/topics/x.md`), so `translation_key` equals the file stem by
   convention; it is still declared explicitly so a future divergent slug stays legal.
3. **UI strings.** `_data/i18n.yml` per-language dictionaries for nav, buttons, filters,
   captions; layouts read `{% assign t = site.data.i18n[page.lang] %}`; JS receives
   strings via one `window.i18n = {{ ... | jsonify }}` line in `<head>`. No hardcoded
   Italian in templates or JS going forward.
4. **Collections.** Editorial collections (`_topics/`) render only entries matching
   `page.lang`. `_photos/` remains language-neutral (coordinates, dates, images are not
   translatable); translated photo-page text is a possible later pipeline extension.
   Because the pipeline writes `_photos/<slug>.md` and the ADR-006 audit globs that
   directory non-recursively, `_photos/` keeps its flat layout; if translated photo pages
   are ever generated, the audit globs and expected-asset paths must become recursive
   first.
   **Implementation prerequisite:** `scripts/process_research.py` globs `TOPICS_DIR/*.md`
   non-recursively in two places (topic audit, topic GeoJSON generation). Language
   subfolders would make it see zero topics and silently skip both. These globs must
   become recursive — and must filter by `lang` so a topic is not emitted once per
   translation — **before** any topic file is moved into a language folder.
5. **Fallbacks, explicit.** A missing translation never produces a 404 link: navigation
   links to the default-language page instead, while the language switcher shows an
   explicit "available in Italian only" note rather than offering a link that would
   silently switch the reader to another language. UI-string lookup falls back to the
   default-language dictionary.
6. **Completeness check.** `scripts/process_research.py --check` (or a sibling mode)
   reports dangling/duplicate `translation_key`s, missing `lang`, and switcher targets
   that do not exist — extending the ADR-006 audit pattern. It also asserts
   **folder language == `lang` frontmatter** (a file under `en/` must declare `lang: en`),
   so the URL and the semantics cannot drift apart.
   The companion `scripts/i18n_report.py` renders the same graph as a coverage matrix
   (`translation_key` × target language, target languages read from `_data/i18n.yml`),
   flags translations whose last commit predates their default-language source, and can
   scaffold the missing files. It imports the pipeline's folder rules rather than
   re-deriving them, so report and audit cannot disagree.

## Resulting Specification
- No new gems; `_config.yml` gains no plugin dependencies.
- `_config.yml` collection permalinks use `/:path/`; language comes from the directory.
- Language directories: default language at the collection root segment
  (`_topics/topics/`), translations at `_topics/<lang>/<segment>/`; plain pages mirror
  this at the repo root (`en/storia.md`).
- Every page carries `lang`; every translatable page carries `translation_key`.
- No Italian literals in `_layouts/`, `_includes/`, or `assets/js/` for UI chrome.
- Language switcher renders only existing translations (or explicit default fallback).
- `--check` reports translation-graph inconsistencies and folder/`lang` mismatches;
  errors block, warnings advise.

## Alternatives Considered
- jekyll-polyglot: rejected — no-plugin constraint (GitHub Pages); most of its value is
  the conventions above, which are cheap to hand-roll.
- Prefix all languages including Italian: rejected — breaks existing `/storia/`-style
  links for no benefit (SEO not a goal). Revisit only if URL symmetry ever matters.
- Translated `raw_data/` photo pages now: deferred — pipeline change (one
  `raw_data/[slug].<lang>.md` → two generated pages) only when translated photo text is
  actually written.

## Consequences
- Positive: zero infrastructure change; works on GitHub Pages as-is; conventions are
  visible in-repo and checkable by `--check` rather than hidden in a gem.
- Negative: the project maintains its own i18n conventions; UI-string extraction is
  tedious one-time work across layouts and JS. The folder scheme reads oddly
  (`_topics/topics/` for the default language, because the collection directory itself is
  stripped from the URL), and filenames must be URL-safe since `:path` does not slugify.
- Editorial: every `_topic` translation is content the human writes and keeps current;
  the completeness check prevents silent drift.

## Verification
- [x] `make build-site` (podman, `jekyll-lanyon:latest`) succeeds; no new gems in the Gemfile
- [x] Probe translations (`en/storia.md`, `_topics/en/topics/x.md`, `en/topics.md`) built to
      `/en/storia/`, `/en/topics/x/`, `/en/topics/`; Italian URLs unchanged (`/topics/x/`,
      `/photos/`, `/labels/` after dropping their per-file permalinks); `<html lang>` follows
      `page.lang`; probes then removed
- [x] Language switcher: with a sibling it links both ways with `hreflang`; without one it shows
      the `switcher.unavailable` note, never a dead link. Sidebar links resolve to the sibling
      when it exists and fall back to the Italian page otherwise (verified on a probe `en/` page)
- [x] Listings are language-scoped: `/topics/` and `/en/topics/` each listed only their own topic
- [x] `--check` with a file under `en/` declaring `lang: it` -> "lang 'it' disagrees with folder
      language 'en'"
- [x] `--check` with a `translation_key` that has no default-language page -> reported as an error
- [x] `python3 scripts/process_research.py geo` after moving topics into language folders ->
      `topics_scanned=1 topics_generated=1 files_written=3`, byte-identical output (proves the
      globs became recursive; a silent zero-topic run is the failure this guards)
- [x] `python -m pytest` -> 41 pass; `--check` -> errors=0 warnings=0
- [x] `scripts/i18n_report.py` renders the coverage matrix; `--scaffold en` generated the 8
      missing files, which passed `--check` unchanged (then removed — stubs holding untranslated
      Italian would publish Italian under `/en/`, the exact failure the design forbids)
- [ ] Serve smoke test with a real second language in place (only the probe run was exercised)


## Waiver
[None]
