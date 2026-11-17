"""Tests for scripts/i18n_report.py (ADR-010 coverage report).

Covers URL derivation, the coverage graph (missing edges, monolingual pages,
duplicate languages) and the scaffolding helper. The report reuses the folder
rules from scripts/process_research.py, so both modules are pointed at a tmp tree.
"""

import importlib
import pathlib


def _load(tmp_path, monkeypatch):
    process_research = importlib.import_module("scripts.process_research")
    monkeypatch.setattr(process_research, "PROJECT_ROOT", tmp_path, raising=False)
    monkeypatch.setattr(process_research, "TOPICS_DIR", tmp_path / "_topics", raising=False)

    report = importlib.import_module("scripts.i18n_report")
    monkeypatch.setattr(report, "PROJECT_ROOT", tmp_path, raising=False)
    monkeypatch.setattr(report, "TOPICS_DIR", tmp_path / "_topics", raising=False)
    monkeypatch.setattr(report, "I18N_DATA", tmp_path / "_data" / "i18n.yml", raising=False)
    return report


def _write(path: pathlib.Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _page(key, lang):
    key_line = f"translation_key: {key}\n" if key else ""
    return f"---\nlayout: default\ntitle: T\nlang: {lang}\n{key_line}---\n\nbody\n"


# ---------------------------------------------------------------------------


def test_dir_url_shapes():
    report = importlib.import_module("scripts.i18n_report")
    assert report._dir_url("storia") == "/storia/"
    assert report._dir_url("en/storia") == "/en/storia/"
    assert report._dir_url("index") == "/"
    assert report._dir_url("en/index") == "/en/"
    assert report._dir_url("topics/x") == "/topics/x/"


def test_graph_missing_edges_and_monolingual(tmp_path, monkeypatch):
    report = _load(tmp_path, monkeypatch)
    _write(tmp_path / "storia.md", _page("storia", "it"))
    _write(tmp_path / "en" / "storia.md", _page("storia", "en"))
    _write(tmp_path / "about.md", _page("about", "it"))
    _write(tmp_path / "technical.md", _page(None, "en"))

    langs = ["it", "en", "de"]
    graph = report.build_graph(report.collect_entries(), langs)
    by_key = {item["key"]: item for item in graph["matrix"]}

    assert by_key["storia"]["missing"] == ["de"]
    assert by_key["storia"]["langs"] == {"it": "storia.md", "en": "en/storia.md"}
    assert by_key["about"]["missing"] == ["en", "de"]
    assert [row["path"] for row in graph["monolingual"]] == ["technical.md"]


def test_topic_urls_and_language_folders(tmp_path, monkeypatch):
    report = _load(tmp_path, monkeypatch)
    _write(
        tmp_path / "_topics" / "topics" / "x.md",
        "---\nlayout: topic\ntitle: X\nlang: it\ntranslation_key: x\n---\n\nit\n",
    )
    _write(
        tmp_path / "_topics" / "en" / "topics" / "x.md",
        "---\nlayout: topic\ntitle: X\nlang: en\ntranslation_key: x\n---\n\nen\n",
    )

    graph = report.build_graph(report.collect_entries(), ["it", "en"])
    item = graph["matrix"][0]
    assert item["key"] == "x"
    assert item["missing"] == []
    urls = {row["lang"]: row["url"] for row in item["rows"]}
    assert urls == {"it": "/topics/x/", "en": "/en/topics/x/"}


def test_explicit_permalink_overrides_folder_url(tmp_path, monkeypatch):
    report = _load(tmp_path, monkeypatch)
    _write(
        tmp_path / "404.md",
        "---\nlayout: default\ntitle: 404\nlang: it\npermalink: 404.html\n---\n\nx\n",
    )
    graph = report.build_graph(report.collect_entries(), ["it"])
    assert [row["url"] for row in graph["monolingual"]] == ["/404.html"]


def test_duplicate_language_is_detected(tmp_path, monkeypatch):
    report = _load(tmp_path, monkeypatch)
    _write(tmp_path / "storia.md", _page("storia", "it"))
    # Wrong folder: an English file parked at the root still claims `it` by folder.
    _write(tmp_path / "storia-alt.md", _page("storia", "it"))

    graph = report.build_graph(report.collect_entries(), ["it"])
    assert graph["matrix"][0]["duplicate_langs"] == ["it"]


def test_target_languages_follows_i18n_data_order(tmp_path, monkeypatch):
    report = _load(tmp_path, monkeypatch)
    _write(tmp_path / "_data" / "i18n.yml", "it:\n  label: Italiano\nen:\n  label: English\n")
    assert report.target_languages() == ["it", "en"]


def test_target_languages_falls_back_to_supported(tmp_path, monkeypatch):
    report = _load(tmp_path, monkeypatch)
    langs = report.target_languages()  # no _data/i18n.yml in the tmp tree
    assert langs[0] == report.DEFAULT_LANG
    assert set(langs) == set(report.SUPPORTED_LANGS)


def test_scaffold_creates_missing_translation(tmp_path, monkeypatch):
    report = _load(tmp_path, monkeypatch)
    src = tmp_path / "storia.md"
    _write(src, _page("storia", "it"))

    graph = report.build_graph(report.collect_entries(), ["it", "en"])
    created = report.scaffold("en", graph, ["it", "en"])

    assert created == [str(pathlib.Path("en") / "storia.md")]
    text = (tmp_path / "en" / "storia.md").read_text(encoding="utf-8")
    assert "lang: en" in text
    assert "translation_key: storia" in text
    assert report.SCAFFOLD_MARKER in text

    # Second run must not clobber the file the author is editing.
    again = report.scaffold("en", report.build_graph(report.collect_entries(), ["it", "en"]), ["it", "en"])
    assert again == []
