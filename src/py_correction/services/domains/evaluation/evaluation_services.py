from pathlib import Path
from typing import TYPE_CHECKING

from src.py_correction.core.domains.evaluation.evaluation_dtos import (EvaluationCreateDTO, EvaluationResponseDTO,
                                                                       EvaluationTemplateResponseDTO,
                                                                       EvaluationUpdateDTO)
from src.py_correction.core.domains.shared.shared_dtos import SelectionWidgetDTO
from src.py_correction.core.domains.shared.shared_enums import AutofillOptions
from src.py_correction.database.evaluation.evaluation_CRUD import EvaluationCRUD
from src.py_correction.services.domains.evaluation.evaluation_mappers import (to_evaluation_orm,
                                                                              to_evaluation_response_dto,
                                                                              to_evaluation_selection_dto)

if TYPE_CHECKING:
    from sqlalchemy.orm import sessionmaker
    from src.py_correction.core.event_bus import EventBus


class EvaluationServices:

    # Throw an error
    def __init__(self, session_factory: "sessionmaker", event_bus: "EventBus"):
        self._session_factory = session_factory
        self._evaluation_crud = EvaluationCRUD()

        self._event_bus = event_bus

    def add_evaluation_from_dto(self, evaluation_create_dto: EvaluationCreateDTO, course_id: int) -> None:
        self.add_evaluation_from_dtos(evaluation_create_dtos=[evaluation_create_dto], course_id=course_id)

    def add_evaluation_from_dtos(self, evaluation_create_dtos: list[EvaluationCreateDTO], course_id: int) -> None:
        evaluation_orm_lists = [to_evaluation_orm(evaluation_input_dto=dto, course_id=course_id)
                                for dto in evaluation_create_dtos]

        with self._session_factory.begin() as session:
            session.add_all(evaluation_orm_lists)

        self._event_bus.evaluation.dataChanged.emit()

    def update_evaluation(self, evaluation_update_dto: EvaluationUpdateDTO) -> None:
        if evaluation_update_dto.id:
            with self._session_factory.begin() as session:
                self._evaluation_crud.update_evaluation(session=session, evaluation_update_dto=evaluation_update_dto)

    def list_evaluation_selection_dtos(self, course_id: int) -> list[SelectionWidgetDTO]:
        with self._session_factory() as session:
            evaluation_orm_records = self._evaluation_crud.list_evaluation_records(session, course_id=course_id)
            if evaluation_orm_records is None:
                return []
            return [to_evaluation_selection_dto(evaluation) for evaluation in evaluation_orm_records]

    def get_evaluation_response_dto(self, evaluation_id: int) -> EvaluationResponseDTO | None:
        with self._session_factory() as session:
            evaluation_orm_record = self._evaluation_crud.get_evaluation(session, evaluation_id)
            if evaluation_orm_record is None:
                return None
            return to_evaluation_response_dto(evaluation_orm=evaluation_orm_record)

    def get_evaluation_title(self, evaluation_id: int) -> str | None:
        with self._session_factory() as session:
            evaluation = self._evaluation_crud.get_evaluation(session, evaluation_id)
            return evaluation.title if evaluation is not None else None

    def get_evaluation_template_dto(self, evaluation_id: int) -> EvaluationTemplateResponseDTO | None:
        with self._session_factory() as session:
            evaluation_orm = self._evaluation_crud.get_by_id(session=session, record_id=evaluation_id)
            if evaluation_orm:
                return EvaluationTemplateResponseDTO(filename=evaluation_orm.template_filename,
                                                     template_sheet=evaluation_orm.template_sheet_name,
                                                     row_keyword=evaluation_orm.template_row_keyword,
                                                     column_keyword=evaluation_orm.template_column_keyword,
                                                     evaluation_title=evaluation_orm.title)
            return None


    def get_evaluation_template_filename(self, evaluation_id: int) -> str | None:
        with self._session_factory() as session:
            evaluation = self._evaluation_crud.get_evaluation(session, evaluation_id)
            return evaluation.template_filename if evaluation is not None else None

    def get_evaluation_template_file_path(self, evaluation_id: int) -> Path | None:
        with self._session_factory() as session:
            evaluation = self._evaluation_crud.get_evaluation(session, evaluation_id)
            return evaluation.template_file_path if evaluation is not None else None

    def get_current_template_selection(self, evaluation_record: EvaluationResponseDTO | None,
                                       autofill_option: AutofillOptions | None) -> Path | None:
        if evaluation_record is None:
            return None

        elif evaluation_record.template_file_path:
            return evaluation_record.template_file_path

        elif autofill_option == AutofillOptions.LAST_ENTRY:
            with self._session_factory() as session:
                previous_record = self._evaluation_crud.get_last_template(
                    session=session, evaluation_id=evaluation_record.id, evaluation_title=evaluation_record.title)
                return previous_record

        elif autofill_option == AutofillOptions.MOST_FREQUENT:
            with self._session_factory() as session:
                most_frequent_record = self._evaluation_crud.get_most_frequent_template(
                    session=session, evaluation_id=evaluation_record.id, evaluation_title=evaluation_record.title)
                return most_frequent_record
        else:
            return None

    def get_current_sheet_selection(self, evaluation_record: EvaluationResponseDTO | None,
                                    autofill_option: AutofillOptions | None) -> str | None:
        if evaluation_record is None or evaluation_record.template_filename is None:
            return None

        elif evaluation_record.template_sheet_name:
            return evaluation_record.template_sheet_name

        elif autofill_option == AutofillOptions.LAST_ENTRY:
            with self._session_factory() as session:
                previous_record = self._evaluation_crud.get_last_sheet(
                    session=session, evaluation_id=evaluation_record.id, evaluation_title=evaluation_record.title,
                    template_filename=evaluation_record.template_filename)
                return previous_record

        elif autofill_option == AutofillOptions.MOST_FREQUENT:
            with self._session_factory() as session:
                most_frequent_record = self._evaluation_crud.get_most_frequent_sheet(
                    session=session, evaluation_id=evaluation_record.id, evaluation_title=evaluation_record.title,
                    template_filename=evaluation_record.template_filename)
                return most_frequent_record
        else:
            return None

    def get_current_row_keyword_selection(self, evaluation_record: EvaluationResponseDTO | None,
                                          autofill_option: AutofillOptions | None) -> str | None:
        if evaluation_record is None or evaluation_record.template_filename is None:
            return None

        elif evaluation_record.template_row_keyword:
            return evaluation_record.template_row_keyword

        elif autofill_option == AutofillOptions.LAST_ENTRY:
            with self._session_factory() as session:
                previous_record = self._evaluation_crud.get_last_row_keyword(
                    session=session, evaluation_id=evaluation_record.id,
                    evaluation_filename=evaluation_record.template_filename)
                return previous_record

        elif autofill_option == AutofillOptions.MOST_FREQUENT:
            with self._session_factory() as session:
                most_frequent_record = self._evaluation_crud.get_most_frequent_row_keyword(
                    session=session, evaluation_id=evaluation_record.id,
                    evaluation_filename=evaluation_record.template_filename)
                return most_frequent_record
        else:
            return None

    def get_current_column_keyword_selection(self, evaluation_record: EvaluationResponseDTO | None,
                                             autofill_option: AutofillOptions | None) -> str | None:
        if evaluation_record is None or evaluation_record.template_filename is None:
            return None

        elif evaluation_record.template_column_keyword:
            return evaluation_record.template_column_keyword

        elif autofill_option == AutofillOptions.LAST_ENTRY:
            with self._session_factory() as session:
                previous_record = self._evaluation_crud.get_last_column_keyword(
                    session=session, evaluation_id=evaluation_record.id,
                    evaluation_filename=evaluation_record.template_filename)
                return previous_record

        elif autofill_option == AutofillOptions.MOST_FREQUENT:
            with self._session_factory() as session:
                most_frequent_record = self._evaluation_crud.get_most_frequent_column_keyword(
                    session=session, evaluation_id=evaluation_record.id,
                    evaluation_filename=evaluation_record.template_filename)
                return most_frequent_record
        else:
            return None
