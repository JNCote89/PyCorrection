import logging
from pathlib import Path
from typing import TYPE_CHECKING

from src.py_correction.core.domains.reference.reference_dtos import (ReferenceSubmissionsDTO, ReferenceTableDTO,
                                                                     ReferenceUpdateDTO)
from src.py_correction.core.domains.reference.reference_enums import RelevanceLevelEnum
from src.py_correction.engine.reference.parsers.apa_parser import APATextParser
from src.py_correction.engine.scraping.internal import doi_verification
from src.py_correction.engine.scraping.verification_pipeline import (ScientificReferenceVerificationPipeline,
                                                                     URLReferenceVerificationPipeline)

if TYPE_CHECKING:
    from src.py_correction.core.event_bus import EventBus
    from src.py_correction.core.settings_manager import SettingsManager
    from src.py_correction.services.domains.course.course_services import CourseServices
    from src.py_correction.services.domains.course_path.course_path_services import CoursePathServices
    from src.py_correction.services.domains.evaluation.evaluation_services import EvaluationServices
    from src.py_correction.services.domains.student.student_services import StudentServices
    from src.py_correction.services.domains.reference.reference_services import ReferenceServices
    from src.py_correction.services.domains.student.student_evaluation_services import StudentEvaluationServices

logger = logging.getLogger(__name__)


class ReferenceOrchestrator:

    def __init__(self, settings_manager: "SettingsManager", course_services: "CourseServices",
                 evaluation_services: "EvaluationServices",
                 course_path_services: "CoursePathServices", reference_services: "ReferenceServices",
                 student_services: "StudentServices", student_evaluation_services: "StudentEvaluationServices",
                 event_bus: "EventBus"):
        self._settings_manager = settings_manager
        self._course_services = course_services
        self._evaluation_services = evaluation_services
        self._course_path_services = course_path_services
        self._reference_services = reference_services
        self._student_services = student_services
        self._student_evaluation_services = student_evaluation_services

        self._event_bus = event_bus

    def get_evaluation_submission_directory(self, course_id: int, evaluation_id: int, student_id: int
                                            ) -> list[Path] | Path | None:
        submission_directory = self._course_path_services.get_submissions_directory(course_id=course_id)

        if submission_directory is None:
            return None

        evaluation_title = self._evaluation_services.get_evaluation_title(evaluation_id=evaluation_id)

        if evaluation_title is None:
            return submission_directory

        student_full_name = self._student_services.get_student_full_name(student_id=student_id)

        if student_full_name is None:
            return submission_directory

        evaluation_submission_directory = submission_directory / evaluation_title

        if not evaluation_submission_directory.exists():
            return None

        return self._return_student_submission_directories(student_full_name=student_full_name,
                                                           evaluation_directory=evaluation_submission_directory)

    def get_evaluation_correction_directory(self, course_id: int, evaluation_id: int, student_id: int) -> Path | None:
        correction_directory = self._course_path_services.get_correction_directory(course_id=course_id)

        if correction_directory is None:
            return None

        evaluation_title = self._evaluation_services.get_evaluation_title(evaluation_id=evaluation_id)

        if evaluation_title is None:
            return correction_directory

        student_full_name = self._student_services.get_student_full_name(student_id=student_id)

        if student_full_name is None:
            return correction_directory

        evaluation_correction_directory = correction_directory / evaluation_title

        if not evaluation_correction_directory.exists():
            return None

        return self._return_student_correction_directory(student_full_name=student_full_name,
                                                         evaluation_directory=evaluation_correction_directory)

    def save_and_get_reference_table_dtos(self, evaluation_id: int | None, student_id: int | None,
                                          reference_submissions_dto: ReferenceSubmissionsDTO) -> list[ReferenceTableDTO]:

        excluded_urls = self._student_evaluation_services.get_excluded_urls(
            student_id=student_id, evaluation_ids=reference_submissions_dto.excluded_evaluation_ids)
        excluded_titles = self._student_evaluation_services.get_excluded_titles(
            student_id=student_id, evaluation_ids=reference_submissions_dto.excluded_evaluation_ids)

        student_evaluation_id = self._student_evaluation_services.get_student_evaluation_id(
            student_id=student_id, evaluation_id=evaluation_id)

        parsed_references = []

        for raw_reference in reference_submissions_dto.references:
            parsed_reference = APATextParser(reference=raw_reference)

            if parsed_reference.title in excluded_titles or parsed_reference.url in excluded_urls:
                continue
            parsed_references.append(ReferenceTableDTO(reference_id=None,
                                                       student_reference=parsed_reference.reference,
                                                       student_reference_html=parsed_reference.html_reference,
                                                       cross_reference=None,
                                                       verification_status=None,
                                                       evidence_level=None,
                                                       relevance=None,
                                                       reference_type=None,
                                                       year=parsed_reference.year,
                                                       url=parsed_reference.url,
                                                       title=parsed_reference.title,
                                                       peer_reviewed=None))

        if student_evaluation_id is None:
            return parsed_references

        else:
            table_dtos = self._reference_services.bulk_insert_references(student_evaluation_id=student_evaluation_id,
                                                                         reference_table_dtos=parsed_references)
            return table_dtos

    def delete_references(self, evaluation_id: int | None, student_id: int | None) -> None:
        student_evaluation_id = self._student_evaluation_services.get_student_evaluation_id(
            student_id=student_id, evaluation_id=evaluation_id)

        if student_evaluation_id:
            self._reference_services.delete_references_by_relationship(student_evaluation_id=student_evaluation_id)

    def get_reference_table_dtos(self, evaluation_id: int | None, student_id: int | None
                                 ) -> list[ReferenceTableDTO] | None:
        student_evaluation_id = self._student_evaluation_services.get_student_evaluation_id(
            student_id=student_id, evaluation_id=evaluation_id)

        if student_evaluation_id is None:
            return None

        references = self._reference_services.get_reference_table_dtos(
            student_evaluation_id=student_evaluation_id)
        return references

    def reference_verification(self, reference_table_dto: ReferenceTableDTO) -> ReferenceTableDTO:
        is_scientific_literature = doi_verification.check_is_scientific_literature(url=reference_table_dto.url)

        if is_scientific_literature:
            scientific_pipeline = ScientificReferenceVerificationPipeline(reference_table_dto=reference_table_dto)
            verified_reference_table_dto = scientific_pipeline.execute()

            reference_update_dto = ReferenceUpdateDTO.from_table_dto(table_dto=verified_reference_table_dto)
            self._reference_services.update_reference(reference_update_dto=reference_update_dto)

            return verified_reference_table_dto

        else:
            url_pipeline = URLReferenceVerificationPipeline(reference_table_dto=reference_table_dto)
            verified_reference_table_dto = url_pipeline.execute()

            reference_update_dto = ReferenceUpdateDTO.from_table_dto(table_dto=verified_reference_table_dto)
            self._reference_services.update_reference(reference_update_dto=reference_update_dto)

            return verified_reference_table_dto

    @staticmethod
    def dry_reference_verification(reference_table_dto: ReferenceTableDTO) -> ReferenceTableDTO:
        is_scientific_literature = doi_verification.check_is_scientific_literature(url=reference_table_dto.url)

        if is_scientific_literature:
            scientific_pipeline = ScientificReferenceVerificationPipeline(reference_table_dto=reference_table_dto)
            verified_reference_table_dto = scientific_pipeline.execute()
            return verified_reference_table_dto

        else:
            url_pipeline = URLReferenceVerificationPipeline(reference_table_dto=reference_table_dto)
            verified_reference_table_dto = url_pipeline.execute()
            return verified_reference_table_dto

    def batch_relevant_evaluation(self, reference_table_dtos: list[ReferenceTableDTO]) -> list[ReferenceTableDTO]:
        bulk_update_reference_dtos = []
        modify_table_dtos = []
        for reference in reference_table_dtos:
            if reference.relevance is not None:
                modify_table_dtos.append(reference)
            else:
                # To avoid type hint error with direct assignment
                setattr(reference, "relevance", RelevanceLevelEnum.RELEVANT)

                modify_table_dtos.append(reference)
                bulk_update_reference_dtos.append(ReferenceUpdateDTO(reference_id=reference.reference_id,
                                                                     relevance=reference.relevance))

        self._reference_services.bulk_update_references(reference_update_dtos=bulk_update_reference_dtos)

        return modify_table_dtos

    @staticmethod
    def dry_batch_relevant_evaluation(reference_table_dto: ReferenceTableDTO) -> ReferenceTableDTO:
        if reference_table_dto.relevance is None:
            reference_table_dto.relevance = RelevanceLevelEnum.RELEVANT

        return reference_table_dto

    def get_save_path(self, course_id: int | None, evaluation_id: int | None,
                      student_id: int | None) -> Path:

        if course_id is not None and evaluation_id is not None and student_id is not None:
            student_correction_directory = self.get_evaluation_correction_directory(course_id=course_id,
                                                                                    evaluation_id=evaluation_id,
                                                                                    student_id=student_id)

            evaluation_title = self._evaluation_services.get_evaluation_title(evaluation_id=evaluation_id)

            student_name = self._student_services.get_student_full_name(student_id=student_id)

            if student_correction_directory is not None:
                return student_correction_directory / f"{student_name} - {evaluation_title}"

        return self._settings_manager.restored_settings.user_root_directory

    @staticmethod
    def _return_student_submission_directories(student_full_name: str, evaluation_directory: Path) -> list[Path]:
        # Moodle split directories between different kind of submissions (e.g., online_text and files)
        student_directories = []
        for student_directory in evaluation_directory.iterdir():
            if student_directory.name.startswith(student_full_name):
                student_directories.append(student_directory)

        if student_directories:
            return student_directories

        # Sometimes GeNote and Moodle have a slightly different spelling for student and won't match, hence
        # the fallback on the top directory. Also prevent crashes if the student has submitted nothing.
        return [evaluation_directory]

    @staticmethod
    def _return_student_correction_directory(student_full_name: str, evaluation_directory: Path) -> Path:
        for student_directory in evaluation_directory.iterdir():
            if student_directory.name.startswith(student_full_name):
                return student_directory

        # Sometimes GeNote and Moodle have a slightly different spelling for student and won't match, hence
        # the fallback on the top directory. Also prevent crashes if the student has submitted nothing.
        return evaluation_directory