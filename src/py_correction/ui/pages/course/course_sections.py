from pathlib import Path
from typing import override

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QWidget

from src.py_correction.core import nuitka_helpers
from src.py_correction.core.domains.course.course_dtos import CourseCreateDTO, CourseTableDTO
from src.py_correction.ui.components.base_components.widget_lifecycle_mixin import WidgetLifecycleMixin
from src.py_correction.ui.components.default_widgets.collapsible_sections import DefaultCollapsibleSection
from src.py_correction.ui.pages.course.course_widgets import (CourseImportFormWidget, CourseTableModel, CourseTableView,
                                                              GeNoteImportWidget)


class GeNoteImportGroupbox(QGroupBox, WidgetLifecycleMixin):
    _is_final_component = True

    geNoteGradeFilePathSubmitted = Signal(Path)
    geNoteImportFailed = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__("Importation automatique de cours", parent=parent)
        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self._genote_import_widget = GeNoteImportWidget()

    @override
    def _assemble_layout(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self._genote_import_widget)

    @override
    def _connect_downstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._genote_import_widget.geNoteGradeFilePathSubmitted,
                                    slot=self.geNoteGradeFilePathSubmitted)
        nuitka_helpers.safe_connect(signal=self._genote_import_widget.geNoteImportFailed, slot=self.geNoteImportFailed)

    @Slot(Path)
    def update_starting_directory(self, starting_directory: Path) -> None:
        self._genote_import_widget.update_starting_path_directory(path_directory=starting_directory)


class CourseImportFormCollapsibleSection(QWidget, WidgetLifecycleMixin):
    _is_final_component = True

    courseFormSubmitted = Signal(CourseCreateDTO)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self.collapsible_section = DefaultCollapsibleSection(title="Création manuelle d'un cours",
                                                             subtitle="Seulement en l'absence d'une feuille GeNote "
                                                                      "pour le cours")
        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self._course_import_form_widget = CourseImportFormWidget()

    @override
    def _assemble_layout(self) -> None:
        self.collapsible_section.add_widget(self._course_import_form_widget)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.collapsible_section)

    @override
    def _connect_downstream_signals(self) -> None:
        nuitka_helpers.safe_connect(signal=self._course_import_form_widget.courseFormSubmitted,
                                    slot=self.courseFormSubmitted)

    def set_collapsible_section_state(self, expanded: bool):
        self.collapsible_section.set_expand_state(expanded=expanded)


class CourseTableViewGroupbox(QGroupBox, WidgetLifecycleMixin):
    _is_final_component = True

    def __init__(self, parent=None):
        super().__init__("Cours dans la base de données", parent=parent)
        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self._course_table_model = CourseTableModel()
        self._course_table_view = CourseTableView(table_model=self._course_table_model)

    @override
    def _assemble_layout(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self._course_table_view)

    @Slot(CourseTableDTO)
    def set_courses(self, course_table_dtos: list[CourseTableDTO]) -> None:
        self._course_table_model.set_courses(course_table_dtos=course_table_dtos)
        self._course_table_view.adjust_table_height()
