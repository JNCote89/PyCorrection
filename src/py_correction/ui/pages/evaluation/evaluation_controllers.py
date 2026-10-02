from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, override

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QApplication, QWidget

from src.py_correction.core import nuitka_helpers
from src.py_correction.core.dependency_injection import container
from src.py_correction.core.domains.evaluation.evaluation_dtos import EvaluationCreateDTO, EvaluationUpdateDTO
from src.py_correction.ui.components.base_components.base_controller import BaseController
from src.py_correction.ui.components.default_widgets.message_boxes import DefaultQuestionMessageBox
from src.py_correction.ui.components.payload_builders import template_payloads
from src.py_correction.ui.components.shared_components.course_selection.course_selection_controller import (
    CourseSelectionController)
from src.py_correction.ui.components.shared_components.workflow.workflow_mixin import ResetWorkflowMixin
from src.py_correction.ui.feedbacks.messages.confirmation_messages import FileOverwriteWarningMessage

if TYPE_CHECKING:
    from src.py_correction.ui.pages.evaluation.evaluation_page import EvaluationPage
    from src.py_correction.ui.pages.evaluation.evaluation_sections import (EvaluationFormImportCollapsibleSection,
                                                                       EvaluationManagementGroupBox,
                                                                       EvaluationTemplateImportGroupBox)


@dataclass
class EvaluationTransactionWorkflow(ResetWorkflowMixin):
    course_id: int | None = field(default=None)
    evaluation_id: int | None = field(default=None)

    evaluation_list_ids: list[int] = field(default_factory=list)

    template_file_path: Path | None = field(default=None)
    template_filename: str | None = field(default=None)
    template_sheet_name: str | None = field(default=None)
    template_row_keyword: str | None = field(default=None)
    template_column_keyword: str | None = field(default=None)


class EvaluationFormImportController(BaseController):
    manualSectionExpansionChanged = Signal(bool)

    evaluationImported = Signal(int)

    def __init__(self, section_view: "EvaluationFormImportCollapsibleSection",
                 workflow: EvaluationTransactionWorkflow, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._workflow = workflow
        self._section_view = section_view

        self._settings_manager = container.settings_manager()
        self._evaluation_services = container.evaluation_services()
        self._evaluation_orchestrator = container.evaluation_orchestrator()

        self._event_bus = container.event_bus()

        self._init_controller()

    @override
    def _connect_upstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._event_bus.settings.manualSectionExpansionChanged, slot=self._section_view.set_collapsible_section_state)

    @override
    def _connect_downstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._section_view.evaluationFormSubmitted, slot=self.import_evaluation_form)

    @override
    def _refresh_view(self) -> None:
        self._refresh_expandable_section()

    @Slot(EvaluationCreateDTO)
    def import_evaluation_form(self, evaluation: EvaluationCreateDTO) -> None:
        if self._workflow.course_id is not None:
            with QApplication.setOverrideCursor(Qt.CursorShape.BusyCursor):  # type: ignore[arg-type]
                self._evaluation_services.add_evaluation_from_dto(evaluation_create_dto=evaluation,
                                                                  course_id=self._workflow.course_id)
                self.evaluationImported.emit(self._workflow.course_id)
                self._event_bus.evaluation.formImportCompleted.emit(evaluation.title)

    def _refresh_expandable_section(self) -> None:
        section_state = self._settings_manager.restored_settings.manual_section_expansion_state
        self._section_view.set_collapsible_section_state(section_state)


class EvaluationTemplateImportController(BaseController):
    evaluationTemplateImported = Signal()

    def __init__(self, section_view: "EvaluationTemplateImportGroupBox", workflow: EvaluationTransactionWorkflow,
                 parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._workflow = workflow
        self._section_view = section_view

        self._settings_manager = container.settings_manager()
        self._course_path_services = container.course_path_services()
        self._evaluation_services = container.evaluation_services()
        self._evaluation_orchestrator = container.evaluation_orchestrator()

        self._event_bus = container.event_bus()

        self._init_controller()

    @override
    def _connect_upstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._event_bus.settings.userRootDirectoryChanged,
                                    slot=self._section_view.update_template_import_starting_directory)

    @override
    def _connect_downstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._section_view.evaluationTemplateFileSubmitted,
                                    slot=self._import_evaluation_template_file)

    @override
    def _refresh_view(self) -> None:
        self._refresh_template_import_widget()

    @Slot(Path)
    def _import_evaluation_template_file(self, file_path: Path) -> None:
        if self._workflow.course_id is not None:
            with QApplication.setOverrideCursor(Qt.CursorShape.BusyCursor):  # type: ignore
                file_already_imported = self._course_path_services.check_if_template_file_exists(
                    course_id=self._workflow.course_id, imported_file_path=file_path)

                if file_already_imported:
                    overwrite_message = FileOverwriteWarningMessage(
                        directory=file_already_imported, overwritten_filename=file_already_imported.name)

                    # The section view is needed to center the QMessageBox on the screen.
                    message_box = DefaultQuestionMessageBox(window_title=overwrite_message.title,
                                                            html_message=overwrite_message.html_text,
                                                            parent=self._section_view)
                    if not message_box.get_reply_bool():
                        return

                self._course_path_services.import_evaluation_file_template(template_file_path=file_path,
                                                                           course_id=self._workflow.course_id)
                self.evaluationTemplateImported.emit()

    def _refresh_template_import_widget(self) -> None:
        user_root_directory = self._settings_manager.restored_settings.user_root_directory
        self._section_view.update_template_import_starting_directory(starting_directory=user_root_directory)


class EvaluationManagementController(BaseController):

    def __init__(self, section_view: "EvaluationManagementGroupBox", workflow: EvaluationTransactionWorkflow,
                 parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._workflow = workflow
        self._section_view = section_view

        self._settings_manager = container.settings_manager()
        self._evaluation_services = container.evaluation_services()
        self._evaluation_orchestrator = container.evaluation_orchestrator()

        self._event_bus = container.event_bus()

        self._init_controller()

    @override
    def _connect_upstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._event_bus.settings.evaluationAutofillChanged,
                                    slot=self._section_view.set_evaluation_settings_group_box_title)
        nuitka_helpers.safe_connect(signal=self._event_bus.evaluation.dataChanged, slot=self._refresh_evaluation_list)

    @override
    def _connect_downstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._section_view.evaluationIDChanged,
                                    slot=self._handle_evaluation_id_changed)
        nuitka_helpers.safe_connect(signal=self._section_view.emptyListStatusChanged,
                                    slot=self._handle_empty_evaluation_list)

        nuitka_helpers.safe_connect(signal=self._section_view.templateFileSelectionChanged,
                                    slot=self._handle_evaluation_template_file_selection_changed)
        nuitka_helpers.safe_connect(signal=self._section_view.sheetNameSelectionChanged,
                                    slot=self._handle_evaluation_sheet_name_selection_changed)
        nuitka_helpers.safe_connect(signal=self._section_view.rowKeywordSelectionChanged,
                                    slot=self._handle_row_keyword_changed)
        nuitka_helpers.safe_connect(signal=self._section_view.columnKeywordSelectionChanged,
                                    slot=self._handle_column_keyword_changed)

    @override
    def _refresh_view(self) -> None:
        self._refresh_group_box_title()

    def update_evaluation_list_widget(self, course_id: int | None) -> None:
        if course_id is not None:
            self._workflow.course_id = course_id
            evaluation_selection_dtos = self._evaluation_services.list_evaluation_selection_dtos(
                course_id=course_id)

            evaluation_list_ids = [value.id for value in evaluation_selection_dtos]

            if evaluation_list_ids != self._workflow.evaluation_list_ids:
                self._workflow.evaluation_list_ids = evaluation_list_ids

                self._section_view.update_evaluation_list(evaluations=evaluation_selection_dtos)

    def update_template_file_combo_box(self) -> None:
        if self._workflow.course_id is not None and self._workflow.evaluation_id is not None:
            combo_box_payload = self._evaluation_orchestrator.get_template_file_combo_box_payload(
                evaluation_id=self._workflow.evaluation_id,
                course_id=self._workflow.course_id)

            self._section_view.populate_template_file_combo_box(payload=combo_box_payload)

    def _refresh_group_box_title(self) -> None:
        current_autofill_option = self._settings_manager.restored_settings.evaluation_autofill_option
        self._section_view.set_evaluation_settings_group_box_title(current_autofill_option)

    @Slot()
    def _refresh_evaluation_list(self) -> None:
        self.update_evaluation_list_widget(course_id=self._workflow.course_id)

    @Slot(object)
    def _handle_evaluation_id_changed(self, evaluation_id: int | None) -> None:
        self._workflow.reset_workflow(excluded_field_names=["course_id",
                                                            "evaluation_list_ids"])
        self._workflow.evaluation_id = evaluation_id
        self.update_template_file_combo_box()

    @Slot(bool)
    def _handle_empty_evaluation_list(self, empty_list: bool) -> None:
        if empty_list:
            current_data_selection = None
            items = []

            template_payload = template_payloads.get_template_combo_box_payload(
                current_data_selection=current_data_selection,
                items=items,
                has_evaluation=False)
            self._section_view.populate_template_file_combo_box(payload=template_payload)

            sheet_payload = template_payloads.get_sheet_combo_box_payload(
                current_data_selection=current_data_selection,
                items=items)
            self._section_view.populate_sheet_name_combo_box(payload=sheet_payload)

            row_keyword_payload = template_payloads.get_row_keyword_combo_box_payload(
                current_data_selection=current_data_selection,
                items=items)
            self._section_view.populate_row_keyword_combo_box(payload=row_keyword_payload)

            column_keyword_payload = template_payloads.get_column_keyword_combo_box_payload(
                current_data_selection=current_data_selection,
                items=items,
                no_row_is_selected=True)
            self._section_view.populate_column_keyword_combo_box(payload=column_keyword_payload)

    @Slot(Path)
    def _handle_evaluation_template_file_selection_changed(self, template_path: Path | None) -> None:
        if not template_path:
            template_path = None

        if template_path is None:
            self._reset_evaluation_template_configuration()

        self._workflow.template_file_path = template_path

        if self._workflow.evaluation_id is not None and template_path is not None:
            update_dto = EvaluationUpdateDTO(id=self._workflow.evaluation_id,
                                             template_file_path=template_path,
                                             template_filename=template_path.name)
            self._evaluation_services.update_evaluation(evaluation_update_dto=update_dto)

        self._update_sheet_name_combo_box()
        self._event_bus.evaluation.templateConfigurationChanged.emit()

    def _update_sheet_name_combo_box(self) -> None:
        if self._workflow.evaluation_id is not None:
            combo_box_payload = self._evaluation_orchestrator.get_sheet_name_combo_box_payload(
                template_file_path=self._workflow.template_file_path,
                evaluation_id=self._workflow.evaluation_id)

            self._section_view.populate_sheet_name_combo_box(payload=combo_box_payload)
            self._update_row_keyword_combo_box()

    @Slot(str)
    def _handle_evaluation_sheet_name_selection_changed(self, sheet: str) -> None:
        if not sheet:
            sheet = None

        if self._workflow.evaluation_id is not None and sheet != self._workflow.template_sheet_name:
            update_dto = EvaluationUpdateDTO(id=self._workflow.evaluation_id,
                                             template_sheet_name=sheet)
            self._evaluation_services.update_evaluation(evaluation_update_dto=update_dto)
            self._event_bus.evaluation.templateConfigurationChanged.emit()

            self._workflow.template_sheet_name = sheet
            self._update_row_keyword_combo_box()

    def _update_row_keyword_combo_box(self) -> None:
        if self._workflow.evaluation_id is not None:
            combo_box_payload = self._evaluation_orchestrator.get_row_keyword_combo_box_payload(
                template_file_path=self._workflow.template_file_path,
                template_sheet_name=self._workflow.template_sheet_name,
                evaluation_id=self._workflow.evaluation_id)
            self._section_view.populate_row_keyword_combo_box(payload=combo_box_payload)
            self._update_column_keyword_combo_box()

    @Slot(str)
    def _handle_row_keyword_changed(self, row_keyword: str) -> None:
        if not row_keyword:
            row_keyword = None

        if self._workflow.evaluation_id is not None and row_keyword != self._workflow.template_row_keyword:
            update_dto = EvaluationUpdateDTO(id=self._workflow.evaluation_id,
                                             template_row_keyword=row_keyword)
            self._evaluation_services.update_evaluation(evaluation_update_dto=update_dto)
            self._event_bus.evaluation.templateConfigurationChanged.emit()

            self._workflow.template_row_keyword = row_keyword
            self._update_column_keyword_combo_box()

    def _update_column_keyword_combo_box(self) -> None:
        if self._workflow.evaluation_id is not None:
            combo_box_payload = self._evaluation_orchestrator.get_column_keyword_combo_box_payload(
                template_file_path=self._workflow.template_file_path,
                template_sheet_name=self._workflow.template_sheet_name,
                template_row_keyword=self._workflow.template_row_keyword,
                evaluation_id=self._workflow.evaluation_id)
            self._section_view.populate_column_keyword_combo_box(payload=combo_box_payload)

    @Slot(str)
    def _handle_column_keyword_changed(self, column_keyword: str) -> None:
        if not column_keyword:
            column_keyword = None

        if self._workflow.evaluation_id is not None and column_keyword != self._workflow.template_column_keyword:
            update_dto = EvaluationUpdateDTO(id=self._workflow.evaluation_id,
                                             template_column_keyword=column_keyword)
            self._evaluation_services.update_evaluation(evaluation_update_dto=update_dto)
            self._event_bus.evaluation.templateConfigurationChanged.emit()

            self._workflow.template_column_keyword = column_keyword

    def _reset_evaluation_template_configuration(self) -> None:
        self._workflow.template_sheet_name = None
        self._workflow.template_row_keyword = None
        self._workflow.template_column_keyword = None


class EvaluationPageController(BaseController):
    courseDataChanged = Signal()
    courseDataValidated = Signal(bool)

    def __init__(self, page_view: "EvaluationPage", parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._page_view = page_view
        self._workflow = EvaluationTransactionWorkflow()

        self._course_selection_controller = CourseSelectionController(
            course_selection_group_box_view=self._page_view.course_selection_group_box)
        self._evaluation_form_import_controller = EvaluationFormImportController(
            workflow=self._workflow, section_view=self._page_view.evaluation_form_import_collapsible_section)
        self._evaluation_template_import_controller = EvaluationTemplateImportController(
            workflow=self._workflow, section_view=self._page_view.evaluation_template_import_groupbox)
        self._evaluation_management_controller = EvaluationManagementController(
            workflow=self._workflow, section_view=self._page_view.evaluation_management_groupbox)

        self._course_services = container.course_services()

        self._event_bus = container.event_bus()

        self._init_controller()

    @override
    def _connect_internal_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._evaluation_template_import_controller.evaluationTemplateImported,
                                    slot=self._evaluation_management_controller.update_template_file_combo_box)

        nuitka_helpers.safe_connect(signal=self._evaluation_form_import_controller.evaluationImported,
                                    slot=self._evaluation_management_controller.update_evaluation_list_widget)

    @override
    def _connect_upstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._event_bus.selection_widget.courseIDChanged,
                                    slot=self._handle_course_id_changed)

        nuitka_helpers.safe_connect(signal=self._event_bus.course.dataChanged, slot=self._refresh_view)
        nuitka_helpers.safe_connect(signal=self._event_bus.database.courseHasValidData, slot=self._toggle_ui_state)

    @Slot()
    @override
    def _refresh_view(self) -> None:
        self._course_selection_controller.refresh_combo_box_selection()
        self._course_services.check_valid_data()

    @Slot(object)
    def _handle_course_id_changed(self, course_id: int | None) -> None:
        if self._workflow.course_id != course_id:
            self._workflow.course_id = course_id

            self._evaluation_management_controller.update_evaluation_list_widget(course_id=course_id)

    @Slot(bool)
    def _toggle_ui_state(self, course_has_valid_data: bool) -> None:
        self._page_view.set_ui_state(enabled_page_widgets=course_has_valid_data)
