from typing import TYPE_CHECKING

from src.py_correction.core.domains.grade.grade_dtos import UpdateGradeDTO
from src.py_correction.core.domains.reference.reference_dtos import ReferenceTableDTO
from src.py_correction.core.domains.reference.reference_enums import ReferenceTypeEnum
from src.py_correction.core.domains.reference.reference_figures_dtos import GradeReferencePlotDTO
from src.py_correction.database.student.models.student_evaluation_orm import StudentEvaluationORM
from src.py_correction.database.student.student_evaluation_CRUD import StudentEvaluationCRUD

if TYPE_CHECKING:
    from sqlalchemy.orm import sessionmaker
    from src.py_correction.core.event_bus import EventBus


class StudentEvaluationServices:

    def __init__(self, session_factory: "sessionmaker", event_bus: "EventBus"):
        self._session_factory = session_factory
        self._student_evaluation_crud = StudentEvaluationCRUD()
        self._event_bus = event_bus

    def get_student_evaluation_id(self, student_id: int | None, evaluation_id: int | None) -> int | None:
        if student_id is None or evaluation_id is None:
            return None

        with self._session_factory.begin() as session:
            student_evaluation_id = self._student_evaluation_crud.get_id_by_foreign_key(session=session,
                                                                                        student_id=student_id,
                                                                                        evaluation_id=evaluation_id)
            return student_evaluation_id

    def get_reference_table_dtos(self, student_id: int | None, evaluation_id: int | None
                                 ) -> list[ReferenceTableDTO]:
        student_evaluation_id = self.get_student_evaluation_id(student_id=student_id, evaluation_id=evaluation_id)

        with self._session_factory() as session:
            db_record = self._student_evaluation_crud.get_by_id(session=session, record_id=student_evaluation_id)
            if not db_record:
                return []
            return [ReferenceTableDTO(reference_id=reference.id,
                                      student_reference=reference.student_reference,
                                      student_reference_html=reference.student_reference_html,
                                      cross_reference=reference.cross_reference,
                                      verification_status=reference.verification_status,
                                      relevance=reference.relevance,
                                      reference_type=reference.reference_type,
                                      evidence_level=reference.evidence_level,
                                      year=reference.year,
                                      url=reference.url,
                                      title=reference.title,
                                      peer_reviewed=reference.peer_reviewed) for reference in db_record.references]

    def get_excluded_urls(self, student_id: int | None, evaluation_ids: list[int] | None) -> list[str]:
        if student_id is None or evaluation_ids is None:
            return []

        with self._session_factory() as session:
            urls = self._student_evaluation_crud.get_urls_from_ids(session=session, student_id=student_id,
                                                                   evaluation_ids=evaluation_ids)
            return urls if urls else []

    def get_excluded_titles(self, student_id: int | None, evaluation_ids: list[int] | None) -> list[str]:
        if student_id is None or evaluation_ids is None:
            return []

        with self._session_factory() as session:
            titles = self._student_evaluation_crud.get_titles_from_ids(session=session, student_id=student_id,
                                                                       evaluation_ids=evaluation_ids)
            return titles if titles else []

    def add_grade_from_name(self, update_grade_dtos: list[UpdateGradeDTO]):
        with self._session_factory.begin() as session:
            for upgrade_dto in update_grade_dtos:
                self._student_evaluation_crud.add_grade_from_name(session=session,
                                                                  evaluation_id=upgrade_dto.evaluation_id,
                                                                  first_name=upgrade_dto.first_name,
                                                                  last_name=upgrade_dto.last_name,
                                                                  grade=upgrade_dto.grade)

    def get_grade_reference_plot_dto(self, evaluation_id: int, active_student_ids: list[int]) -> GradeReferencePlotDTO:
        with self._session_factory() as session:
            db_records = self._student_evaluation_crud.list_evaluation_grades_references(
                session=session, evaluation_id=evaluation_id, active_student_ids=active_student_ids)

            return GradeReferencePlotDTO(
                bins=self._extract_student_names(db_records=db_records),
                grades=self._extract_grades(db_records=db_records),
                grey_counts=self._extract_grey_literature_counts(db_records=db_records),
                scientific_no_review_counts=self._extract_scientific_no_review_counts(db_records=db_records),
                scientific_review_counts=self._extract_scientific_review_literature_counts(db_records=db_records))

    @staticmethod
    def _extract_student_names(db_records: list[StudentEvaluationORM]) -> list[str]:
        return [f"{db_record.student.last_name}, {db_record.student.first_name}" for db_record in db_records]

    @staticmethod
    def _extract_grades(db_records: list[StudentEvaluationORM]) -> list[float | int]:
        maximum_grade = db_records[0].evaluation.maximum_grade

        grades = [float(round((db_record.grade / maximum_grade) * 100, 2))
                  if db_record.grade is not None and maximum_grade else 0.0
                  for db_record in db_records]

        return grades

    @staticmethod
    def _extract_grey_literature_counts(db_records: list[StudentEvaluationORM]) -> list[int]:
        return [sum(ref.reference_type == ReferenceTypeEnum.GREY for ref in (db_record.references or []))
                for db_record in db_records]

    @staticmethod
    def _extract_scientific_no_review_counts(db_records: list[StudentEvaluationORM]) -> list[int]:
        return [
            sum(ref.reference_type == ReferenceTypeEnum.SCIENTIFIC_NO_REVIEW for ref in (db_record.references or []))
            for db_record in db_records]

    @staticmethod
    def _extract_scientific_review_literature_counts(db_records: list[StudentEvaluationORM]) -> list[int]:
        return [
            sum(ref.reference_type == ReferenceTypeEnum.SCIENTIFIC_PEER_REVIEW for ref in (db_record.references or []))
            for db_record in db_records]