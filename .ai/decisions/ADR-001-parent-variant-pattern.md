# ADR-001: Parent-Variant pattern for research objects
- **Status:** Active
- **Date:** 2026-02-15
- **Scope:** `raw_data/**`, `scripts/**`, `_photos/**`
- **Author:** human (mined from `.ai/PROJECT_MAP.md` during Lean SDD v2 migration — confirm)

## Context
A historical research object (e.g. a monastery facade) exists in multiple visual
representations: the original scan, a digitally restored version, detail crops. The naive
model — one entry per image — caused metadata duplication and data drift between entries
describing the same object.

## Decision
Each `raw_data/[slug].md` file represents ONE research object/event. It stores one
`primary_image` plus an optional `variants` array (`{file, type, note}`). The Python
pipeline processes the primary image and every variant, generating
`assets/images/variants/[slug]/…` and matching thumbnails, and preserves `type`/`note`.

## Resulting Specification
- `raw_data/[slug].md` must carry `title` and `labels`; optional `date`,
  `location: {lat, lng}`, `variants` array.
- A variant must never become its own `raw_data/` entry.
- All variants of an object inherit the object's date, location, and labels.
- Generated collection entries (`_photos/[slug].md`) must link primary and variant assets.

## Alternatives Considered
- One entry per image: rejected because metadata (location, date, labels) is duplicated per
  image and drifts apart.

## Consequences
- Positive: single source of truth per object; adding a view is one array element.
- Negative: `raw_data/` frontmatter is richer; the pipeline must handle nested variant
  processing and folder hierarchy.

## Verification
- [ ] `python3 scripts/process_research.py --check` → no errors (source/generated consistent)
- [ ] `python -m pytest` → all tests pass (conda env `cotonificio`)

## Waiver
[None]
