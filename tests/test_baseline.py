"""Baseline regression test (ADR-007).

Fails when generated output (photos pages, topics, GeoJSON layers, permalinks)
diverges from tests/baseline.json without a deliberate `make update-baseline`.
"""

import baseline


def test_output_matches_baseline():
    state = baseline.compute_state()
    try:
        expected = baseline.load_baseline()
    except FileNotFoundError:
        raise AssertionError(
            "tests/baseline.json missing — run `make update-baseline` to create it"
        )

    diffs = baseline.diff(state, expected)
    assert not diffs, (
        "Generated output diverged from baseline (tests/baseline.json).\n"
        "If this change is intentional, regenerate with `make update-baseline`.\n\n"
        + "\n".join(diffs)
    )


def test_baseline_covers_required_keys():
    expected = baseline.load_baseline()
    for key in (
        "raw_md_count",
        "photos_md_count",
        "topics_md_count",
        "photos_slugs",
        "topics_slugs",
        "photo_permalinks",
        "topic_permalinks",
        "geojson_features",
    ):
        assert key in expected, f"baseline.json missing key: {key}"
