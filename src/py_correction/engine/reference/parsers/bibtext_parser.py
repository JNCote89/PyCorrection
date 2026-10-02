import logging
from pathlib import Path
import re
import tempfile
import unicodedata

import pypandoc

from src.py_correction.core import paths

logging.getLogger("pypandoc").setLevel(logging.WARNING)

DEFAULT_CSL_STYLES_NAME = "universite-de-montreal-apa.csl"


def render_bibliography(bib_path: Path, csl_style_name: str = DEFAULT_CSL_STYLES_NAME,
                        output_format: str = "plain") -> str:
    safe_bib_path = Path(_clean_and_sanitize_bib(bib_path))

    content = safe_bib_path.read_text(encoding="utf-8")
    keys = re.findall(r'@([a-zA-Z]+)\s*\{\s*([^,]+),', content)
    clean_keys = [re.sub(r'[.\s]+', '_', k[1]) for k in keys]

    if not clean_keys:
        safe_bib_path.unlink(missing_ok=True)
        return "No citation keys found in .bib file."

    csl_file_path = paths.CSL_STYLES / csl_style_name

    if not csl_file_path.is_file():
        safe_bib_path.unlink(missing_ok=True)
        raise FileNotFoundError(f"CSL Style file not found at: {csl_file_path}")

    citations_trigger = " ".join([f"[@{k}]" for k in clean_keys])
    input_text = f"Force render: {citations_trigger} -DISCARD-"

    extra_args = ["--citeproc",
                  f"--bibliography={safe_bib_path.as_posix()}",
                  f"--csl={csl_file_path.as_posix()}",
                  "--wrap=none"]

    try:
        full_output = pypandoc.convert_text(input_text, to=output_format, format="markdown", extra_args=extra_args)
    finally:
        safe_bib_path.unlink(missing_ok=True)

    output_references = full_output.split("-DISCARD-")[-1].strip()
    return _sanitize_bibtex_output(output_references)


def _clean_and_sanitize_bib(input_bib_path: Path) -> str:
    content = input_bib_path.read_text(encoding="utf-8")

    def sanitize_key(match):
        entry_type = match.group(1)
        key = match.group(2)
        clean_key = re.sub(r'[.\s]+', '_', key)
        clean_key = re.sub(r'^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$', '', clean_key)
        return f"@{entry_type}{{{clean_key},"

    pattern_key = re.compile(r'@([a-zA-Z]+)\s*\{\s*([^,]+),')
    content = pattern_key.sub(sanitize_key, content)

    def sanitize_author(match):
        """To solve the problem of institution name vs last name, first name"""
        field_start = match.group(1)
        author_val = match.group(2).strip()

        if author_val.startswith("{{") and author_val.endswith("}}"):
            return match.group(0)

        # Check if it's a single entity (no comma and no ')
        if "," not in author_val and " and " not in author_val:
            # Heuristic: If it has multiple words and lacks lowercase typical first-names,
            # or matches institutional keywords, wrap it in double braces.
            # For safety, any single-string author without a comma can be treated
            # as an organization if it doesn't look like a standard "First Last" human name
            # (or you can blanket-wrap single-string authors if your library is mostly papers).
            return f"{field_start}{{{{{author_val}}}}}"

        return match.group(0)

    pattern_author = re.compile(r'(author\s*=\s*)\{([^}]+)}', re.IGNORECASE)
    content = pattern_author.sub(sanitize_author, content)

    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".bib", encoding="utf-8", delete=False)

    try:
        temp_file.write(content)
        temp_file.flush()
    except Exception:
        temp_file.close()
        Path(temp_file.name).unlink(missing_ok=True)
        raise
    finally:
        temp_file.close()

    return temp_file.name

def _sanitize_bibtex_output(text: str) -> str:
    if not text:
        return ""

    text = text.replace(r"^(∘)", "°")
    text = text.replace(r"$^{\circ}$", "°")
    text = text.replace(r"$^\circ$", "°")
    text = text.replace(r"^{\circ}", "°")
    text = text.replace(r"\circ", "°")

    text = re.sub(r"\^?\(\s*([°\\cir])\s*\)", "°", text)

    text = re.sub(r"\$([^$]+)\$", r"\1", text)

    text = text.replace("\u00A0", " ")
    text = text.replace("\r\n", "\n")

    text = re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)

    text = unicodedata.normalize("NFC", text)

    return text.encode("utf-8", errors="replace").decode("utf-8")