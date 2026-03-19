import importlib
import json
import logging


def _load_module():
    return importlib.import_module("scripts.process_research")


def _configure_module_paths(process_research, monkeypatch, tmp_path):
    project_root = tmp_path
    topics_dir = project_root / "_topics"

    monkeypatch.setattr(process_research, "PROJECT_ROOT", project_root)
    monkeypatch.setattr(process_research, "TOPICS_DIR", topics_dir)
    monkeypatch.setattr(
        process_research,
        "logger",
        process_research.setup_logging(logging.ERROR),
        raising=False,
    )

    return {
        "project_root": project_root,
        "topics_dir": topics_dir,
    }


def _write_text(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_jekyll_slugify_normalizes_complex_string():
    process_research = _load_module()
    value = "  Via_Carmine -- Ponte!!! 1900  "
    assert process_research.jekyll_slugify(value) == "via-carmine-ponte-1900"


def test_derive_photo_post_rel_url_prefers_primary_image_slug():
    process_research = _load_module()
    metadata = {
        "slug": "ignored-fallback",
        "images": [
            {"file": "assets/images/secondary.jpg", "is_primary": False},
            {"file": "assets/images/Via_Carmine-main.jpg", "is_primary": True},
        ],
    }
    assert process_research.derive_photo_post_rel_url(metadata) == "/photos/via-carmine/"


def test_derive_photo_post_rel_url_falls_back_to_title_when_images_missing():
    process_research = _load_module()
    metadata = {
        "title": "Piazza Carmine 1940",
    }
    assert process_research.derive_photo_post_rel_url(metadata) == "/photos/piazza-carmine-1940/"


def test_normalize_location_data_removes_geometry_keys():
    process_research = _load_module()
    location = {
        "latitude_origin": 41.0,
        "longitude_origin": 14.0,
        "origin_geojson": "{}",
        "fov_geojson": "{}",
        "line_of_sight_geojson": "{}",
    }

    normalized = process_research.normalize_location_data(location)

    assert "origin_geojson" not in normalized
    assert "fov_geojson" not in normalized
    assert "line_of_sight_geojson" not in normalized
    assert normalized["latitude_origin"] == 41.0
    assert normalized["longitude_origin"] == 14.0


def test_add_geojson_to_location_generates_origin_fov_and_los_with_midpoint_boresight():
    process_research = _load_module()
    location = {
        "latitude_origin": 10.0,
        "longitude_origin": 20.0,
        "latitude_vertex_left": 11.0,
        "longitude_vertex_left": 21.0,
        "latitude_vertex_right": 9.0,
        "longitude_vertex_right": 23.0,
    }

    output = process_research.add_geojson_to_location(location)

    origin = json.loads(output["origin_geojson"])
    fov = json.loads(output["fov_geojson"])
    los = json.loads(output["line_of_sight_geojson"])

    assert origin["type"] == "Point"
    assert origin["coordinates"] == [20.0, 10.0]
    assert fov["type"] == "Polygon"
    assert los["type"] == "LineString"
    assert los["coordinates"][0] == [20.0, 10.0]
    assert los["coordinates"][1] == [22.0, 10.0]


def test_add_geojson_to_location_uses_explicit_boresight_when_present():
    process_research = _load_module()
    location = {
        "latitude_origin": 10.0,
        "longitude_origin": 20.0,
        "latitude_vertex_left": 11.0,
        "longitude_vertex_left": 21.0,
        "latitude_vertex_right": 9.0,
        "longitude_vertex_right": 23.0,
        "latitude_boresight": 12.0,
        "longitude_boresight": 25.0,
    }

    output = process_research.add_geojson_to_location(location)
    los = json.loads(output["line_of_sight_geojson"])

    assert los["coordinates"][1] == [25.0, 12.0]


def test_load_topic_featured_ids_extracts_valid_ids_and_skips_empty(monkeypatch, tmp_path):
    process_research = _load_module()
    paths = _configure_module_paths(process_research, monkeypatch, tmp_path)

    _write_text(
        paths["topics_dir"] / "topic-a.md",
        """---
featured_photos:
  - id: photo-1
    commentary: a
  - id: photo-2
  - commentary: missing-id
  - plain-string
---
""",
    )
    _write_text(
        paths["topics_dir"] / "topic-b.md",
        """---
featured_photos: []
---
""",
    )
    _write_text(
        paths["topics_dir"] / "topic-c.md",
        """---
title: no featured list
---
""",
    )

    topics = process_research.load_topic_featured_ids()

    assert len(topics) == 1
    assert topics[0]["slug"] == "topic-a"
    assert topics[0]["featured_ids"] == ["photo-1", "photo-2"]


def test_load_topic_featured_ids_skips_parse_failures(monkeypatch, tmp_path):
    process_research = _load_module()
    paths = _configure_module_paths(process_research, monkeypatch, tmp_path)

    _write_text(paths["topics_dir"] / "topic-a.md", "---\nfeatured_photos:\n  - id: photo-1\n---\n")
    _write_text(paths["topics_dir"] / "topic-b.md", "---\nfeatured_photos:\n  - id: photo-2\n---\n")

    original_loader = process_research.frontmatter.load

    def fake_loader(file_obj):
        if file_obj.name.endswith("topic-b.md"):
            raise ValueError("synthetic parse failure")
        return original_loader(file_obj)

    monkeypatch.setattr(process_research.frontmatter, "load", fake_loader)

    topics = process_research.load_topic_featured_ids()

    assert len(topics) == 1
    assert topics[0]["slug"] == "topic-a"
    assert topics[0]["featured_ids"] == ["photo-1"]
