from pathlib import Path
from typing import TYPE_CHECKING, override

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QApplication, QWidget

from src.py_correction.core import nuitka_helpers
from src.py_correction.core.dependency_injection import container
from src.py_correction.core.domains.course.course_dtos import CourseCreateDTO
from src.py_correction.ui.components.base_components.base_controller import BaseController

if TYPE_CHECKING:
    from src.py_correction.ui.pages.course.course_page import CoursePage
    from src.py_correction.ui.pages.course.course_sections import (CourseImportFormCollapsibleSection,
                                                               CourseTableViewGroupbox,
                                                               GeNoteImportGroupbox)


class GeNoteImportController(BaseController):

    def __init__(self, section_view: "GeNoteImportGroupbox", parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._section_view = section_view

        self._settings_manager = container.settings_manager()
        self._course_services = container.course_services()
        self._course_genote_orchestrator = container.course_genote_orchestrator()
        self._event_bus = container.event_bus()

        self._init_controller()

    @override
    def _connect_upstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._event_bus.settings.userRootDirectoryChanged,
                                    slot=self._section_view.update_starting_directory)

    @override
    def _connect_downstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._section_view.geNoteGradeFilePathSubmitted,
                                    slot=self._import_genote_grade_file_path)
        nuitka_helpers.safe_connect(signal=self._section_view.geNoteImportFailed,
                                    slot=self._event_bus.course.geNoteImportFailed)

    @override
    def _refresh_view(self) -> None:
        self._refresh_root_directory()

    @Slot(Path)
    def _import_genote_grade_file_path(self, file_path: Path) -> None:
        with QApplication.setOverrideCursor(Qt.CursorShape.BusyCursor): # type: ignore[arg-type]
            self._course_genote_orchestrator.import_genote_grade_file(file_path=file_path)

    def _refresh_root_directory(self) -> None:
        user_root_directory = self._settings_manager.restored_settings.user_root_directory
        self._section_view.update_starting_directory(user_root_directory)


class CourseImportFormController(BaseController):


    def __init__(self, section_view: "CourseImportFormCollapsibleSection", parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._section_view = section_view

        self._settings_manager = container.settings_manager()
        self._course_form_orchestrator = container.course_form_orchestrator()

        self._event_bus = container.event_bus()

        self._init_controller()

    @override
    def _connect_upstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._event_bus.settings.manualSectionExpansionChanged,
                                    slot=self._section_view.set_collapsible_section_state)

    @override
    def _connect_downstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._section_view.courseFormSubmitted, slot=self._import_course_form)

    @override
    def _refresh_view(self) -> None:
        self._refresh_manual_sections()

    @Slot(CourseCreateDTO)
    def _import_course_form(self, course_input_dto: CourseCreateDTO) -> None:
        with QApplication.setOverrideCursor(Qt.CursorShape.BusyCursor): # type: ignore[arg-type]
            self._course_form_orchestrator.import_course_form(course_input_dto=course_input_dto)

    def _refresh_manual_sections(self) -> None:
        manual_section_expand_state = self._settings_manager.restored_settings.manual_section_expansion_state
        self._section_view.set_collapsible_section_state(expanded=manual_section_expand_state)


class CourseTableViewController(BaseController):

    def __init__(self, section_view: "CourseTableViewGroupbox", parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._section_view = section_view

        self._course_services = container.course_services()

        self._init_controller()

    def set_courses(self) -> None:
        course_records = self._course_services.list_course_table_rows()
        self._section_view.set_courses(course_table_dtos=course_records)


class CoursePageController(BaseController):

    def __init__(self, page_view: "CoursePage", parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._page_view = page_view

        self._genote_import_controller = GeNoteImportController(
            section_view=self._page_view.genote_import_groupbox)
        self._course_import_form_controller = CourseImportFormController(
            section_view=self._page_view.course_import_form_collapsible_section)
        self._course_table_view_controller = CourseTableViewController(
            section_view=self._page_view.table_view_groupbox)
        self._course_services = container.course_services()

        self._event_bus = container.event_bus()

        self._init_controller()

    @override
    def _connect_upstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._event_bus.course.dataChanged,
                                    slot=self._refresh_view)

    @Slot()
    @override
    def _refresh_view(self) -> None:
        self._course_table_view_controller.set_courses()
        self._course_services.check_valid_data()