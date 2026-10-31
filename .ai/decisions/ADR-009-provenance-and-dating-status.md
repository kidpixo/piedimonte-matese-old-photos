# ADR-009: Provenance and dating-status fields
- **Status:** Proposed
- **Date:** 2026-10-31
- **Scope:** `raw_data/**`, `scripts/**`, `.ai/decisions/ADR-008*` (schema prerequisite)
- **Author:** human
- **Source:** Claude action-item list, id **AI-005**

## Context
Historical data in `raw_data/` mixes facts of different epistemic strength: measured
coordinates, map-derived locations, oral tradition, guesswork. Nothing today records
where a date or location came from or how certain it is. For a research archive this is
the difference between scholarship and decoration.

## Decision
Add optional provenance fields to the `raw_data/` frontmatter schema (ADR-008) and
surface them on photo pages:

- `source`: reference to a documentary, cartographic, bibliographic, or oral source
  (free text or structured `{type, ref}` — exact shape fixed when the schema is written)
- `dating`: `documented | estimated | hypothetical` (per entry; per-field refinement
  deferred)
- `precision`: optional note on location/date uncertainty (e.g. "±5 anni", "centroid of
  frazione")

Rule: **uncertainty is recorded, never faked** — a missing date stays missing or is
explicitly `estimated`; no artificial precision is invented. Fields are optional so
existing entries remain valid.

## Resulting Specification
- Schema (ADR-008) extended with the fields above, with allowed values.
- `--check` warns on unknown `dating` values (error-level decision to be made during
  implementation).
- `_layouts/photo.html` displays provenance when present; absent fields render nothing.
- Generated `_photos/` frontmatter passes provenance through.

## Alternatives Considered
- Mandatory provenance for all entries: rejected — would invalidate existing entries and
  discourage the record-as-you-learn workflow.
- Separate provenance database: rejected — violates the one-file-per-object pattern
  (ADR-001).

## Consequences
- Positive: uncertainty is explicit and visible; research workflow (find source later)
  is supported; archive gains scholarly value.
- Negative: frontmatter becomes richer; page layout must show it without clutter.

## Verification
- [ ] `python -m pytest` → all pass, including provenance passthrough tests
- [ ] `python3 scripts/process_research.py --check` → existing entries still clean
      (fields optional)
- [ ] An entry with `dating: documentato` + `source` → provenance visible on the
      generated photo page

## Waiver
[None]
