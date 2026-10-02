from contextlib import contextmanager
import io
import os
import sys
import tempfile

from pypdf import PdfReader

# PDF title warns through the console that the openai package is not installed.
_old_stdout = sys.stdout
_old_stderr = sys.stderr
sys.stdout = open(os.devnull, 'w')
sys.stderr = open(os.devnull, 'w')

import pdftitle

sys.stdout.close()
sys.stderr.close()
sys.stdout = _old_stdout
sys.stderr = _old_stderr


@contextmanager
def suppress_output():
    """Redirects stdout and stderr to devnull to suppress third-party print statements."""
    with open(os.devnull, 'w') as devnull:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = devnull
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr


def extract_pdf_title(pdf_bytes: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        if reader.metadata and reader.metadata.title:
            title = reader.metadata.title.strip()

            if title and not title.lower().startswith("microsoft word"):
                return title
    except Exception:
        pass

    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True) as temp_pdf:
            temp_pdf.write(pdf_bytes)
            temp_pdf.flush()

            with suppress_output():
                extracted_title = pdftitle.get_title_from_file(temp_pdf.name) # type: ignore
            if extracted_title:
                return extracted_title.strip()
    except Exception:
        pass

    return "Les métadonnées ne sont pas disponibles pour le fichier PDF"
