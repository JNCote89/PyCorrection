import logging

from sqlalchemy import URL, create_engine
from sqlalchemy.orm import Session, selectinload

from src.py_correction.core.logger import DEBUG_DB_MODE
from src.py_correction.database.base.base_model import BaseORM
from src.py_correction.database.course.models.course_orm import CourseORM
from src.py_correction.database.evaluation.models.evaluation_orm import EvaluationORM
from src.py_correction.database.student.models.student_evaluation_orm import StudentEvaluationORM

logger = logging.getLogger(__name__)


class ArchiveCourseCRUD:

    @staticmethod
    def archive_course(main_session: Session, course_id: int, archive_database_path: str) -> None:
        archive_sql_url = URL.create("sqlite", database=str(archive_database_path))
        archive_engine = create_engine(archive_sql_url, echo=DEBUG_DB_MODE)
        BaseORM.metadata.create_all(bind=archive_engine)

        course = main_session.query(
            CourseORM).options(selectinload(CourseORM.course_path),
                               selectinload(CourseORM.course_students),
                               selectinload(CourseORM.evaluations
                                            ).selectinload(EvaluationORM.student_evaluations
                                                           ).selectinload(StudentEvaluationORM.references),
                               ).filter(CourseORM.id == course_id).first()

        if not course:
            logger.warning(f"Course {course_id} not found.")

        with Session(archive_engine) as archive_session:
            archive_session.merge(course)
            archive_session.commit()

        main_session.delete(course)

    @staticmethod
    def restore_course(main_session: Session, archive_database_path: str) -> CourseORM | None:
        archive_sql_url = URL.create("sqlite", database=str(archive_database_path))
        archive_engine = create_engine(archive_sql_url, echo=DEBUG_DB_MODE)

        with Session(archive_engine) as archive_session:
            archived_course = archive_session.query(
                CourseORM).options(
                selectinload(CourseORM.course_path),
                selectinload(CourseORM.course_students),
                selectinload(CourseORM.evaluations).selectinload(EvaluationORM.student_evaluations
                                                                 ).selectinload(StudentEvaluationORM.references),
            ).first()

            if not archived_course:
                logging.warning(f"Course not found in archive.")

            archive_session.expunge_all()

        main_session.merge(archived_course)

        return archived_course
