# ADR-011: Vertical historical prototype before generic modeling
- **Status:** Proposed
- **Date:** 2026-10-31
- **Scope:** `raw_data/**`, `_topics/**`, `scripts/**`, `_layouts/**`
- **Source:** Claude action-item list, id **AI-015** (adopted; generic Entity/Event/Source
  model from AI-003 intentionally deferred until this prototype proves which parts are
  real)
- **Author:** human

## Context
External proposals (full canonical data model, events collection, timelines) risk
speculative generality: building generic machinery before any real historical object has
exercised it. The project's strength is the concrete one-way pipeline; abstractions should
be earned by a worked example.

## Decision
Build one vertical prototype on a single building/element of the cotonificio before any
generic data-model work:

- 3–4 documentable historical events for that element, each with provenance
  (ADR-009 fields: source, dating, precision)
- the relevant photographs (existing `raw_data/` entries) linked to the events
- one narrative `_topic` page presenting the events in order — exercising ADR-010 i18n by
  being the first bilingual essay (it + en)

## Resulting Specification
- The prototype demonstrates the full path: curated source → validation/schema →
  generated pages → narrative page → map, with provenance visible.
- No new collections (`_events/`) or abstractions until the prototype shows they are
  needed; if the prototype suffices without them, the generic model stays deferred.
- Findings (what the schema/provenance/i18n conventions got wrong) feed updates to
  ADR-008/009/010 before any wider rollout.

## Alternatives Considered
- Design the Entity/Event/Source model first, then fill data: rejected — the exact
  over-engineering this ADR guards against.
- Prototype without provenance/i18n to move faster: rejected — the point is to stress
  the new conventions on real material.

## Consequences
- Positive: cheap, reversible proof of the whole stack; concrete material to judge
  generic-model proposals against; first bilingual content.
- Negative: some prototype-specific choices may need rework when generalized.

## Verification
- [ ] The prototype topic page renders in it + en with no 404 links
- [ ] All prototype events carry source + dating (ADR-009 fields) visible on the page
- [ ] `python3 scripts/process_research.py --check` → clean
- [ ] `python -m pytest` → all pass
- [ ] Human verdict recorded (in `03_CURRENT_STATUS`): which generic-model parts, if
      any, the prototype justified

## Waiver
[None]
