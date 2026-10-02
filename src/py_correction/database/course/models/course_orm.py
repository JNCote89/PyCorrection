from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.py_correction.core.domains.shared.shared_enums import ImportTypeEnum
from src.py_correction.database.base.base_model import BaseORM, LocalDateTime

if TYPE_CHECKING:
    from src.py_correction.database.course_path.models.course_path_orm import CoursePathORM
    from src.py_correction.database.evaluation.models.evaluation_orm import EvaluationORM
    from src.py_correction.database.course.models.course_student_orm import CourseStudentORM


class CourseORM(BaseORM):
    __tablename__ = "courses"

    # --- Keys ---
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # --- Columns ---
    semester: Mapped[str] = mapped_column(String(5), nullable=False)
    code: Mapped[str] = mapped_column(String(6), nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    group: Mapped[str] = mapped_column(String(2), nullable=False)
    genote_filename: Mapped[str] = mapped_column(String(256), nullable=True)
    import_type: Mapped[ImportTypeEnum] = mapped_column(String(64), nullable=False)
    creation_date: Mapped[datetime] = mapped_column(LocalDateTime, nullable=False)

    # --- Relationships ---
    course_path: Mapped["CoursePathORM"] = relationship("CoursePathORM", back_populates="course",
                                                        cascade="all, delete-orphan")
    evaluations: Mapped[list["EvaluationORM"]] = relationship("EvaluationORM",
                                                              back_populates="course",
                                                              cascade="all, delete-orphan")
    course_students: Mapped[list["CourseStudentORM"]] = relationship("CourseStudentORM",
                                                                     back_populates="course",
                                                                     cascade="all, delete-orphan")

    # --- Constraints ---
    __table_args__ = (UniqueConstraint("semester", "code", "name", "group", name="unique_course_entry"),)
