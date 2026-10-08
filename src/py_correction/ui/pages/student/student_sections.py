from typing import override

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QWidget

from src.py_correction.core import nuitka_helpers
from src.py_correction.core.domains.course.course_student_dtos import CourseStudentTableDTO, CourseStudentUpdateDTO
from src.py_correction.core.domains.student.student_dtos import StudentCreateDTO
from src.py_correction.ui.components.base_components.widget_lifecycle_mixin import WidgetLifecycleMixin
from src.py_correction.ui.components.default_widgets.collapsible_sections import DefaultCollapsibleSection
from src.py_correction.ui.pages.student.student_widgets import (StudentImportFormWidget, StudentTableModel,
                                                                StudentTableView)


class StudentImportFormCollapsibleSection(QWidget, WidgetLifecycleMixin):
    _is_final_component = True

    studentFormSubmitted = Signal(StudentCreateDTO)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self.collapsible_section = DefaultCollapsibleSection(title="Ajout manuel d'un étudiant",
                                                             subtitle="Seulement en l'absence d'une feuille GeNote "
                                                                      "pour le cours")

        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self._student_import_form_widget = StudentImportFormWidget()

    @override
    def _assemble_layout(self) -> None:
        self.collapsible_section.add_widget(self._student_import_form_widget)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.collapsible_section)

    @override
    def _connect_downstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._student_import_form_widget.studentFormSubmitted,
                                    slot=self.studentFormSubmitted)

    def set_collapsible_section_state(self, expanded: bool) -> None:
        self.collapsible_section.set_expand_state(expanded=expanded)


class StudentTableViewGroupbox(QGroupBox, WidgetLifecycleMixin):
    _is_final_component = True

    studentStatusChanged = Signal(CourseStudentUpdateDTO)

    def __init__(self, parent: QWidget | None = None):
        super().__init__("Étudiant pour le cours", parent=parent)

        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self._student_table_model = StudentTableModel()
        self._student_table_view = StudentTableView(table_model=self._student_table_model)

    @override
    def _assemble_layout(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self._student_table_view)

    @override
    def _connect_downstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._student_table_model.studentStatusChanged,
                                    slot=self.studentStatusChanged)

    @Slot(CourseStudentTableDTO)
    def set_students(self, students: list[CourseStudentTableDTO]) -> None:
        self._student_table_model.set_students(course_student_table_dtos=students)

        # To remove the scrolling bar which duplicate the scrolling area with the page, making navigation difficult.
        self._student_table_view.adjust_table_height()
