import importlib
import json
import logging


def _write_text(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_topic_markdown(path, featured_ids):
    featured_block = "\n".join([f"  - id: {item}\n    commentary: test" for item in featured_ids])
    _write_text(
        path,
        f"""---
title: Topic Test
featured_photos:
{featured_block}
---

Topic body.
""",
    )


def _load_module():
    return importlib.import_module("scripts.process_research")


def _configure_paths(process_research, monkeypatch, tmp_path):
    project_root = tmp_path
    maps_data_dir = project_root / "assets" / "maps_data"
    topics_dir = project_root / "_topics"
    topic_maps_dir = maps_data_dir / "topics"

    monkeypatch.setattr(process_research, "PROJECT_ROOT", project_root)
    monkeypatch.setattr(process_research, "MAPS_DATA_DIR", maps_data_dir)
    monkeypatch.setattr(process_research, "TOPICS_DIR", topics_dir)
    monkeypatch.setattr(process_research, "TOPIC_MAPS_DIR", topic_maps_dir)
    monkeypatch.setattr(
        process_research,
        "logger",
        process_research.setup_logging(logging.ERROR),
        raising=False,
    )

    return {
        "topics_dir": topics_dir,
        "topic_maps_dir": topic_maps_dir,
    }


def _metadata_with_geo(process_research, slug, title):
    metadata = {
        "slug": slug,
        "title": title,
        "date": "1900-01-01",
        "labels": ["test"],
        "location": [
            {
                "latitude_origin": 41.0,
                "longitude_origin": 14.0,
                "latitude_vertex_left": 41.01,
                "longitude_vertex_left": 14.01,
                "latitude_vertex_right": 40.99,
                "longitude_vertex_right": 14.02,
            }
        ],
    }
    process_research.process_location_data(metadata, source=f"{slug}.md")
    return metadata


def test_generate_topic_geojson_raises_for_missing_featured_id(monkeypatch, tmp_path):
    process_research = _load_module()
    paths = _configure_paths(process_research, monkeypatch, tmp_path)

    _write_topic_markdown(paths["topics_dir"] / "topic-a.md", featured_ids=["missing-photo"])
    all_metadata = [
        _metadata_with_geo(process_research, "photo-1", "Photo One"),
    ]

    try:
        process_research.generate_topic_geojson(all_metadata)
        assert False, "Expected ValueError for missing featured photo id"
    except ValueError as exc:
        assert "references missing photo" in str(exc)
        assert "missing-photo" in str(exc)


def test_generate_topic_geojson_writes_origin_fov_lov_files(monkeypatch, tmp_path):
    process_research = _load_module()
    paths = _configure_paths(process_research, monkeypatch, tmp_path)

    _write_topic_markdown(paths["topics_dir"] / "topic-a.md", featured_ids=["photo-1"])
    all_metadata = [
        _metadata_with_geo(process_research, "photo-1", "Photo One"),
    ]

    stats = process_research.generate_topic_geojson(all_metadata)
    assert stats["ok"] is True
    assert stats["topics_scanned"] == 1
    assert stats["topics_generated"] == 1
    assert stats["files_written"] == 3

    topic_dir = paths["topic_maps_dir"] / "topic-a"
    origin_path = topic_dir / "origin.geojson"
    fov_path = topic_dir / "fov.geojson"
    lov_path = topic_dir / "lov.geojson"

    assert origin_path.exists()
    assert fov_path.exists()
    assert lov_path.exists()

    origin = json.loads(origin_path.read_text(encoding="utf-8"))
    fov = json.loads(fov_path.read_text(encoding="utf-8"))
    lov = json.loads(lov_path.read_text(encoding="utf-8"))

    assert origin["type"] == "FeatureCollection"
    assert fov["type"] == "FeatureCollection"
    assert lov["type"] == "FeatureCollection"

    assert len(origin["features"]) == 1
    assert len(fov["features"]) == 1
    assert len(lov["features"]) == 1

    assert origin["features"][0]["geometry"]["type"] == "Point"
    assert fov["features"][0]["geometry"]["type"] == "Polygon"
    assert lov["features"][0]["geometry"]["type"] == "LineString"

    assert origin["features"][0]["properties"]["photo_post_rel_url"] == "/photos/photo-1/"
