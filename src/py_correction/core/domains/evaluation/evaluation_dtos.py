from dataclasses import dataclass, field, fields
from decimal import Decimal
from pathlib import Path

from src.py_correction.core.domains.shared.shared_enums import ImportTypeEnum, UNSET


@dataclass(frozen=True, slots=True)
class EvaluationCreateDTO:
    title: str
    maximum_grade: Decimal | None
    import_type: ImportTypeEnum


@dataclass(frozen=True, slots=True)
class EvaluationResponseDTO:
    id: int
    title: str
    maximum_grade: Decimal
    import_type: ImportTypeEnum
    template_file_path: Path | None = None
    template_filename: str | None = None
    template_sheet_name: str | None = None
    template_row_keyword: str | None = None
    template_column_keyword: str | None = None


@dataclass
class EvaluationUpdateDTO:
    id: int = field(metadata={"updatable": False})
    # At the moment, to avoid disconnection with GeNote, update are only allowed on the configurations
    # for the Excel template.
    template_file_path: Path | str | None | object = field(default=UNSET, metadata={"updatable": True})
    template_filename: str | None | object = field(default=UNSET, metadata={"updatable": True})
    template_sheet_name: str | None | object = field(default=UNSET, metadata={"updatable": True})
    template_row_keyword: str | None | object = field(default=UNSET, metadata={"updatable": True})
    template_column_keyword: str | None | object = field(default=UNSET, metadata={"updatable": True})

    def updatable_items_to_dict(self) -> dict:
        updatable_fields = [f.name for f in fields(self) if f.metadata["updatable"] is not False]
        return {k: v for k, v in self.__dict__.items() if k in updatable_fields and v is not UNSET}


@dataclass(frozen=True, slots=True)
class EvaluationTemplateCompletedResponseDTO:
    original_path: Path
    template_directory: Path


@dataclass(frozen=True, slots=True)
class EvaluationTemplateResponseDTO:
    filename: str | None
    template_sheet: str | None
    row_keyword: str | None
    column_keyword: str | None
    evaluation_title: str | None