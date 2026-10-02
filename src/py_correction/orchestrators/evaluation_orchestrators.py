import logging
from pathlib import Path
from typing import TYPE_CHECKING

from src.py_correction.core.domains.shared.shared_dtos import ComboBoxPayload
from src.py_correction.engine.excel.excel_operations import (exclude_duplicate_keyword, get_excel_sheet_keyword_options,
                                                             get_excel_sheet_names)
from src.py_correction.ui.components.payload_builders import template_payloads

if TYPE_CHECKING:
    from src.py_correction.core.settings_manager import SettingsManager
    from src.py_correction.services.domains.course.course_services import CourseServices
    from src.py_correction.services.domains.course_path.course_path_services import CoursePathServices
    from src.py_correction.services.domains.evaluation.evaluation_services import EvaluationServices

logger = logging.getLogger(__name__)


class EvaluationOrchestrator:

    def __init__(self, settings_manager: "SettingsManager", course_services: "CourseServices",
                 evaluation_services: "EvaluationServices", course_path_services: "CoursePathServices"):
        self._settings_manager = settings_manager
        self._course_services = course_services
        self._evaluation_services = evaluation_services
        self._course_path_services = course_path_services

    def get_template_file_combo_box_payload(self, evaluation_id: int, course_id: int) -> ComboBoxPayload[Path | None]:
        evaluation_record = self._evaluation_services.get_evaluation_response_dto(evaluation_id=evaluation_id)

        template_path_items = self._course_path_services.scan_evaluation_template_paths_directory(course_id=course_id)
        current_data_selection = self._evaluation_services.get_current_template_selection(
            evaluation_record=evaluation_record,
            autofill_option=self._settings_manager.restored_settings.evaluation_autofill_option)

        return template_payloads.get_template_combo_box_payload(current_data_selection=current_data_selection,
                                                                items=template_path_items)

    def get_sheet_name_combo_box_payload(self, template_file_path: Path | None, evaluation_id: int
                                         ) -> ComboBoxPayload[str | None]:
        sheet_name_items = get_excel_sheet_names(excel_path=template_file_path)

        evaluation_record = self._evaluation_services.get_evaluation_response_dto(evaluation_id=evaluation_id)

        current_data_selection = self._evaluation_services.get_current_sheet_selection(
            evaluation_record=evaluation_record,
            autofill_option=self._settings_manager.restored_settings.evaluation_autofill_option)

        return template_payloads.get_sheet_combo_box_payload(current_data_selection=current_data_selection,
                                                             items=sheet_name_items)

    def get_row_keyword_combo_box_payload(self, template_file_path: Path | None, template_sheet_name: str | None,
                                          evaluation_id: int) -> ComboBoxPayload[str | None]:
        keyword_option_items = get_excel_sheet_keyword_options(excel_path=template_file_path,
                                                               sheet_name=template_sheet_name)

        evaluation_record = self._evaluation_services.get_evaluation_response_dto(evaluation_id=evaluation_id)

        current_data_selection = self._evaluation_services.get_current_row_keyword_selection(
            evaluation_record=evaluation_record,
            autofill_option=self._settings_manager.restored_settings.evaluation_autofill_option)

        return template_payloads.get_row_keyword_combo_box_payload(current_data_selection=current_data_selection,
                                                                   items=keyword_option_items)

    def get_column_keyword_combo_box_payload(self, template_file_path: Path | None, template_sheet_name: str | None,
                                             template_row_keyword: str | None, evaluation_id: int
                                             ) -> ComboBoxPayload[str | None]:
        keyword_option_items = get_excel_sheet_keyword_options(excel_path=template_file_path,
                                                               sheet_name=template_sheet_name)

        column_keyword_option_items = exclude_duplicate_keyword(row_keyword=template_row_keyword,
                                                                keywords=keyword_option_items)

        evaluation_record = self._evaluation_services.get_evaluation_response_dto(evaluation_id=evaluation_id)

        current_data_selection = self._evaluation_services.get_current_column_keyword_selection(
            evaluation_record=evaluation_record,
            autofill_option=self._settings_manager.restored_settings.evaluation_autofill_option)

        return template_payloads.get_column_keyword_combo_box_payload(
            current_data_selection=current_data_selection,
            items=column_keyword_option_items,
            no_row_is_selected=not bool(template_row_keyword))
