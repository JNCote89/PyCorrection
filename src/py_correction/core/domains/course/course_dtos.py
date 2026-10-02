from dataclasses import dataclass, field, fields
from datetime import datetime
from enum import StrEnum

from src.py_correction.core.domains.shared.shared_enums import ImportTypeEnum


@dataclass(frozen=True, slots=True)
class CourseCreateDTO:
    semester: str
    code: str
    name: str
    group: str
    genote_filename: str | None
    import_type: ImportTypeEnum
    creation_date: datetime


@dataclass(frozen=True, slots=True)
class CourseResponseDTO:
    id: int
    semester: str
    code: str
    name: str
    group: str
    import_type: ImportTypeEnum
    creation_date: datetime


@dataclass(slots=True)
class CourseTableDTO:
    # To easily check the field name inside the GUI to format the date
    class Fields(StrEnum):
        CREATION_DATE = "creation_date"

    semester: str = field(metadata={"label": "Semestre", "visible": True})
    code: str = field(metadata={"label": "Sigle du cours", "visible": True})
    name: str = field(metadata={"label": "Nom du cours", "visible": True})
    group: str = field(metadata={"label": "Groupe", "visible": True})
    import_type: str = field(metadata={"label": "Type d'importation", "visible": True})
    creation_date: datetime = field(metadata={"label": "Date de création", "visible": True})

    @classmethod
    def get_headers(cls):
        return [f.metadata["label"] for f in fields(cls) if f.metadata["visible"] is True]

    @classmethod
    def get_field_names(cls):
        return [f.name for f in fields(cls) if f.metadata["visible"] is True]


@dataclass(slots=True)
class CourseSelectionWidgetDTO:
    """Require a specific selection DTO to set up the QSortFilterProxyModel"""
    id: int
    semester: str
    code: str
    group: str
    name: str
