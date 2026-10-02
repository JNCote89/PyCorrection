from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.py_correction.core.domains.shared.shared_enums import ImportTypeEnum
from src.py_correction.database.base.base_model import AutoPathType, BaseORM, LocalDateTime

if TYPE_CHECKING:
    from src.py_correction.database.course.models.course_orm import CourseORM
    from src.py_correction.database.student.models.student_evaluation_orm import StudentEvaluationORM


class EvaluationORM(BaseORM):
    __tablename__ = "evaluations"

    # --- Keys ---
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)

    # --- Columns ---
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    maximum_grade: Mapped[Decimal] = mapped_column(Numeric(precision=5, scale=2), nullable=False)
    import_type: Mapped[ImportTypeEnum] = mapped_column(nullable=False)
    updated_at: Mapped[datetime] = mapped_column(LocalDateTime, onupdate=datetime.now, nullable=True)

    # Excel configurations
    template_file_path: Mapped[Path | None] = mapped_column(AutoPathType(1024), default=None, nullable=True)
    template_filename: Mapped[str | None] = mapped_column(String(256), default=None, nullable=True)
    template_sheet_name: Mapped[str | None] = mapped_column(String(256), default=None, nullable=True)
    template_row_keyword: Mapped[str | None] = mapped_column(String(256), default=None, nullable=True)
    template_column_keyword: Mapped[str | None] = mapped_column(String(256), default=None, nullable=True)

    # --- Relationships ---
    course: Mapped["CourseORM"] = relationship("CourseORM", back_populates="evaluations")
    student_evaluations: Mapped[list["StudentEvaluationORM"]] = relationship("StudentEvaluationORM",
                                                                             back_populates="evaluation",
                                                                             cascade="all, delete-orphan")
