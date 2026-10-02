from typing import override

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

from src.py_correction import app_metadata
from src.py_correction.ui.components.base_components.base_page import BasePage
from src.py_correction.ui.components.default_widgets.labels import DefaultLabel
from src.py_correction.ui.components.layouts import DefaultPageVerticalScrollLayout
from src.py_correction.ui.pages.instruction.instruction_sections import (AboutCollapsibleSection, FAQCollapsibleSection,
                                                                         OptionsCollapsibleSection,
                                                                         QuickStartCollapsibleSection)


class InstructionPage(BasePage):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self.version_label: DefaultLabel
        self.about_section: AboutCollapsibleSection
        self.quick_start_section: QuickStartCollapsibleSection
        self.options_section: OptionsCollapsibleSection
        self.faq_section: FAQCollapsibleSection

        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self.version_label = DefaultLabel(text="Version",
                                          subtext=app_metadata.METADATA.VERSION,
                                          alignment_h_flag=Qt.AlignmentFlag.AlignRight) # type: ignore[arg-type]
        self.about_section = AboutCollapsibleSection()
        self.quick_start_section = QuickStartCollapsibleSection()
        self.options_section = OptionsCollapsibleSection()
        self.faq_section = FAQCollapsibleSection()

    @override
    def _assemble_layout(self) -> None:
        self.page_layout = DefaultPageVerticalScrollLayout(page_view=self,
                                                           widgets=[self.version_label,
                                                                    self.about_section,
                                                                    self.quick_start_section,
                                                                    self.options_section,
                                                                    self.faq_section])
