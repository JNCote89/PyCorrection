import logging

from bs4 import BeautifulSoup
import requests

from src.py_correction.engine.scraping.internal import pdf_verification

logger = logging.getLogger(__name__)


def get_metadata_title(url: str) -> str:
    try:
        pdf_bytes = _fetch_first_bytes(url, max_bytes=512 * 1024)

        if pdf_bytes.startswith(b"%PDF") or url.lower().endswith(".pdf"):
            return pdf_verification.extract_pdf_title(pdf_bytes)

        html_text = pdf_bytes.decode("utf-8", errors="ignore")
        return _extract_html_title(html_text)

    except requests.exceptions.Timeout:
        logger.info(f"La requête pour rejoindre le site {url} a expiré.")
        return "Les métadonnées n'ont pas pu être vérifiées en raison de problèmes à rejoindre le serveur"

    except requests.exceptions.RequestException as e:
        logger.info(f"La requête pour rejoindre le site {url} a échoué pour la raison suivante {e}.")
        return "Les métadonnées n'ont pas pu être vérifiées en raison de problèmes à rejoindre le serveur"

    except Exception as e:
        logger.info(f"La requête pour rejoindre le site {url} a échoué pour la raison suivante {e}.")
        return "Les métadonnées n'ont pas pu être vérifiées en raison de problèmes à rejoindre le serveur"


def _fetch_first_bytes(url: str, max_bytes: int = 512 * 1024) -> bytes:
    headers = {"Range": f"bytes=0-{max_bytes - 1}", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    with requests.get(url, headers=headers, stream=True, timeout=5) as response:
        response.raise_for_status()

        content = bytearray()
        for chunk in response.iter_content(chunk_size=8192):
            content.extend(chunk)
            if len(content) >= max_bytes:
                break

        return bytes(content)


def _extract_html_title(html_content: str) -> str:
    soup = BeautifulSoup(html_content, "html.parser")

    og_title = soup.find("meta", property="og:title") or soup.find("meta", attrs={"name": "DC.title"})

    if og_title and og_title.get("content"):
        return og_title["content"].strip() # type: ignore[arg-type]

    if soup.title and soup.title.string:
        return soup.title.string.strip() # type: ignore[arg-type]

    return "Aucune métadonnée n'est associée avec l'URL fournit."