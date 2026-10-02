from typing import override

from PySide6.QtWidgets import QWidget

from src.py_correction.ui.components.base_components.base_page import BasePage
from src.py_correction.ui.components.layouts import DefaultPageVerticalScrollLayout
from src.py_correction.ui.pages.configuration.configuration_controllers import (ConfigurationsPageController)
from src.py_correction.ui.pages.configuration.configuration_sections import ConfigurationsGroupBox


class ConfigurationPage(BasePage):

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self.configurations_groupbox: ConfigurationsGroupBox

        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self.configurations_groupbox = ConfigurationsGroupBox()

    @override
    def _initialize_controllers(self) -> None:
        self._page_controller = ConfigurationsPageController(page_view=self)

    @override
    def _assemble_layout(self) -> None:
        self._page_layout = DefaultPageVerticalScrollLayout(page_view=self, widgets=[self.configurations_groupbox])
