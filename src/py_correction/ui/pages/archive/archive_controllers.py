from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, override

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QApplication, QWidget

from src.py_correction.core import nuitka_helpers
from src.py_correction.core.dependency_injection import container
from src.py_correction.ui.components.base_components.base_controller import BaseController
from src.py_correction.ui.components.shared_components.course_selection.course_selection_controller import (
    CourseSelectionController)
from src.py_correction.ui.components.shared_components.workflow.workflow_mixin import ResetWorkflowMixin
from src.py_correction.ui.feedbacks.labels.directory_labels import ArchivePathLabelText

if TYPE_CHECKING:
    from src.py_correction.ui.pages.archive.archive_page import ArchivePage
    from src.py_correction.ui.pages.archive.archive_sections import ArchiveManagementGroupBox


@dataclass
class ArchiveTransactionWorkflow(ResetWorkflowMixin):
    course_id: int | None = None


class ArchiveManagementController(BaseController):
    archiveLabelUpdated = Signal(Path)

    def __init__(self, section_view: "ArchiveManagementGroupBox", workflow: ArchiveTransactionWorkflow,
                 parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._workflow = workflow
        self._section_view = section_view

        self._settings_manager = container.settings_manager()
        self._archive_orchestrator = container.archive_orchestrator()

        self._event_bus = container.event_bus()

        self._init_controller()

    @override
    def _connect_upstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._event_bus.settings.userRootDirectoryChanged,
                                    slot=self._refresh_archive_label)
        nuitka_helpers.safe_connect(signal=self._event_bus.course.geNoteImportCompleted,
                                    slot=self._refresh_archive_label)

    @override
    def _connect_downstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._section_view.archiveButtonClicked, slot=self._handle_course_archiving)
        nuitka_helpers.safe_connect(signal=self._section_view.restoredArchivePathSubmitted,
                                    slot=self._handle_archive_restoration)

    @override
    def _refresh_view(self) -> None:
        self._refresh_archive_label()

    def set_archive_button_state(self, button_state: bool) -> None:
        self._section_view.set_archive_button_state(button_state=button_state)

    @Slot()
    def _refresh_archive_label(self) -> None:
        archive_path = self._archive_orchestrator.get_archive_path()
        archive_label = ArchivePathLabelText(directory=archive_path)
        self._section_view.set_archive_label(archive_label)

    @Slot()
    def _handle_course_archiving(self) -> None:
        if self._workflow.course_id is not None:
            with QApplication.setOverrideCursor(Qt.CursorShape.BusyCursor): # type: ignore[arg-type]
                response_dto = self._archive_orchestrator.archive_course(course_id=self._workflow.course_id)

                self._event_bus.course.dataChanged.emit()
                self._event_bus.student.dataChanged.emit()
                self._event_bus.evaluation.dataChanged.emit()

                self._event_bus.archive.courseArchiveCompleted.emit(response_dto)

    @Slot(Path)
    def _handle_archive_restoration(self, zip_file_path: Path) -> None:
        with QApplication.setOverrideCursor(Qt.CursorShape.BusyCursor): # type: ignore[arg-type]
            response_dto = self._archive_orchestrator.restore_course(zip_file_path=zip_file_path)

            self._event_bus.course.dataChanged.emit()
            self._event_bus.student.dataChanged.emit()
            self._event_bus.evaluation.dataChanged.emit()

            self._event_bus.archive.courseRestoreCompleted.emit(response_dto)


class ArchivePageController(BaseController):

    def __init__(self, page_view: "ArchivePage", parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._page_view = page_view
        self._workflow = ArchiveTransactionWorkflow()

        self._course_selection_controller = CourseSelectionController(
            course_selection_group_box_view=self._page_view.course_selection_group_box)
        self._archive_management_controller = ArchiveManagementController(
            workflow=self._workflow, section_view=self._page_view.archive_management_group_box)

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
    def _handle_course_id_changed(self, course_id: int | None) -> None:
        if self._workflow.course_id != course_id:
            self._workflow.course_id = course_id

    @Slot(bool)
    def _toggle_ui_state(self, course_has_valid_data: bool) -> None:
        self._page_view.set_ui_state(enabled_page_widgets=course_has_valid_data)
        self._archive_management_controller.set_archive_button_state(button_state=course_has_valid_data)
