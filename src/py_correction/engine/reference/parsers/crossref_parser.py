import html
import json
import logging
import os
import re
import tempfile

import pypandoc

from src.py_correction.core import paths

logging.getLogger("pypandoc").setLevel(logging.WARNING)

DEFAULT_CSL_STYLES_NAME = "universite-de-montreal-apa.csl"


def format_crossref_to_csl(crossref_message: dict, csl_style_name: str = DEFAULT_CSL_STYLES_NAME) -> str:
    citekey = "target_ref"
    csl_item = _crossref_json_to_csl_item(crossref_message=crossref_message, citekey=citekey)
    csl_database = [csl_item]

    # Create temporary file without auto-deletion and close handle before Pandoc runs
    bibliography_file = tempfile.NamedTemporaryFile("w+", suffix=".json", encoding="utf-8", delete=False)
    try:
        json.dump(csl_database, bibliography_file)
        bibliography_file.close()  # Releases the file handle so Pandoc can read it on Windows

        csl_file_path = paths.CSL_STYLES.joinpath(csl_style_name)

        # Force an explicit citation in the text body so the CSL engine renders it
        markdown_input = f"Force render: @{citekey} -DISCARD-"

        extra_args = [
            "--citeproc",
            f"--bibliography={bibliography_file.name}",
            f"--csl={csl_file_path.as_posix()}",
        ]

        output = pypandoc.convert_text(source=markdown_input, to="plain", format="markdown", extra_args=extra_args)

        # Discard the citation triggers
        output_references = output.split("-DISCARD-")[-1].strip()
        return output_references.strip()

    finally:
        # Guarantee cleanup of temporary file
        if os.path.exists(bibliography_file.name):
            os.unlink(bibliography_file.name)


def _clean_crossref_text(text: str, preserve_formatting: bool = True) -> str:
    if not isinstance(text, str) or not text.strip():
        return ""

    cleaned = html.unescape(text)

    cleaned = re.sub(r"</?(?:scp|font|span|style)[^>]*>", "", cleaned, flags=re.IGNORECASE)

    if preserve_formatting:
        cleaned = re.sub(r"</?(?:i|em)>", "*", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"</?(?:b|strong)>", "**", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"<sub>(.*?)</sub>", r"~\1~", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"<sup>(.*?)</sup>", r"^\1^", cleaned, flags=re.IGNORECASE)
    else:
        cleaned = re.sub(r"<[^>]+>", "", cleaned)

    cleaned = re.sub(r"\s+", " ", cleaned)

    return cleaned.strip()


def _crossref_json_to_csl_item(crossref_message: dict, citekey: str = "item1") -> dict:
    data = crossref_message
    csl_item = {"id": citekey}

    type_map = {"journal-article": "article-journal",
                "book-chapter": "chapter",
                "posted-content": "article",
                "monograph": "book",
                "edited-book": "book",
                "proceedings-article": "paper-conference"}
    csl_item["type"] = type_map.get(data.get("type"), "article") # type: ignore[arg-type]

    string_fields = [("title", "title"), ("container-title", "container-title"), ("publisher", "publisher"),
                     ("DOI", "DOI")]

    for target_key, src_key in string_fields:
        val = data.get(src_key)

        raw_val = val[0] if isinstance(val, list) and val else val

        if isinstance(raw_val, str) and raw_val.strip():
            if target_key == "DOI":
                csl_item[target_key] = _clean_crossref_text(raw_val, preserve_formatting=False)
            else:
                csl_item[target_key] = _clean_crossref_text(raw_val, preserve_formatting=True)

    for key in ["volume", "issue", "page"]:
        if data.get(key):
            csl_item[key] = str(data[key]).strip()

    if "author" in data and isinstance(data["author"], list):
        authors = []
        for a in data["author"]:
            author_obj = {}
            if "given" in a:
                author_obj["given"] = _clean_crossref_text(a["given"], preserve_formatting=False)
            if "family" in a:
                author_obj["family"] = _clean_crossref_text(a["family"], preserve_formatting=False)
            if "literal" in a:
                author_obj["literal"] = _clean_crossref_text(a["literal"], preserve_formatting=False)

            if author_obj:
                authors.append(author_obj)
        if authors:
            csl_item["author"] = authors # type: ignore

    date_source = (data.get("published-print") or data.get("published-online") or data.get("issued")
                   or data.get("created"))

    if date_source and "date-parts" in date_source:
        date_parts = date_source["date-parts"]
        if isinstance(date_parts, list) and len(date_parts) > 0:
            csl_item["issued"] = {"date-parts": date_parts} # type: ignore

    return csl_item