#!/usr/bin/env python3
"""Translation coverage report (ADR-010).

Shows, per `translation_key`, which languages exist and which are missing, so a
gap in the multilingual corpus is visible before a reader finds it as a 404.

The folder rules come from `scripts/process_research.py` — the same functions the
build audit uses — so the report and `--check` can never disagree about what a
language folder means.

Usage:
    python scripts/i18n_report.py                  human-readable tables
    python scripts/i18n_report.py --format md      markdown, for an issue or doc
    python scripts/i18n_report.py --format json    machine-readable
    python scripts/i18n_report.py --stale          flag translations older than their source
    python scripts/i18n_report.py --scaffold en    create stubs for one missing language
    python scripts/i18n_report.py --fail-on-missing  exit 1 when edges are missing

Scope: pages and topics only. Generated `_photos/` records carry no `lang` yet,
so they are language-neutral by construction and are not part of the graph.

Exit code: 1 on audit errors, or on missing translations with --fail-on-missing.
"""

import argparse
import datetime
import json
import pathlib
import subprocess
import sys

import frontmatter
import yaml

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.process_research import (  # noqa: E402
    DEFAULT_LANG,
    SUPPORTED_LANGS,
    TOPICS_DIR,
    audit_i18n_for_check,
    iter_page_files,
    iter_topic_files,
    page_lang_from_path,
    topic_lang_from_path,
)

I18N_DATA = PROJECT_ROOT / "_data" / "i18n.yml"
SCAFFOLD_MARKER = "TODO: translate"


# ---------------------------------------------------------------------------
# Collection
# ---------------------------------------------------------------------------

def _dir_url(rel: str) -> str:
    """`a/b/index` -> `/a/b/`, `a/b` -> `/a/b/` (Jekyll pretty/permalink shape)."""
    if rel.endswith("index"):
        rel = rel[: -len("index")].rstrip("/")
    return f"/{rel}/" if rel else "/"


def page_url(path: pathlib.Path) -> str:
    rel = path.relative_to(PROJECT_ROOT).as_posix()
    return _dir_url(rel[:-3])


def topic_url(path: pathlib.Path) -> str:
    rel = path.relative_to(TOPICS_DIR).as_posix()
    return _dir_url(rel[:-3])


def target_languages() -> list:
    """Languages the site intends to publish, default first.

    `_data/i18n.yml` is the source of truth: a language gets a dictionary before
    it gets content, so the report asks for exactly what the interface promises.
    """
    langs = []
    if I18N_DATA.exists():
        raw = yaml.safe_load(I18N_DATA.read_text(encoding="utf-8")) or {}
        # File order is kept: it is the author's priority order, not alphabetical.
        langs = [k for k, v in raw.items() if isinstance(v, dict) and k in SUPPORTED_LANGS]
    if not langs:
        langs = sorted(SUPPORTED_LANGS)
    if DEFAULT_LANG in langs:
        langs.remove(DEFAULT_LANG)
    return [DEFAULT_LANG] + langs


def collect_entries() -> list:
    """One record per page/topic file, with folder and declared language."""
    entries = []
    sources = [(p, "page") for p in iter_page_files()]
    sources += [(p, "topic") for p in iter_topic_files()]

    for path, kind in sources:
        try:
            post = frontmatter.load(path)
        except Exception as exc:  # unreadable frontmatter: report it, keep going
            entries.append(
                {
                    "path": path.relative_to(PROJECT_ROOT).as_posix(),
                    "kind": kind,
                    "error": f"unreadable frontmatter: {exc}",
                }
            )
            continue

        meta = post.metadata
        declared = meta.get("lang")
        folder_lang = (
            topic_lang_from_path(path) if kind == "topic" else page_lang_from_path(path)
        )
        derived = topic_url(path) if kind == "topic" else page_url(path)
        # An explicit `permalink:` overrides the folder-derived URL (404.md does this).
        explicit = meta.get("permalink")
        url = f"/{str(explicit).lstrip('/')}" if explicit else derived
        entries.append(
            {
                "path": path.relative_to(PROJECT_ROOT).as_posix(),
                "kind": kind,
                "key": meta.get("translation_key"),
                "declared_lang": str(declared) if declared is not None else None,
                "folder_lang": folder_lang,
                # The folder wins in the URL, so it is what the graph is built on.
                "lang": folder_lang,
                "title": str(meta.get("title") or ""),
                "url": url,
            }
        )
    return entries


def git_mtime(rel_path: str):
    """Last commit touching the path; None when untracked or git is unavailable."""
    try:
        proc = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "--", rel_path],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=10,
        )
        out = proc.stdout.strip()
        return int(out) if out else None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

def build_graph(entries: list, langs: list) -> dict:
    """Group entries by translation_key and compute the missing edges."""
    groups = {}
    monolingual = []
    broken = []

    for entry in entries:
        if entry.get("error"):
            broken.append(entry)
            continue
        key = entry["key"]
        if not key:
            monolingual.append(entry)
            continue
        groups.setdefault(str(key), {"page": [], "topic": []})[entry["kind"]].append(entry)

    matrix = []
    for key in sorted(groups):
        rows = groups[key]["page"] + groups[key]["topic"]
        present = {row["lang"]: row for row in rows}
        duplicates = sorted({row["lang"] for row in rows if present[row["lang"]] is not row})
        matrix.append(
            {
                "key": key,
                "langs": {
                    lang: present[lang]["path"] for lang in present if lang in langs
                },
                "unexpected": sorted(set(present) - set(langs)),
                "missing": [lang for lang in langs if lang not in present],
                "duplicate_langs": duplicates,
                "has_default": DEFAULT_LANG in present,
                "kinds": sorted({row["kind"] for row in rows}),
                "rows": sorted(rows, key=lambda r: (r["kind"], r["lang"])),
            }
        )

    return {"matrix": matrix, "monolingual": monolingual, "broken": broken}


def stale_rows(graph: dict) -> list:
    """Translations whose last commit predates their default-language source."""
    stamps = {}
    for item in graph["matrix"]:
        for row in item["rows"]:
            stamps[row["path"]] = git_mtime(row["path"])

    stale = []
    for item in graph["matrix"]:
        source = next((r for r in item["rows"] if r["lang"] == DEFAULT_LANG), None)
        if not source:
            continue
        source_stamp = stamps.get(source["path"])
        if source_stamp is None:
            continue
        for row in item["rows"]:
            if row["lang"] == DEFAULT_LANG:
                continue
            stamp = stamps.get(row["path"])
            if stamp is not None and stamp < source_stamp:
                age = (source_stamp - stamp) / 86400
                stale.append(
                    {
                        "key": item["key"],
                        "lang": row["lang"],
                        "path": row["path"],
                        "source": source["path"],
                        "behind_days": round(age),
                    }
                )
    return stale


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def render_text(graph: dict, langs: list, stale: list, audit: dict) -> str:
    out = []
    header = ", ".join(
        f"{lang} (default)" if lang == DEFAULT_LANG else lang for lang in langs
    )
    out.append(f"Target languages: {header}")
    out.append("")

    for kind, label in (("page", "PAGES"), ("topic", "TOPICS")):
        rows = [item for item in graph["matrix"] if kind in item["kinds"]]
        out.append(label)
        if not rows:
            out.append("  (none)")
            out.append("")
            continue
        width = max([len(item["key"]) for item in rows] + [len("translation_key")])
        out.append(f"  {'translation_key'.ljust(width)}  " + "  ".join(l.ljust(2) for l in langs) + "  missing")
        for item in rows:
            cells = "  ".join(
                ("x" if item["langs"].get(lang) else "-").ljust(2) for lang in langs
            )
            missing = ", ".join(item["missing"]) or "-"
            out.append(f"  {item['key'].ljust(width)}  {cells}  {missing}")
        out.append("")

    out.append("MONOLINGUAL (no translation_key: one URL, every language)")
    if graph["monolingual"]:
        for row in graph["monolingual"]:
            out.append(f"  {row['path']}  [{row['declared_lang']}]  {row['url']}")
    else:
        out.append("  (none)")
    out.append("")

    if stale:
        out.append("STALE (translation older than its default-language source)")
        for row in stale:
            out.append(
                f"  {row['lang']:>3}  {row['path']}  behind {row['source']} by "
                f"~{row['behind_days']}d"
            )
        out.append("")

    findings = [("error", e) for e in audit["errors"]] + [("warn", w) for w in audit["warnings"]]
    out.append("FINDINGS (from the ADR-010 audit)")
    if findings:
        for level, message in findings:
            out.append(f"  {level}: {message}")
    else:
        out.append("  none")
    out.append("")

    complete = sum(1 for item in graph["matrix"] if not item["missing"])
    total_missing = sum(len(item["missing"]) for item in graph["matrix"])
    out.append("SUMMARY")
    out.append(f"  keys={len(graph['matrix'])}  complete={complete}/{len(graph['matrix'])}")
    out.append(
        f"  pages={audit['pages_checked']}  monolingual={len(graph['monolingual'])}  "
        f"missing_edges={total_missing}"
    )
    return "\n".join(out)


def render_markdown(graph: dict, langs: list, stale: list, audit: dict) -> str:
    out = []
    out.append(
        "Target languages: "
        + ", ".join(
            f"`{lang}` (default)" if lang == DEFAULT_LANG else f"`{lang}`" for lang in langs
        )
    )
    out.append("")
    for kind, label in (("page", "Pages"), ("topic", "Topics")):
        rows = [item for item in graph["matrix"] if kind in item["kinds"]]
        out.append(f"### {label}")
        out.append("")
        if not rows:
            out.append("_None._")
            out.append("")
            continue
        out.append("| translation_key | " + " | ".join(langs) + " | missing |")
        out.append("|---" * (len(langs) + 2) + "|")
        for item in rows:
            cells = ["x" if item["langs"].get(lang) else "" for lang in langs]
            out.append(f"| `{item['key']}` | " + " | ".join(cells) + f" | {', '.join(item['missing']) or '-'} |")
        out.append("")

    out.append("### Monolingual")
    out.append("")
    if graph["monolingual"]:
        out.append("| file | lang | url |")
        out.append("|---|---|---|")
        for row in graph["monolingual"]:
            out.append(f"| `{row['path']}` | {row['declared_lang']} | `{row['url']}` |")
    else:
        out.append("_None._")
    out.append("")

    if stale:
        out.append("### Stale translations")
        out.append("")
        out.append("| lang | file | source | behind |")
        out.append("|---|---|---|---|")
        for row in stale:
            out.append(
                f"| {row['lang']} | `{row['path']}` | `{row['source']}` | ~{row['behind_days']}d |"
            )
        out.append("")

    findings = [("error", e) for e in audit["errors"]] + [("warn", w) for w in audit["warnings"]]
    out.append("### Findings")
    out.append("")
    if findings:
        for level, message in findings:
            out.append(f"- **{level}**: {message}")
    else:
        out.append("_None._")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Scaffolding
# ---------------------------------------------------------------------------

def scaffold(lang: str, graph: dict, langs: list) -> list:
    """Create empty translations for `lang`, copying front matter from the source."""
    if lang not in langs:
        raise SystemExit(f"unknown language '{lang}' (known: {', '.join(langs)})")

    created = []
    for item in graph["matrix"]:
        if lang in item["langs"]:
            continue
        source = next((r for r in item["rows"] if r["lang"] == DEFAULT_LANG), None)
        if source is None:
            continue  # nothing to copy from; --check already flags the missing default

        source_path = PROJECT_ROOT / source["path"]
        if source["kind"] == "topic":
            rel = source_path.relative_to(TOPICS_DIR)
            parts = list(rel.parts)
            parts.insert(0, lang)
            dest = TOPICS_DIR.joinpath(*parts)
        else:
            rel = source_path.relative_to(PROJECT_ROOT)
            dest = PROJECT_ROOT / lang / rel.name

        if dest.exists():
            print(f"skip (exists): {dest.relative_to(PROJECT_ROOT)}")
            continue

        post = frontmatter.load(source_path)
        meta = dict(post.metadata)
        meta["lang"] = lang
        body = post.content.strip()
        text = frontmatter.dumps(
            frontmatter.Post(
                f"<!-- {SCAFFOLD_MARKER} {source['path']} -->\n\n{body}",
                **meta,
            )
        )
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text + "\n", encoding="utf-8")
        print(f"created: {dest.relative_to(PROJECT_ROOT)}")
        created.append(str(dest.relative_to(PROJECT_ROOT)))
    return created


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Translation coverage report (ADR-010)")
    parser.add_argument("-f", "--format", choices=["text", "md", "json"], default="text")
    parser.add_argument("--stale", action="store_true", help="compare commit dates with the source")
    parser.add_argument("--scaffold", metavar="LANG", help="create stubs for a missing language")
    parser.add_argument("--fail-on-missing", action="store_true", help="exit 1 when translations are missing")
    args = parser.parse_args()

    langs = target_languages()
    entries = collect_entries()
    graph = build_graph(entries, langs)
    audit = audit_i18n_for_check()
    stale = stale_rows(graph) if (args.stale or args.format == "json") else []

    if args.scaffold:
        created = scaffold(args.scaffold, graph, langs)
        print(f"\n{len(created)} file(s) created; fill them in, then re-run --check.")

    if args.format == "json":
        payload = {
            "generated": datetime.datetime.now().isoformat(timespec="seconds"),
            "default_lang": DEFAULT_LANG,
            "target_langs": langs,
            "graph": {
                "matrix": graph["matrix"],
                "monolingual": graph["monolingual"],
                "broken": graph["broken"],
            },
            "stale": stale,
            "audit": audit,
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    elif args.format == "md":
        print(render_markdown(graph, langs, stale, audit))
    else:
        print(render_text(graph, langs, stale, audit))

    if audit["errors"]:
        return 1
    if args.fail_on_missing and any(item["missing"] for item in graph["matrix"]):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
