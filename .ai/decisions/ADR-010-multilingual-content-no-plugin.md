# ADR-010: Multilingual content without plugins
- **Status:** Proposed
- **Date:** 2026-10-31
- **Scope:** `_config.yml`, `_layouts/**`, `_includes/**`, `_topics/**`, `raw_data/**`, `scripts/**`, `assets/js/**`
- **Source:** Claude action-item list, ids **AI-007, AI-008, AI-009, AI-010** (adopted in reduced form: no i18n of `raw_data/` photo pages initially, no SEO work)
- **Author:** human

## Context
The human will create multilingual editorial content (Italian default + translations).
The site is built for GitHub Pages; adding plugins (e.g. jekyll-polyglot) is undesirable.
SEO is explicitly not a goal. The existing UI has Italian strings hardcoded in layouts and
`assets/js/` (DataTables already localizes to Italian).

## Decision
Hand-rolled i18n using only stock Jekyll (Liquid + `_data/` + frontmatter):

1. **Languages and URLs.** `lang` frontmatter on every page. Italian (default) stays at
   the repo root URLs (`/storia/`, …) — existing links keep working. Translations get
   language-prefixed permalinks (`/en/storia/`).
2. **Translation grouping.** Pages sharing a `translation_key` are translations of each
   other; `id` (slug/permalink) and `translation_key` are distinct concepts. Italian
   pages carry `translation_key` too, so grouping is uniform.
3. **UI strings.** `_data/i18n.yml` per-language dictionaries for nav, buttons, filters,
   captions; layouts read `{% assign t = site.data.i18n[page.lang] %}`; JS receives
   strings via one `window.i18n = {{ ... | jsonify }}` line in `<head>`. No hardcoded
   Italian in templates or JS going forward.
4. **Collections.** Editorial collections (`_topics/`) render only entries matching
   `page.lang`. `_photos/` remains language-neutral (coordinates, dates, images are not
   translatable); translated photo-page text is a possible later pipeline extension.
5. **Fallbacks, explicit.** A missing translation never produces a 404 link: nav and
   language switcher link to the default-language page instead; UI-string lookup falls
   back to the Italian dictionary.
6. **Completeness check.** `scripts/process_research.py --check` (or a sibling mode)
   reports dangling/duplicate `translation_key`s, missing `lang`, and switcher targets
   that do not exist — extending the ADR-006 audit pattern.

## Resulting Specification
- No new gems; `_config.yml` gains no plugin dependencies.
- Every page carries `lang`; every translatable page carries `translation_key`.
- No Italian literals in `_layouts/`, `_includes/`, or `assets/js/` for UI chrome.
- Language switcher renders only existing translations (or explicit default fallback).
- `--check` reports translation-graph inconsistencies; errors block, warnings advise.

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
  tedious one-time work across layouts and JS.
- Editorial: every `_topic` translation is content the human writes and keeps current;
  the completeness check prevents silent drift.

## Verification
- [ ] `bundle exec jekyll build` → succeeds with no new gems added to the Gemfile
- [ ] Language switcher on a translated page → links to the sibling translation; on a
      untranslated page → links to the Italian page (no 404)
- [ ] `--check` with a deliberately dangling `translation_key` → reports it
- [ ] `python -m pytest` → all pass

## Waiver
[None]
