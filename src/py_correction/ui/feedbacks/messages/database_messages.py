from typing import override

from src.py_correction.ui.feedbacks.messages.base_message import BaseMessageText


class CourseIntegrityFailedMessage(BaseMessageText):

    def __init__(self, course_code: str, course_name: str, course_semester: str, course_group: str | int):
        super().__init__()
        self._course_code = course_code
        self._course_name = course_name
        self._course_semester = course_semester
        self._course_group = course_group

    @property
    @override
    def title(self) -> str:
        return "Erreur d'importation d'un cours dans la base de données"

    @property
    @override
    def html_text(self) -> str:
        return f"""<p>Le cours {self._course_code} - {self._course_name} pour la session {self._course_semester} et le 
                groupe {self._course_group} existe déjà. Si vous souhaitez recommencer l'importation, vous devez 
                archiver le cours déjà importé.</p>"""
