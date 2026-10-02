import logging
import re

from habanero import Crossref, RequestError
import httpx2
import requests

from src.py_correction.app_metadata import METADATA

logger = logging.getLogger(__name__)


def check_is_scientific_literature(url: str | None) -> bool:
    "To check if the reference needs to be processed by this module or not. CrossRef needs a DOI to work."
    if url is None:
        return False

    url = url.strip()

    scientific_prefix = ["https://doi.org/", "http://doi.org/", "https://dx.doi.org/", "http://dx.doi.org/", "doi:"]
    for prefix in scientific_prefix:
        if url.lower().startswith(prefix):
            return True

    return False


def fetch_crossref_metadata(doi: str) -> dict | None:
    clean_doi = doi.strip()

    # CrossRef need the DOI number only.
    for prefix in ["https://doi.org/", "http://doi.org/", "https://dx.doi.org/", "http://dx.doi.org/", "doi:"]:
        if clean_doi.lower().startswith(prefix):
            clean_doi = clean_doi[len(prefix):]
            break

    cr = Crossref()

    try:
        response = cr.works(ids=clean_doi,
                            headers={"User-Agent": f"{METADATA.NAME}/{METADATA.VERSION} (mailto:pycorrection@gmail.com)"})
        return response.get("message", {}) # type: ignore

    except httpx2.HTTPStatusError as e:
        if e.response.status_code == 404:
            logger.info(f"Le DOI n'a pas été trouvé dans Crossref (erreur 404) : {clean_doi}")
        else:
            logger.warning(f"Erreur HTTP {e.response.status_code} Crossref pour le DOI {clean_doi}")
        return {}

    except (httpx2.TimeoutException, httpx2.RequestError) as e:
        logger.info(f"La requête réseau a expiré ou échoué pour le DOI {clean_doi}: {e}")
        return {}

    except RequestError as e:
        logger.info(f"Erreur Habanero pour le DOI {clean_doi}: {e}")
        return {}

    except Exception as e:
        logger.exception(f"Erreur inattendue pour le DOI {clean_doi} : {e}")
        return {}


def check_is_peer_reviewed(doi: str) -> bool:
    clean_doi = doi.strip()

    # To prevent a double import
    for prefix in ["https://doi.org/", "http://doi.org/", "https://dx.doi.org/", "http://dx.doi.org/", "doi:"]:
        if clean_doi.lower().startswith(prefix):
            clean_doi = clean_doi[len(prefix):]
            break

    """Check OpenAlex directly via DOI URL to see if it belongs to a peer-reviewed journal."""
    url = f"https://api.openalex.org/works/https://doi.org/{clean_doi}"
    headers = {"User-Agent": "PyCorrectionApp/Beta (mailto:pycorrection@gmail.com)"}

    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()

            primary_location = data.get("primary_location") or {}
            source = primary_location.get("source") or {}

            # OpenAlex source type 'journal' designates peer-reviewed serials
            return source.get("type") == "journal"

    except Exception as e:
        logger.info(f"OpenAlex n'a pas été en mesure de vérifier le DOI {clean_doi} pour la raison suivante: {e}")

    return False


def check_is_article_review(title: str | None) -> bool:
    if title is None:
        return False

    review_pattern = re.compile(r"\b(review|reviews|meta-analys[ie]s|meta-synthes[ie]s|meta-ethnograph[yi]|"
                                r"scoping|systematic|narrative|integrative|critical|umbrella|rapid|"
                                r"realist|mapping|evidence gap|evidence map|state-of-the-art|"
                                r"research synthesis|evidence synthesis|PRISMA|Cochrane|JBI|PROSPERO"
                                r")\b", re.IGNORECASE, )

    return bool(review_pattern.search(title))
