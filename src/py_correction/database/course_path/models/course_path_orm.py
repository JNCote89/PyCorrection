from pathlib import Path
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.py_correction.database.base.base_model import AutoPathType, BaseORM

if TYPE_CHECKING:
    from src.py_correction.database.course.models.course_orm import CourseORM


class CoursePathORM(BaseORM):
    __tablename__ = "course_paths"

    # --- Keys ---
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)

    # --- Columns ---
    # Root
    user_root_directory: Mapped[Path] = mapped_column(AutoPathType(1024), nullable=False)
    course_root_path: Mapped[Path] = mapped_column(AutoPathType(1024), nullable=False)

    # Top-level directories
    corrections_directory: Mapped[Path] = mapped_column(AutoPathType(1024), nullable=False)
    correction_templates_directory: Mapped[Path] = mapped_column(AutoPathType(1024), nullable=False)
    grades_directory: Mapped[Path] = mapped_column(AutoPathType(1024), nullable=False)
    submissions_directory: Mapped[Path] = mapped_column(AutoPathType(1024), nullable=False)

    # Sub-directories
    submission_archives_directory: Mapped[Path] = mapped_column(AutoPathType(1024), nullable=False)
    correction_archives_directory: Mapped[Path] = mapped_column(AutoPathType(1024), nullable=False)

    # --- Relationships ---
    course: Mapped["CourseORM"] = relationship("CourseORM", back_populates="course_path")
