from typing import Any, Protocol, TYPE_CHECKING

from sqlalchemy import select

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class HasUpdatableItemsToDict(Protocol):

    def updatable_items_to_dict(self) -> dict:
        ...


class BaseCRUD[ModelType]:
    model: type[ModelType]

    def get_by_id(self, session: "Session", record_id: int | None) -> ModelType | None:
        stmt = select(self.model).where(self.model.id == record_id)
        return session.scalar(stmt)

    @staticmethod
    def _update_from_dto(db_record: Any, update_dto: HasUpdatableItemsToDict) -> None:
        for field_name, value in update_dto.updatable_items_to_dict().items():
            if hasattr(db_record, field_name):
                setattr(db_record, field_name, value)
