from pathlib import Path
from typing import TYPE_CHECKING

from sqlalchemy import func, select

from src.py_correction.database.base.base_CRUD import BaseCRUD
from src.py_correction.database.evaluation.models.evaluation_orm import EvaluationORM

if TYPE_CHECKING:
    from sqlalchemy.orm import Session
    from src.py_correction.core.domains.evaluation.evaluation_dtos import EvaluationUpdateDTO


class EvaluationCRUD(BaseCRUD[EvaluationORM]):
    model = EvaluationORM

    def list_evaluation_records(self, session: "Session", course_id: int) -> list[EvaluationORM]:
        stmt = select(self.model).where(self.model.course_id == course_id)
        evaluations = session.scalars(stmt).all()
        return [row for row in evaluations] if evaluations is not None else []

    def get_evaluation(self, session: "Session", evaluation_id: int) -> EvaluationORM | None:
        stmt = select(self.model).where(self.model.id == evaluation_id)
        evaluation = session.scalar(stmt)
        return evaluation

    def update_evaluation(self, session: "Session", evaluation_update_dto: "EvaluationUpdateDTO"):
        db_record = session.get(self.model, evaluation_update_dto.id)
        if db_record:
            self._update_from_dto(db_record=db_record, update_dto=evaluation_update_dto)

    def get_last_template(self, session: "Session", evaluation_id: int, evaluation_title: str) -> Path | None:
        stmt = select(self.model.template_file_path
                      ).where(self.model.id != evaluation_id,
                              self.model.template_file_path.isnot(None),
                              self.model.title == evaluation_title
                              ).order_by(self.model.updated_at.desc())

        return session.scalars(stmt).first()

    def get_most_frequent_template(self, session: "Session", evaluation_id: int, evaluation_title: str) -> Path | None:
        stmt = select(self.model.template_file_path
                      ).where(self.model.id != evaluation_id,
                              self.model.template_file_path.isnot(None),
                              self.model.title == evaluation_title
                              ).group_by(self.model.template_file_path
                                         ).order_by(func.count(self.model.template_filename).desc(),
                                                    self.model.updated_at.desc())
        return session.scalars(stmt).first()

    def get_last_sheet(self, session: "Session", evaluation_id: int, evaluation_title: str,
                       template_filename: str) -> str | None:
        stmt = select(self.model.template_sheet_name
                      ).where(self.model.id != evaluation_id,
                              self.model.template_sheet_name.isnot(None),
                              self.model.title == evaluation_title,
                              self.model.template_filename == template_filename
                              ).order_by(self.model.updated_at.desc())
        return session.scalars(stmt).first()

    def get_most_frequent_sheet(self, session: "Session", evaluation_id: int, evaluation_title: str,
                                template_filename: str) -> str | None:
        stmt = select(self.model.template_sheet_name
                      ).where(self.model.id != evaluation_id,
                              self.model.template_sheet_name.isnot(None),
                              self.model.title == evaluation_title,
                              self.model.template_filename == template_filename
                              ).group_by(self.model.template_sheet_name
                                         ).order_by(func.count(self.model.template_sheet_name).desc(),
                                                    self.model.updated_at.desc())
        return session.scalars(stmt).first()

    def get_last_row_keyword(self, session: "Session", evaluation_id: int, evaluation_filename: str) -> str | None:
        stmt = select(self.model.template_row_keyword
                      ).where(self.model.id != evaluation_id,
                              self.model.template_row_keyword.isnot(None),
                              self.model.template_filename == evaluation_filename
                              ).order_by(self.model.updated_at.desc())
        return session.scalars(stmt).first()

    def get_most_frequent_row_keyword(self, session: "Session", evaluation_id: int,
                                      evaluation_filename: str) -> str | None:
        stmt = select(self.model.template_row_keyword
                      ).where(self.model.id != evaluation_id,
                              self.model.template_row_keyword.isnot(None),
                              self.model.template_filename == evaluation_filename
                              ).group_by(self.model.template_row_keyword
                                         ).order_by(func.count(self.model.template_row_keyword).desc(),
                                                    self.model.updated_at.desc())
        return session.scalars(stmt).first()

    def get_last_column_keyword(self, session: "Session", evaluation_id: int,
                                evaluation_filename: str) -> str | None:
        stmt = (select(self.model.template_column_keyword
                       ).where(self.model.id != evaluation_id,
                               self.model.template_column_keyword.isnot(None),
                               self.model.template_filename == evaluation_filename,
                               ).order_by(self.model.updated_at.desc()))
        return session.scalars(stmt).first()

    def get_most_frequent_column_keyword(self, session: "Session", evaluation_id: int,
                                         evaluation_filename: str) -> str | None:
        stmt = select(self.model.template_column_keyword
                      ).where(self.model.id != evaluation_id,
                              self.model.template_column_keyword.isnot(None),
                              self.model.template_filename == evaluation_filename
                              ).group_by(self.model.template_column_keyword
                                         ).order_by(func.count(self.model.template_column_keyword).desc(),
                                                    self.model.updated_at.desc())
        return session.scalars(stmt).first()
