from typing import override

from src.py_correction.ui.feedbacks.messages.base_message import BaseMessageText
from src.py_correction.utils import list_format


class ReferenceVerificationDryRunMessage(BaseMessageText):

    def __init__(self, course_id: int | None, evaluation_id: int | None, student_id: int | None):
        self._course_id = course_id
        self._evaluation_id = evaluation_id
        self._student_id = student_id

    @property
    @override
    def title(self) -> str:
        return "Avertissement sur la vérification des références"

    @property
    @override
    def html_text(self) -> str:
        missing_ids = []

        if self._course_id is None:
            missing_ids.append("de cours")
        if self._evaluation_id is None:
            missing_ids.append("d'évaluations")
        if self._student_id is None:
            missing_ids.append("d'étudiants")

        if not missing_ids:
            return ""

        enumeration = list_format.enumeration_join(items=missing_ids)

        return f"Il n'y a pas {enumeration} associés aux références. La vérification ne sera donc pas sauvegardée."
