from typing import override

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QGroupBox

from src.py_correction.core.domains.course.course_dtos import CourseSelectionWidgetDTO
from src.py_correction.ui.components.base_components.widget_lifecycle_mixin import WidgetLifecycleMixin
from src.py_correction.ui.components.default_widgets.labels import DefaultLabel
from src.py_correction.ui.components.layouts import DefaultGridLayout
from src.py_correction.ui.components.shared_components.course_selection.course_selection_widgets import (
    CourseIDComboBox, CourseSelectionComboBoxModel, CourseSemesterComboBox)


class CourseSelectionGroupBox(QGroupBox, WidgetLifecycleMixin):
    _is_final_component = True

    courseIDChanged = Signal(object)
    semesterLabelChanged = Signal(object)

    def __init__(self, parent=None):
        super().__init__("Sélection de cours", parent)
        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self.setMaximumHeight(150)

        self._semester_label = DefaultLabel(text="Filtrer la session",
                                            alignment_h_flag=Qt.AlignmentFlag.AlignHCenter) # type: ignore[arg-type]
        self._course_label = DefaultLabel(text="Sélectionner le cours",
                                          alignment_h_flag=Qt.AlignmentFlag.AlignHCenter) # type: ignore[arg-type]

        self._course_selection_combo_box_model = CourseSelectionComboBoxModel()

        self._course_semester_combo_box = CourseSemesterComboBox()
        self._course_semester_combo_box.setModel(self._course_selection_combo_box_model.semester_model)

        self._course_id_combo_box = CourseIDComboBox()
        self._course_id_combo_box.setModel(self._course_selection_combo_box_model)

    @override
    def _assemble_layout(self) -> None:
        main_grid_layout = DefaultGridLayout(self)

        main_grid_layout.addWidget(self._semester_label, 0, 0)
        main_grid_layout.addWidget(self._course_label, 0, 1)

        main_grid_layout.addWidget(self._course_semester_combo_box, 1, 0)
        main_grid_layout.addWidget(self._course_id_combo_box, 1, 1)

        main_grid_layout.setColumnStretch(0, 1)
        main_grid_layout.setColumnStretch(1, 3)

    @override
    def _connect_internal_signals(self) -> None:
        self._course_semester_combo_box.currentTextChanged.connect(
            self._course_selection_combo_box_model.filter_course_by_semester)

    @override
    def _connect_downstream_signals(self) -> None:
        self._course_id_combo_box.courseIDChanged.connect(self.courseIDChanged)
        self._course_semester_combo_box.semesterLabelChanged.connect(self.semesterLabelChanged)

    @Slot(CourseSelectionWidgetDTO)
    def set_courses(self, course_selection_widget_dtos: list[CourseSelectionWidgetDTO]) -> None:
        self._course_selection_combo_box_model.set_courses(course_selection_widget_dtos=course_selection_widget_dtos)

    @Slot(object)
    def synchronized_course_id(self, course_id: int | None):
        self._course_id_combo_box.synchronized_course_id(course_id=course_id)

    @Slot(object)
    def synchronized_semester_label(self, semester_label: str | None):
        self._course_semester_combo_box.synchronized_semester_label(semester_label=semester_label)

    def refresh_group_box(self, course_selection_widget_dtos: list[CourseSelectionWidgetDTO],
                          restored_semester_label: str | None, restored_course_id: int | None):

        self.blockSignals(True)
        self.set_courses(course_selection_widget_dtos=course_selection_widget_dtos)
        self.synchronized_course_id(course_id=restored_course_id)
        self.synchronized_semester_label(semester_label=restored_semester_label)
        self.blockSignals(False)

        self.courseIDChanged.emit(restored_course_id)
        self.semesterLabelChanged.emit(restored_semester_label)


    def set_state(self, data_is_valid: bool) -> None:
        self._course_id_combo_box.setEnabled(data_is_valid)
        self._course_semester_combo_box.setEnabled(data_is_valid)
        self._course_id_combo_box.update_placeholder(data_is_valid)
