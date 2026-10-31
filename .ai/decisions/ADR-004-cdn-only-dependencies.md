# ADR-004: CDN-only front-end dependencies, centralized in _config.yml
- **Status:** Active
- **Date:** 2026-02-25
- **Scope:** `_config.yml`, `_includes/**`, `_layouts/**`, `assets/**`
- **Author:** human (mined from `.ai/copilot-instructions.md` + `.ai/MEMORY/LEARNINGS.md` during Lean SDD v2 migration — confirm)

## Context
The site is statically hosted (GitHub Pages option, Docker/Nginx target). Adding npm/bundler
would break the no-build-pipeline constraint, and hardcoded CDN URLs in individual layouts
had already caused inconsistent versions and a Bootstrap dependency violation in the sidebar
(2026-02-25 learning).

## Decision
All external front-end libraries load from pinned CDN URLs declared exactly once in
`_config.yml` under `cdn_libs` (Leaflet, jQuery, Bootstrap, georaster, …). Layouts reference
`{{ site.cdn_libs.* }}`; no npm/bundler; no hardcoded URLs in layouts or JS.

## Resulting Specification
- Every external library URL appears only in `_config.yml` (`cdn_libs`).
- Pinned versions; validate CORS and SRI hashes where applicable.
- Global dependencies (Bootstrap CSS/JS) load in `_includes/head.html`, not per-layout.
- No hardcoded API keys; config values enter via Jekyll config.

## Alternatives Considered
- npm/bundler asset pipeline: rejected — no build pipeline; GitHub Pages static hosting.
- Vendoring libraries into `assets/`: rejected — larger repo, manual updates.

## Consequences
- Positive: one place to bump versions; consistent library availability across layouts.
- Negative: runtime dependence on CDN availability; mitigated by pinning + graceful fallbacks
  and console error logging (never silent failures).

## Verification
- [ ] `grep -rE "cdn\.jsdelivr|unpkg|cdnjs" _layouts _includes --include="*.html" -l` → no file hardcodes a CDN URL except via `site.cdn_libs`
- [ ] `grep -c "cdn_libs" _config.yml` → ≥ 1 (section present)

## Waiver
[None]
