"""Schema validation tests (ADR-008, ADR-009).

raw_data/schema.json must accept every existing entry shape (preferred `images`,
legacy `primary_image`, provenance fields) and reject invalid frontmatter.
"""

import json
import pathlib

import pytest
import yaml

from scripts.process_research import (
    SCHEMA_PATH,
    _json_default,
    load_frontmatter_schema,
    validate_schema,
)

SCHEMA = load_frontmatter_schema()


def _meta(**overrides):
    base = {
        "layout": "photo",
        "title": "Test Photo",
        "date": {"year": 1945, "month": 1, "day": 1},
        "labels": ["test"],
        "location": {
            "latitude_origin": 41.0,
            "longitude_origin": 14.0,
        },
        "images": [{"file": "photo.jpg"}],
    }
    base.update(overrides)
    return base


def _validate(meta):
    return validate_schema(meta, SCHEMA, pathlib.Path("entry.md"))


@pytest.mark.skipif(SCHEMA is None, reason="jsonschema or schema.json unavailable")
class TestSchemaAccepts:
    def test_valid_preferred_entry(self, tmp_path):
        assert _validate(_meta()) == []

    def test_valid_legacy_entry(self, tmp_path):
        meta = _meta()
        meta.pop("images")
        meta["primary_image"] = "photo.jpg"
        meta["variants"] = [{"file": "photo-b.jpg"}]
        assert _validate(meta) == []

    def test_provenance_fields_optional(self, tmp_path):
        assert _validate(_meta()) == []

    def test_provenance_string_source(self, tmp_path):
        meta = _meta(source="Archivio Diocesano, vol. 3", dating="estimated", precision="±5 anni")
        assert _validate(meta) == []

    def test_provenance_structured_source(self, tmp_path):
        meta = _meta(source={"type": "cartographic", "ref": "Mappa 1940"}, dating="documented")
        assert _validate(meta) == []

    def test_original_url_nullable(self, tmp_path):
        assert _validate(_meta(original_url=None)) == []

    def test_supplier_string(self, tmp_path):
        assert _validate(_meta(supplier="Istituto Luce")) == []


@pytest.mark.skipif(SCHEMA is None, reason="jsonschema or schema.json unavailable")
class TestSchemaRejects:
    def test_unknown_dating_value(self, tmp_path):
        errs = _validate(_meta(dating="certamente-documentato"))
        assert len(errs) == 1 and "dating" in errs[0]

    def test_bad_zoom_type(self, tmp_path):
        errs = _validate(_meta(map={"zoom": "venti"}))
        assert any("zoom" in e for e in errs)

    def test_unknown_top_level_key(self, tmp_path):
        errs = _validate(_meta(chiave_sconosciuta="x"))
        assert any("Additional properties" in e or "chiave_sconosciuta" in e for e in errs)

    def test_missing_location(self, tmp_path):
        meta = _meta()
        meta.pop("location")
        assert _validate(meta)

    def test_missing_required_field(self, tmp_path):
        meta = _meta()
        meta.pop("title")
        errs = _validate(meta)
        assert any("title" in e for e in errs)

    def test_legacy_list_location_accepted(self, tmp_path):
        meta = _meta(location=[{"latitude_origin": 41.0, "longitude_origin": 14.0}])
        assert _validate(meta) == []

    def test_location_missing_origin_coords(self, tmp_path):
        meta = _meta(location={"latitude_origin": 41.0})
        errs = _validate(meta)
        assert any("location" in e for e in errs)

    def test_empty_labels(self, tmp_path):
        errs = _validate(_meta(labels=[]))
        assert any("labels" in e for e in errs)


def test_every_raw_data_entry_validates():
    """All committed raw_data entries must satisfy the schema."""
    import frontmatter

    assert SCHEMA is not None
    failures = []
    for path in sorted(SCHEMA_PATH.parent.glob("*.md")):
        post = frontmatter.load(path)
        meta = json.loads(json.dumps(post.metadata, default=_json_default))
        failures.extend(validate_schema(meta, SCHEMA, path))
    assert not failures, "\n".join(failures)
