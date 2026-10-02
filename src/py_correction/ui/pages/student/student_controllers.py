from dataclasses import dataclass
from typing import TYPE_CHECKING, override

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget

from src.py_correction.core import nuitka_helpers
from src.py_correction.core.dependency_injection import container
from src.py_correction.core.domains.course.course_student_dtos import CourseStudentUpdateDTO
from src.py_correction.core.domains.student.student_dtos import StudentCreateDTO
from src.py_correction.ui.components.base_components.base_controller import BaseController
from src.py_correction.ui.components.shared_components.course_selection.course_selection_controller import (
    CourseSelectionController)
from src.py_correction.ui.components.shared_components.workflow.workflow_mixin import ResetWorkflowMixin

if TYPE_CHECKING:
    from src.py_correction.ui.pages.student.student_page import StudentPage
    from src.py_correction.ui.pages.student.student_sections import (StudentTableViewGroupbox,
                                                                 StudentImportFormCollapsibleSection)


@dataclass
class StudentTransactionWorkflow(ResetWorkflowMixin):
    course_id: int | None = None


class StudentImportFormController(BaseController):

    def __init__(self, section_view: "StudentImportFormCollapsibleSection", workflow: StudentTransactionWorkflow,
                 parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._workflow = workflow
        self._section_view = section_view

        self._settings_manager = container.settings_manager()
        self._student_services = container.student_services()

        self._event_bus = container.event_bus()

        self._init_controller()

    @override
    def _connect_upstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._event_bus.settings.manualSectionExpansionChanged,
                                    slot=self._section_view.set_collapsible_section_state)

    @override
    def _connect_downstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._section_view.studentFormSubmitted, slot=self._import_student_form)

    @override
    def _refresh_view(self) -> None:
        self._refresh_expandable_section()

    @Slot(StudentCreateDTO)
    def _import_student_form(self, student_create_dto: StudentCreateDTO) -> None:
        if self._workflow.course_id is not None:
            self._student_services.add_student_from_dto(student_create_dto=student_create_dto,
                                                        course_id=self._workflow.course_id)
            self._event_bus.student.formImportCompleted.emit(student_create_dto)

    def _refresh_expandable_section(self) -> None:
        section_state = self._settings_manager.restored_settings.manual_section_expansion_state
        self._section_view.set_collapsible_section_state(expanded=section_state)



class StudentTableViewController(BaseController):

    def __init__(self, section_view: "StudentTableViewGroupbox", workflow: StudentTransactionWorkflow,
                 parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._workflow = workflow
        self._section_view = section_view

        self._course_student_services = container.course_student_services()

        self._event_bus = container.event_bus()

        self._init_controller()

    @override
    def _connect_upstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._event_bus.student.dataChanged, slot=self.populate_student_view)

    @override
    def _connect_downstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._section_view.studentStatusChanged, slot=self._change_student_status)

    def populate_student_view(self) -> None:
        course_id = self._workflow.course_id
        if course_id is not None:
            student_records = self._course_student_services.list_course_student_rows(course_id=course_id)

            self._section_view.set_students(student_records)

    @Slot(CourseStudentUpdateDTO)
    def _change_student_status(self, course_student_update_dto: CourseStudentUpdateDTO) -> None:
        self._course_student_services.update_course_student(course_student_update_dto=course_student_update_dto)
        self._event_bus.student.dataChanged.emit()


class StudentPageController(BaseController):

    def __init__(self, page_view: "StudentPage", parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._page_view = page_view
        self._workflow = StudentTransactionWorkflow()

        self._course_selection_controller = CourseSelectionController(
            course_selection_group_box_view=self._page_view.course_selection_group_box)
        self._student_import_form_controller = StudentImportFormController(
            section_view=self._page_view.student_import_form_collapsible_section, workflow=self._workflow)
        self._student_table_view_controller = StudentTableViewController(
            section_view=self._page_view.student_table_view_group_box, workflow=self._workflow)

        self._course_services = container.course_services()

        self._event_bus = container.event_bus()

        self._init_controller()

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
    def _handle_course_id_changed(self, course_id: int) -> None:
        if self._workflow.course_id != course_id:
            self._workflow.course_id = course_id

            self._student_table_view_controller.populate_student_view()

    @Slot(bool)
    def _toggle_ui_state(self, course_has_valid_data: bool) -> None:
        self._page_view.set_ui_state(enabled_page_widgets=course_has_valid_data)
