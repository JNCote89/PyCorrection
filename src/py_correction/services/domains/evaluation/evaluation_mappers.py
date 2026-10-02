from src.py_correction.core.domains.evaluation.evaluation_dtos import EvaluationCreateDTO, EvaluationResponseDTO
from src.py_correction.core.domains.shared.shared_dtos import SelectionWidgetDTO
from src.py_correction.database.evaluation.models.evaluation_orm import EvaluationORM


def to_evaluation_orm(evaluation_input_dto: EvaluationCreateDTO, course_id: int) -> EvaluationORM:
    return EvaluationORM(title=evaluation_input_dto.title,  # type: ignore
                         maximum_grade=evaluation_input_dto.maximum_grade,  # type: ignore
                         import_type=evaluation_input_dto.import_type,  # type: ignore
                         course_id=course_id)  # type: ignore


def to_evaluation_selection_dto(evaluation_orm: EvaluationORM):
    return SelectionWidgetDTO(id=evaluation_orm.id, label=evaluation_orm.title)


def to_evaluation_response_dto(evaluation_orm: EvaluationORM):
    return EvaluationResponseDTO(id=evaluation_orm.id,
                                 title=evaluation_orm.title,
                                 maximum_grade=evaluation_orm.maximum_grade,
                                 import_type=evaluation_orm.import_type,
                                 template_file_path=evaluation_orm.template_file_path,
                                 template_filename=evaluation_orm.template_filename,
                                 template_sheet_name=evaluation_orm.template_sheet_name,
                                 template_row_keyword=evaluation_orm.template_row_keyword,
                                 template_column_keyword=evaluation_orm.template_column_keyword)
