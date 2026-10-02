from html.parser import HTMLParser
import re

from rapidfuzz import fuzz, utils


class SmartHTMLCleaner(HTMLParser):
    def __init__(self):
        super().__init__()
        self.result = []

    def handle_data(self, data):
        self.result.append(data)

    def get_text(self) -> str:
        return " ".join(self.result)


def clean_html_title(raw_title: str | None) -> str:
    if not raw_title:
        return ""

    parser = SmartHTMLCleaner()
    parser.feed(raw_title)
    text = parser.get_text()

    cleaned = re.sub(r'\s+', ' ', text).strip()
    return cleaned


def title_similarity(student_title: str | None, metadata_title: str | None, similarity_threshold: float = 0.85,
                     short_title_word_threshold=4, short_title_similarity_threshold: float = 0.9) -> bool:
    """ Based on the Levenshtein distance between titles """
    if not student_title or not metadata_title:
        return False

    student_clean_title = _sanitized_title(student_title)
    metadata_clean_title = _sanitized_title(metadata_title)

    if not student_clean_title or not metadata_clean_title:
        return False

    # Prevent False Positives: Guard against extreme length mismatches
    len_ratio = min(len(student_clean_title), len(metadata_clean_title)
                    ) / max(len(student_clean_title), len(metadata_clean_title))

    if len_ratio < 0.4 or len(student_clean_title) <= short_title_word_threshold:
        short_title_score = fuzz.token_set_ratio(student_clean_title, metadata_clean_title) / 100.0
        # Enforce stricter rules if there is a big mismatch in title length to avoid matching generic words.
        return short_title_score >= short_title_similarity_threshold

    set_score = fuzz.token_set_ratio(student_clean_title, metadata_clean_title) / 100.0
    if set_score >= similarity_threshold:
        return True

    # Fallback: QRatio (Character N-grams) catches glued words if token matching missed them
    qgram_score = fuzz.QRatio(student_clean_title, metadata_clean_title) / 100.0
    return qgram_score >= similarity_threshold


def _sanitized_title(title: str):
    title_without_tags = clean_html_title(title)
    return utils.default_process(title_without_tags)