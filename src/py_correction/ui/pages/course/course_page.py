from typing import override

from PySide6.QtWidgets import QWidget

from src.py_correction.ui.components.base_components.base_page import BasePage
from src.py_correction.ui.components.layouts import DefaultPageVerticalScrollLayout
from src.py_correction.ui.pages.course.course_controllers import (CoursePageController)
from src.py_correction.ui.pages.course.course_sections import (CourseImportFormCollapsibleSection,
                                                               CourseTableViewGroupbox,
                                                               GeNoteImportGroupbox)


class CoursePage(BasePage):

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self.genote_import_groupbox: GeNoteImportGroupbox
        self.course_import_form_collapsible_section: CourseImportFormCollapsibleSection
        self.table_view_groupbox: CourseTableViewGroupbox

        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self.genote_import_groupbox = GeNoteImportGroupbox()
        self.course_import_form_collapsible_section = CourseImportFormCollapsibleSection()
        self.table_view_groupbox = CourseTableViewGroupbox()

    @override
    def _initialize_controllers(self) -> None:
        self._page_controller = CoursePageController(page_view=self)

    @override
    def _assemble_layout(self) -> None:
        self._page_layout = DefaultPageVerticalScrollLayout(page_view=self,
                                                            widgets=[self.genote_import_groupbox,
                                                                     self.course_import_form_collapsible_section,
                                                                     self.table_view_groupbox])
