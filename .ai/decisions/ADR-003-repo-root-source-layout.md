# ADR-003: Source layout at repo root (no site_source/)
- **Status:** Active
- **Date:** 2026-02-20
- **Scope:** `_config.yml`, `_photos/**`, `_topics/**`
- **Author:** human (mined from `.ai/PROJECT_MAP.md` during Lean SDD v2 migration — confirm)

## Context
Early refactor plans nested the Jekyll source under `site_source/`. Jekyll's default
workflow is source at root with output in `_site/`, and the repo had already settled on
that layout.

## Decision
Keep the Jekyll source at the repository root (`_photos/`, `_topics/`, `_layouts/`,
`assets/` at root level) with output in `_site/`. No `site_source/` folder.

## Resulting Specification
- Collections are `_photos/` and `_topics/` at the repo root, registered in `_config.yml`.
- `_config.yml` excludes `archive/`, `raw_data/`, and `scripts/` from the build.

## Alternatives Considered
- `site_source/` nesting: rejected as unnecessary churn versus Jekyll defaults.

## Consequences
- Positive: standard Jekyll tooling and mental model; fewer path overrides.
- Negative: root directory holds both site source and pipeline/data directories; `.gitignore`
  and `_config.yml` exclusions must keep them apart.

## Verification
- [ ] `grep -E "source:|destination:" _config.yml` → no `site_source` override (defaults in force)
- [ ] `bundle exec jekyll build` (or `make build`) → succeeds, output in `_site/`

## Waiver
[None]
