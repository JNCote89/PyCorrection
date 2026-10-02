from typing import override

from PySide6.QtWidgets import QWidget

from src.py_correction.ui.components.base_components.base_page import BasePage
from src.py_correction.ui.components.layouts import DefaultPageVerticalScrollLayout
from src.py_correction.ui.components.shared_components.course_selection.course_selection_group_boxes import (
    CourseSelectionGroupBox)
from src.py_correction.ui.pages.student.student_controllers import StudentPageController
from src.py_correction.ui.pages.student.student_sections import (StudentImportFormCollapsibleSection,
                                                                 StudentTableViewGroupbox)


class StudentPage(BasePage):

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self.course_selection_group_box: CourseSelectionGroupBox
        self.student_import_form_collapsible_section: StudentImportFormCollapsibleSection
        self.student_table_view_group_box: StudentTableViewGroupbox

        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self.course_selection_group_box = CourseSelectionGroupBox()
        self.student_import_form_collapsible_section = StudentImportFormCollapsibleSection()
        self.student_table_view_group_box = StudentTableViewGroupbox()

    @override
    def _initialize_controllers(self) -> None:
        self._page_controller = StudentPageController(page_view=self)

    @override
    def _assemble_layout(self) -> None:
        self._page_layout = DefaultPageVerticalScrollLayout(page_view=self,
                                                            widgets=[self.course_selection_group_box,
                                                                     self.student_import_form_collapsible_section,
                                                                     self.student_table_view_group_box])

    def set_ui_state(self, enabled_page_widgets: bool) -> None:
        self.course_selection_group_box.set_state(enabled_page_widgets)

        self.student_import_form_collapsible_section.setVisible(enabled_page_widgets)
        self.student_table_view_group_box.setVisible(enabled_page_widgets)
