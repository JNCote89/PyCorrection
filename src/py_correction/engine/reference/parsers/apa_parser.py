from functools import cached_property
import re

from src.py_correction.core.domains.shared.shared_enums import NOT_AVAILABLE


def _extract_possible_doi(url: str | None) -> str | None:
    "If student do not use the DOI directly in the citation, but use the publisher URL website."
    if url is None:
        return None

    doi_match = re.search(r'(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)', url)

    if not doi_match:
        return url

    doi_number = doi_match.group(1).rstrip('.')

    return f"https://doi.org/{doi_number}"


class APATextParser:

    def __init__(self, reference: str, href_style: str = "style='color:#3ea6ff; text-decoration: none'"):
        self.reference = reference
        self._href_style = href_style

    @cached_property
    def year(self) -> int | NOT_AVAILABLE:
        regex_year = re.search(r'\([^)]*?(\d{4})[^)]*\)', self.reference)
        if regex_year:
            return int(regex_year.group(1))
        return NOT_AVAILABLE

    @cached_property
    def title(self) -> str | None:
        # Check what is between a typical date for APA (YYYY). and a period to retrieve the title.
        # Won't return the full title if the title is split in two sentences.
        pattern = (r"\((?:(?:\d{4}[a-z]?|(?:n\.d\.|s\.\s*d\.)(?:\s*-?\s*[a-z])?|no date|in press|sous presse)"
                   r"(?:,\s*[^)]+)?)\)\.\s+(.*?)(?:\.|\s*$)")
        match = re.search(pattern, self.reference, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return "Bad citation format"

    @cached_property
    def url(self) -> str | None:
        for token in self.reference.split():
            if token.startswith("http"):
                url = token.rstrip(".")
                return _extract_possible_doi(url=url)
            if token.startswith("doi:"):
                return token.replace("doi:", "https://doi.org/", 1).rstrip(".")
        return None

    @cached_property
    def html_reference(self) -> str:
        """For dynamic label in the QTableView"""
        raw_token = None
        for token in self.reference.split():
            if token.startswith("http") or token.startswith("doi:"):
                raw_token = token
                break

        if not raw_token or not self.url:
            return self.reference

        clean_raw = raw_token.rstrip(".,;:")

        match = re.search(re.escape(raw_token), self.reference)
        if not match:
            return self.reference

        start, end = match.span()

        anchor = f"<a {self._href_style} href='{self.url}'>{clean_raw}</a>"

        return f"{self.reference[:start]}{anchor}{self.reference[end:]}"
