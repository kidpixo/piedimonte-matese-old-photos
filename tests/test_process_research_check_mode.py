import importlib
import json
import logging


def _write_text(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_raw_photo_markdown(path, image_name="photo.jpg"):
    _write_text(
        path,
        f"""---
title: Test Photo
date: 1900-01-01
labels:
  - test
location:
  - latitude_origin: 41.0
    longitude_origin: 14.0
primary_image: {image_name}
---

Body.
""",
    )


def _write_topic_markdown(path, featured_id):
    _write_text(
        path,
        f"""---
title: Test Topic
featured_photos:
  - id: {featured_id}
    commentary: test
---

Topic body.
""",
    )


def _load_module():
    return importlib.import_module("scripts.process_research")


def _configure_paths(process_research, monkeypatch, tmp_path):
    project_root = tmp_path
    raw_data_dir = project_root / "raw_data"
    photos_output_dir = project_root / "_photos"
    assets_dir = project_root / "assets"
    images_dir = assets_dir / "images"
    thumbs_dir = assets_dir / "thumbs"
    maps_data_dir = assets_dir / "maps_data"
    topics_dir = project_root / "_topics"
    topic_maps_dir = maps_data_dir / "topics"
    variants_dir = images_dir / "variants"
    variants_thumbs_dir = thumbs_dir / "variants"

    monkeypatch.setattr(process_research, "PROJECT_ROOT", project_root)
    monkeypatch.setattr(process_research, "RAW_DATA_DIR", raw_data_dir)
    monkeypatch.setattr(process_research, "PHOTOS_OUTPUT_DIR", photos_output_dir)
    monkeypatch.setattr(process_research, "ASSETS_DIR", assets_dir)
    monkeypatch.setattr(process_research, "IMAGES_DIR", images_dir)
    monkeypatch.setattr(process_research, "THUMBS_DIR", thumbs_dir)
    monkeypatch.setattr(process_research, "MAPS_DATA_DIR", maps_data_dir)
    monkeypatch.setattr(process_research, "TOPICS_DIR", topics_dir)
    monkeypatch.setattr(process_research, "TOPIC_MAPS_DIR", topic_maps_dir)
    monkeypatch.setattr(process_research, "VARIANTS_DIR", variants_dir)
    monkeypatch.setattr(process_research, "VARIANTS_THUMBS_DIR", variants_thumbs_dir)
    monkeypatch.setattr(
        process_research,
        "logger",
        process_research.setup_logging(logging.ERROR),
        raising=False,
    )

    return {
        "project_root": project_root,
        "raw_data_dir": raw_data_dir,
        "photos_output_dir": photos_output_dir,
        "topics_dir": topics_dir,
        "topic_maps_dir": topic_maps_dir,
    }


def test_audit_topics_reports_missing_featured_photo(monkeypatch, tmp_path):
    process_research = _load_module()
    paths = _configure_paths(process_research, monkeypatch, tmp_path)

    _write_topic_markdown(paths["topics_dir"] / "topic-a.md", featured_id="missing-photo")

    result = process_research.audit_topics_for_check(
        raw_slugs={"photo-1"},
        photos_slugs={"photo-1"},
    )

    assert result["topics_md_files"] == 1
    assert result["topics_with_featured"] == 1
    assert any("not found in raw_data/*.md" in msg for msg in result["errors"])


def test_run_check_mode_json_includes_topic_stats_and_missing_topic_files_warning(monkeypatch, tmp_path, capsys):
    process_research = _load_module()
    paths = _configure_paths(process_research, monkeypatch, tmp_path)

    _write_raw_photo_markdown(paths["raw_data_dir"] / "photo-1.md", image_name="photo.jpg")
    _write_text(paths["raw_data_dir"] / "photo.jpg", "not-an-image")
    _write_text(paths["photos_output_dir"] / "photo-1.md", "---\ntitle: generated\n---\n")
    _write_topic_markdown(paths["topics_dir"] / "topic-a.md", featured_id="photo-1")

    exit_code = process_research.run_check_mode(json_output=True, strict_warnings=False)
    assert exit_code == 0

    captured = capsys.readouterr()
    report = json.loads(captured.out)

    assert report["stats"]["topics_md_files"] == 1
    assert report["stats"]["topics_with_featured"] == 1
    assert report["stats"]["expected_topic_geojson_files"] == 3
    assert any("Missing topic GeoJSON" in msg for msg in report["warnings"])


def test_run_check_mode_strict_warnings_fails_on_missing_topic_geojson(monkeypatch, tmp_path):
    process_research = _load_module()
    paths = _configure_paths(process_research, monkeypatch, tmp_path)

    _write_raw_photo_markdown(paths["raw_data_dir"] / "photo-1.md", image_name="photo.jpg")
    _write_text(paths["raw_data_dir"] / "photo.jpg", "not-an-image")
    _write_text(paths["photos_output_dir"] / "photo-1.md", "---\ntitle: generated\n---\n")
    _write_topic_markdown(paths["topics_dir"] / "topic-a.md", featured_id="photo-1")

    exit_code = process_research.run_check_mode(json_output=False, strict_warnings=True)
    assert exit_code == -1