"""Baseline snapshot helper (ADR-007).

Computes the observable output state of the repository (generated _photos
markdown, topic pages, GeoJSON layers, derived permalinks) and compares it
against tests/baseline.json.

Regenerate the baseline deliberately with `make update-baseline` when output
changes legitimately. `make test` fails if current output diverges from the
baseline without such an update.
"""

import json
import pathlib

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "raw_data"
PHOTOS_DIR = PROJECT_ROOT / "_photos"
TOPICS_DIR = PROJECT_ROOT / "_topics"
MAPS_DATA_DIR = PROJECT_ROOT / "assets" / "maps_data"
BASELINE_PATH = pathlib.Path(__file__).resolve().parent / "baseline.json"


def compute_state() -> dict:
    """Compute the current observable output state of the repository."""
    raw_slugs = sorted(p.stem for p in RAW_DATA_DIR.glob("*.md"))
    photos_slugs = sorted(p.stem for p in PHOTOS_DIR.glob("*.md"))
    # Recursive: topics live in language folders (ADR-010), e.g. _topics/en/topics/x.md
    topics_slugs = sorted(p.stem for p in TOPICS_DIR.rglob("*.md"))

    geojson_features = {}
    if MAPS_DATA_DIR.exists():
        for path in sorted(MAPS_DATA_DIR.rglob("*.geojson")):
            rel = path.relative_to(PROJECT_ROOT).as_posix()
            data = json.loads(path.read_text(encoding="utf-8"))
            geojson_features[rel] = len(data.get("features", []))

    return {
        "raw_md_count": len(raw_slugs),
        "photos_md_count": len(photos_slugs),
        "topics_md_count": len(topics_slugs),
        "photos_slugs": photos_slugs,
        "topics_slugs": topics_slugs,
        # Permalinks derived from _config.yml collection config
        # (photos: /photos/:slug/, topics: /topics/:slug/), relative to baseurl.
        "photo_permalinks": [f"/photos/{slug}/" for slug in photos_slugs],
        "topic_permalinks": [f"/topics/{slug}/" for slug in topics_slugs],
        "geojson_features": geojson_features,
    }


def load_baseline() -> dict:
    return json.loads(BASELINE_PATH.read_text(encoding="utf-8"))


def diff(state: dict, baseline: dict) -> list:
    """Return a list of human-readable differences (empty when in sync)."""
    diffs = []
    for key in sorted(set(state) | set(baseline)):
        if state.get(key) != baseline.get(key):
            diffs.append(f"{key}:\n  baseline: {baseline.get(key)}\n  current:  {state.get(key)}")
    return diffs


def main() -> int:
    state = compute_state()
    BASELINE_PATH.write_text(
        json.dumps(state, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Baseline written: {BASELINE_PATH.relative_to(PROJECT_ROOT)}")
    print(f"  raw_data entries: {state['raw_md_count']}")
    print(f"  _photos pages:    {state['photos_md_count']}")
    print(f"  _topics pages:    {state['topics_md_count']}")
    print(f"  geojson layers:   {len(state['geojson_features'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
