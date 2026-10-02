from typing import TYPE_CHECKING, override

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget

from src.py_correction.core import nuitka_helpers
from src.py_correction.core.dependency_injection import container
from src.py_correction.core.domains.shared.shared_enums import UNSET
from src.py_correction.ui.components.base_components.base_controller import BaseController

if TYPE_CHECKING:
    from src.py_correction.ui.components.shared_components.course_selection.course_selection_group_boxes import (
        CourseSelectionGroupBox)


class CourseSelectionController(BaseController):

    def __init__(self, course_selection_group_box_view: "CourseSelectionGroupBox", parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._course_selection_group_box = course_selection_group_box_view

        self._settings_manager = container.settings_manager()
        self._course_services = container.course_services()

        self._event_bus = container.event_bus()

        self._last_course_id_sync = UNSET
        self._last_semester_label_sync = UNSET

        self._init_controller()

    @override
    def _connect_upstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._event_bus.selection_widget.courseIDChanged,
                                    slot=self._synchronize_upstream_course_id_changed)
        nuitka_helpers.safe_connect(signal=self._event_bus.selection_widget.semesterLabelChanged,
                                    slot=self._synchronize_upstream_semester_label_changed)

        nuitka_helpers.safe_connect(signal=self._event_bus.course.newCourseIDImported,
                                    slot=self._handle_downstream_course_id_changed)

    @override
    def _connect_downstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._course_selection_group_box.courseIDChanged,
                                    slot=self._handle_downstream_course_id_changed)
        nuitka_helpers.safe_connect(signal=self._course_selection_group_box.semesterLabelChanged,
                                    slot=self._handle_downstream_semester_label_changed)

    def refresh_combo_box_selection(self) -> None:
        course_dtos = self._course_services.list_course_selection_dtos()
        restore_course_id = self._settings_manager.restored_settings.course_id_selected
        restore_semester_label = self._settings_manager.restored_settings.semester_label_selected

        self._course_selection_group_box.refresh_group_box(course_selection_widget_dtos=course_dtos,
                                                           restored_course_id=restore_course_id,
                                                           restored_semester_label=restore_semester_label)

    @Slot(object)
    def _synchronize_upstream_course_id_changed(self, course_id: int | None):
        if self._last_course_id_sync != course_id:
            self._last_course_id_sync = course_id

            self._course_selection_group_box.blockSignals(True)
            self._course_selection_group_box.synchronized_course_id(course_id=course_id)
            self._course_selection_group_box.blockSignals(False)

    @Slot(object)
    def _synchronize_upstream_semester_label_changed(self, semester_label: str | None):
        if self._last_semester_label_sync != semester_label:
            self._last_semester_label_sync = semester_label

            self._course_selection_group_box.blockSignals(True)
            self._course_selection_group_box.synchronized_semester_label(semester_label=semester_label)
            self._course_selection_group_box.blockSignals(False)

    @Slot(object)
    def _handle_downstream_course_id_changed(self, course_id: int | None):
        if self._last_course_id_sync != course_id:
            self._last_course_id_sync = course_id

            self._event_bus.selection_widget.courseIDChanged.emit(course_id)

    @Slot(object)
    def _handle_downstream_semester_label_changed(self, semester_label: str | None):
        if self._last_semester_label_sync != semester_label:
            self._last_semester_label_sync = semester_label

            self._event_bus.selection_widget.semesterLabelChanged.emit(semester_label)
