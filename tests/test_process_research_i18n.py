"""i18n audit tests (ADR-010).

Covers the folder-driven language rules: folder/lang agreement, the translation
graph, the monolingual-page exemption, and topic discovery across language folders.
"""

import importlib
import logging
import pathlib


def _load_module():
    return importlib.import_module("scripts.process_research")


def _configure(process_research, monkeypatch, tmp_path):
    project_root = tmp_path
    monkeypatch.setattr(process_research, "PROJECT_ROOT", project_root)
    monkeypatch.setattr(process_research, "TOPICS_DIR", project_root / "_topics")
    monkeypatch.setattr(
        process_research,
        "logger",
        process_research.setup_logging(logging.ERROR),
        raising=False,
    )
    return project_root


def _write(path, frontmatter):
    path.parent.mkdir(parents=True, exist_ok=True)
    body = "".join(f"{k}: {v}\n" for k, v in frontmatter.items())
    path.write_text(f"---\n{body}---\n\nContent.\n", encoding="utf-8")


def test_topic_lang_from_path_defaults_and_detects(monkeypatch, tmp_path):
    pr = _load_module()
    _configure(pr, monkeypatch, tmp_path)

    default = pr.topic_lang_from_path(tmp_path / "_topics" / "topics" / "x.md")
    english = pr.topic_lang_from_path(tmp_path / "_topics" / "en" / "topics" / "x.md")
    assert default == pr.DEFAULT_LANG
    assert english == "en"


def test_page_lang_from_path(monkeypatch, tmp_path):
    pr = _load_module()
    _configure(pr, monkeypatch, tmp_path)

    assert pr.page_lang_from_path(tmp_path / "storia.md") == pr.DEFAULT_LANG
    assert pr.page_lang_from_path(tmp_path / "en" / "storia.md") == "en"


def test_iter_page_files_skips_repo_docs(monkeypatch, tmp_path):
    pr = _load_module()
    root = _configure(pr, monkeypatch, tmp_path)

    _write(root / "storia.md", {"lang": "it"})
    _write(root / "README.md", {})
    _write(root / "AGENTS.md", {})

    names = {p.name for p in pr.iter_page_files()}
    assert names == {"storia.md"}


def test_audit_accepts_default_tree(monkeypatch, tmp_path):
    pr = _load_module()
    root = _configure(pr, monkeypatch, tmp_path)

    _write(root / "storia.md", {"lang": "it", "translation_key": "storia"})
    _write(root / "en" / "storia.md", {"lang": "en", "translation_key": "storia"})
    _write(root / "_topics" / "topics" / "t.md", {"lang": "it", "translation_key": "t"})
    _write(root / "_topics" / "en" / "topics" / "t.md", {"lang": "en", "translation_key": "t"})

    result = pr.audit_i18n_for_check()
    assert result["errors"] == [], result["errors"]
    assert result["translation_keys"] == 2


def test_audit_flags_missing_lang(monkeypatch, tmp_path):
    pr = _load_module()
    root = _configure(pr, monkeypatch, tmp_path)

    _write(root / "storia.md", {"translation_key": "storia"})

    assert any("missing 'lang'" in e for e in pr.audit_i18n_for_check()["errors"])


def test_audit_flags_folder_lang_mismatch(monkeypatch, tmp_path):
    pr = _load_module()
    root = _configure(pr, monkeypatch, tmp_path)

    _write(root / "en" / "storia.md", {"lang": "it", "translation_key": "storia"})

    errors = pr.audit_i18n_for_check()["errors"]
    assert any("disagrees with folder language" in e for e in errors)


def test_audit_allows_monolingual_page_at_root(monkeypatch, tmp_path):
    """technical.md: English content, no translation_key, lives at /technical/."""
    pr = _load_module()
    root = _configure(pr, monkeypatch, tmp_path)

    _write(root / "technical.md", {"lang": "en"})

    assert pr.audit_i18n_for_check()["errors"] == []


def test_audit_flags_duplicate_language_in_key(monkeypatch, tmp_path):
    pr = _load_module()
    root = _configure(pr, monkeypatch, tmp_path)

    _write(root / "storia.md", {"lang": "it", "translation_key": "storia"})
    _write(root / "storia-alt.md", {"lang": "it", "translation_key": "storia"})

    errors = pr.audit_i18n_for_check()["errors"]
    assert any("duplicate languages" in e for e in errors)


def test_audit_flags_key_without_default_language(monkeypatch, tmp_path):
    pr = _load_module()
    root = _configure(pr, monkeypatch, tmp_path)

    _write(root / "en" / "storia.md", {"lang": "en", "translation_key": "storia"})

    errors = pr.audit_i18n_for_check()["errors"]
    assert any("no it (default-language) page" in e for e in errors)


def test_topic_discovery_across_language_folders(monkeypatch, tmp_path):
    """Translations of one topic must yield one entry, default language winning."""
    pr = _load_module()
    root = _configure(pr, monkeypatch, tmp_path)

    def write_topic(rel_path, lang):
        path = root / "_topics" / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"---\nlang: {lang}\ntranslation_key: t\n"
            "featured_photos:\n  - id: one\n---\n\nContent.\n",
            encoding="utf-8",
        )

    # English first on disk: the default-language entry must still win.
    write_topic(pathlib.Path("en") / "topics" / "t.md", "en")
    write_topic(pathlib.Path("topics") / "t.md", "it")

    topics = pr.load_topic_featured_ids()
    assert len(topics) == 1
    assert topics[0]["lang"] == pr.DEFAULT_LANG
