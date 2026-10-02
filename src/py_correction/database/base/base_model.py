from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import DateTime, Dialect, String, TypeDecorator
from sqlalchemy.orm import DeclarativeBase


class AutoPathType(TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect: Dialect):
        if value is not None:
            return str(value)
        return value

    def process_result_value(self, value: str | None, dialect: Dialect):
        if value is not None:
            return Path(str(value))
        return value


class LocalDateTime(TypeDecorator[datetime]):
    """Stores as UTC in the DB, but retrieves as system local time in Python."""

    impl = DateTime(timezone=True)
    cache_ok = True

    def process_result_value(self, value: datetime | None, dialect: Dialect) -> datetime | None:
        if value is not None:
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)

            return value.astimezone()
        return value

    def process_bind_param(self, value: datetime | None, dialect: Dialect) -> datetime | None:
        if value is not None:
            if value.tzinfo is None:
                value = value.astimezone()

            return value.astimezone(timezone.utc)
        return value


class BaseORM(DeclarativeBase):
    type_annotation_map = {Path: AutoPathType, }
