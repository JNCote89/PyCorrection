from typing import override

from PySide6.QtWidgets import QWidget

from src.py_correction.ui.components.base_components.base_page import BasePage
from src.py_correction.ui.components.layouts import DefaultPageVerticalScrollLayout
from src.py_correction.ui.components.shared_components.course_selection.course_selection_group_boxes import (
    CourseSelectionGroupBox)
from src.py_correction.ui.pages.archive.archive_controllers import ArchivePageController
from src.py_correction.ui.pages.archive.archive_sections import ArchiveManagementGroupBox


class ArchivePage(BasePage):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self.course_selection_group_box: CourseSelectionGroupBox
        self.archive_management_group_box: ArchiveManagementGroupBox

        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self.course_selection_group_box = CourseSelectionGroupBox()
        self.archive_management_group_box = ArchiveManagementGroupBox()

    @override
    def _initialize_controllers(self) -> None:
        self._page_controller = ArchivePageController(page_view=self)

    @override
    def _assemble_layout(self) -> None:
        self._page_layout = DefaultPageVerticalScrollLayout(page_view=self, widgets=[self.course_selection_group_box,
                                                                                     self.archive_management_group_box])

    def set_ui_state(self, enabled_page_widgets: bool) -> None:
        self.course_selection_group_box.set_state(enabled_page_widgets)
