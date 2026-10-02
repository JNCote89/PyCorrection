from pathlib import Path

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from src.py_correction.services.domains.course_path.course_path_services import CoursePathServices
    from src.py_correction.services.domains.evaluation.evaluation_services import EvaluationServices

class PathResolver:

    def __init__(self, course_path_services: "CoursePathServices", evaluation_services: "EvaluationServices"):
        self._course_path_services = course_path_services
        self._evaluation_services = evaluation_services

    def get_evaluation_correction_directory(self, course_id: int, evaluation_id: int) -> Path | None:
        correction_directory = self._course_path_services.get_correction_directory(course_id=course_id)
        evaluation_title = self._evaluation_services.get_evaluation_title(evaluation_id=evaluation_id)

        if not correction_directory or not evaluation_title:
            return None

        path = Path(correction_directory) / evaluation_title

        return path

    def get_evaluation_submission_directory(self, evaluation_id: int, course_id: int) -> Path | None:
        submissions_directory = self._course_path_services.get_submissions_directory(course_id=course_id)
        evaluation_title = self._evaluation_services.get_evaluation_title(evaluation_id=evaluation_id)

        if not submissions_directory or not evaluation_title:
            return None

        path = Path(submissions_directory) / evaluation_title

        return path