from decimal import Decimal
import logging

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from src.py_correction.database.base.base_CRUD import BaseCRUD
from src.py_correction.database.reference.models.reference_orm import ReferenceORM
from src.py_correction.database.student.models.student_evaluation_orm import StudentEvaluationORM
from src.py_correction.database.student.models.student_orm import StudentORM

logger = logging.getLogger(__name__)

class StudentEvaluationCRUD(BaseCRUD[StudentEvaluationORM]):
    model = StudentEvaluationORM

    def get_id_by_foreign_key(self, session: "Session", evaluation_id: int, student_id: int) -> int:
        stmt = select(self.model.id).where(self.model.evaluation_id == evaluation_id,
                                           self.model.student_id == student_id)
        record_id = session.scalars(stmt).first()
        if record_id:
            return record_id # type: ignore[arg-type]

        new_record = self.model(evaluation_id=evaluation_id, student_id=student_id) # type: ignore[call-arg]
        session.add(new_record)
        session.flush()

        return new_record.id

    def get_titles_from_ids(self, session: "Session", student_id: int, evaluation_ids: list[int]) -> list[str] | None:
        stmt = select(ReferenceORM.title).join(ReferenceORM.student_evaluation
                                               ).where(self.model.student_id == student_id,
                                                       self.model.evaluation_id.in_(evaluation_ids),
                                                       ReferenceORM.title.isnot(None))
        titles = session.scalars(stmt).all()
        return list(titles) if titles else None

    def get_urls_from_ids(self, session: "Session", student_id: int, evaluation_ids: list[int]) -> list[str] | None:
        stmt = select(ReferenceORM.url).join(ReferenceORM.student_evaluation
                                             ).where(self.model.student_id == student_id,
                                                     self.model.evaluation_id.in_(evaluation_ids),
                                                     ReferenceORM.url.isnot(None))
        urls = session.scalars(stmt).all()
        return list(urls) if urls else None

    def add_grade_from_name(self, session: Session, evaluation_id: int, first_name: str, last_name: str,
                            grade: Decimal | None):
        stmt = select(self.model).join(self.model.student).where(
            self.model.evaluation_id == evaluation_id,
            StudentORM.first_name == first_name,
            StudentORM.last_name == last_name)

        matches = session.scalars(stmt).all()

        if len(matches) > 1:
            logger.warning(f"Ambiguity error: Multiple students named '{first_name} {last_name}' "
                             f"are already linked to evaluation {evaluation_id}.")

        if matches:
            student_evaluation_record = matches[0]
            student_evaluation_record.grade = grade
        else:
            student_stmt = select(StudentORM).where(
                StudentORM.first_name == first_name,
                StudentORM.last_name == last_name)

            students = session.scalars(student_stmt).all()

            if not students:
                logging.warning(f"Student '{first_name} {last_name}' does not exist.")
            if len(students) > 1:
                logging.warning(f"""Ambiguity error: Found {len(students)} students named '{first_name} {last_name}' 
                                     in the database. Cannot safely assign grade without a unique identifier.""")

            student_evaluation_record = StudentEvaluationORM(student_id=students[0].id, evaluation_id=evaluation_id, # type: ignore[call-arg]
                                                             grade=grade) # type: ignore[call-arg]
            session.add(student_evaluation_record)

    def list_evaluation_grades_references(self, session: Session, evaluation_id: int,
                                          active_student_ids: list[int]) -> list[StudentEvaluationORM]:
        stmt = select(self.model).options(selectinload(self.model.student),
                                          selectinload(self.model.references),
                                          selectinload(self.model.evaluation),
                                          ).where(self.model.evaluation_id == evaluation_id,
                                                  self.model.student_id.in_(active_student_ids),
                                                  ).order_by(self.model.grade.desc())

        return session.scalars(stmt).all() # type: ignore[arg-type]
