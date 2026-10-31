# ADR-008: Raw-data frontmatter schema
- **Status:** Proposed
- **Date:** 2026-10-31
- **Scope:** `scripts/**`, `raw_data/**`, `.ai/decisions/ADR-007*` (baseline prerequisite)
- **Author:** human
- **Source:** Claude action-item list, id **AI-003** (reduced scope: frontmatter schema only, not the full Entity/Event/Source model)

## Context
`raw_data/*.md` frontmatter is validated ad hoc inside `scripts/process_research.py`
(required-field checks, key-typo diagnostics). There is no machine-readable definition of
the schema, so new fields (provenance in ADR-009, `lang`/`translation_key` in ADR-010)
would each need bespoke validation code and could drift from documentation.

## Decision
Define the `raw_data/` frontmatter schema once, in JSON Schema, and validate against it
in the pipeline's `--check` mode. Scope is deliberately limited to the existing
`raw_data/` entry format — NOT a generic Entity/Event/Source data model (explicitly
deferred; see ADR-011 prototype).

## Resulting Specification
- `raw_data/schema.json` (or `scripts/` location) defines: required fields (`title`,
  `labels`, `primary_image`), optional fields (`date`, `location` variants incl.
  list-of-dicts, `variants` array), types and constraints.
- `process_research.py --check` reports schema violations as errors, in the existing
  errors/warnings structure (machine-readable via `--json`).
- Schema and this ADR are updated together when the schema changes.

## Alternatives Considered
- Full canonical data model (Entity/Photo/Event/Source/Relation): rejected for now —
  speculative at current data volume; revisit via ADR-011 prototype.
- Validation only in prose (documentation): rejected — not machine-checkable.

## Consequences
- Positive: one source of truth for the schema; new fields (ADR-009, ADR-010) extend it
  instead of adding ad-hoc checks; CI-ready via `--check --json`.
- Negative: schema file must be kept in sync with the validator; slight learning curve
  for JSON Schema.

## Verification
- [ ] `python -m pytest` → all pass, including schema-validation tests (valid + invalid
      fixture entries)
- [ ] `python3 scripts/process_research.py --check` → existing entries report no errors
- [ ] Adding a deliberately invalid entry in a scratch copy → `--check` reports it

## Waiver
[None]
