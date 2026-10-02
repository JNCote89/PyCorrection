from typing import TYPE_CHECKING

from sqlalchemy import delete, select, update

from src.py_correction.database.base.base_CRUD import BaseCRUD
from src.py_correction.database.reference.models.reference_orm import ReferenceORM

if TYPE_CHECKING:
    from sqlalchemy.orm import Session
    from src.py_correction.core.domains.reference.reference_dtos import ReferenceUpdateDTO


class ReferenceCRUD(BaseCRUD[ReferenceORM]):
    model = ReferenceORM

    def update_reference(self, session: "Session", reference_update_dto: "ReferenceUpdateDTO") -> None:
        stmt = select(self.model).where(self.model.id == reference_update_dto.reference_id)
        db_record = session.scalars(stmt).first()
        if db_record:
            self._update_from_dto(db_record=db_record, update_dto=reference_update_dto)

    def delete_reference_by_relationship(self, session: "Session", student_evaluation_id: int) -> None:
        stmt = delete(self.model).where(self.model.student_evaluation_id == student_evaluation_id)
        session.execute(stmt)

    def get_references_by_relationship(self, session: "Session", student_evaluation_id: int) -> list[ReferenceORM]:
        stmt = select(self.model).where(self.model.student_evaluation_id == student_evaluation_id)
        db_records = session.scalars(stmt).all()
        return list(db_records)

    def bulk_update_references(self, session: "Session", bulk_update_data: list[dict]):
        session.execute(update(self.model), bulk_update_data)
