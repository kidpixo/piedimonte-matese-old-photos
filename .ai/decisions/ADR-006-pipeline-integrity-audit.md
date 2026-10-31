# ADR-006: Pipeline integrity audit mode
- **Status:** Active
- **Date:** 2026-03-14
- **Scope:** `scripts/**`
- **Author:** human (mined from `.ai/PROJECT_MAP.md` + `.ai/IMPLEMENTATION_STEPS.md` during Lean SDD v2 migration — confirm)

## Context
With `_photos/` and `assets/` fully generated (ADR-002), drift between sources and generated
files — orphans, stale entries, frontmatter typos — was previously found only by hand.

## Decision
`scripts/process_research.py --check` audits source/generated consistency and reports
errors and warnings. Machine-readable `--json` for CI; `--strict-warnings` fails when
warnings exist; `--clean [--yes]` removes orphan files after an integrity check.

## Resulting Specification
- Exit code contract: `--check` → `0` clean, `1` errors, `2` internal failure;
  `--check --strict-warnings` returns `-1` when warnings exist (shell sees `255`).
- Short switches available: `-l` log, `-c` check, `-C` clean, `-y` yes, `-j` json,
  `-w` strict-warnings, `-p` changed --prune.
- `location` is normalized to a single dict (list-of-dicts input supported); Geo key typo
  diagnostics include expected vs found keys and likely matches.
- Run `--check` after any pipeline change.

## Alternatives Considered
- External linter/CI-only validation: rejected — the pipeline already walks all sources;
  a built-in mode keeps one source of truth for the validation rules.

## Consequences
- Positive: drift is caught mechanically; CI can gate on `--check --json`.
- Negative: audit rules live inside `process_research.py` and must evolve with the
  frontmatter schema.

## Verification
- [ ] `python3 scripts/process_research.py --check` → no errors on a clean tree
- [ ] `python3 scripts/process_research.py --check --json` → valid JSON report
- [ ] `python -m pytest` → all tests pass (helper coverage includes check-mode logic)

## Waiver
[None]
