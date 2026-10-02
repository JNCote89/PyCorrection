from typing import override

from PySide6.QtCore import QEvent, QPoint
from PySide6.QtGui import QEnterEvent
from PySide6.QtWidgets import QCheckBox, QToolTip

from src.py_correction.ui.components.base_components.widget_lifecycle_mixin import WidgetLifecycleMixin


class BaseCheckBox(QCheckBox):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # To change CSS properties specific to this widget to avoid a visual glitch on selection. Global configuration
        # does not work.
        self.setProperty("class", "check_box_glitch_fix")

    def set_state(self, enabled: bool):
        self.setChecked(enabled)


class DefaultCheckBox(BaseCheckBox, WidgetLifecycleMixin):
    _is_final_component = True

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._init_ui()


class DefaultToolTipCheckBox(BaseCheckBox, WidgetLifecycleMixin):
    _is_final_component = True

    def __init__(self, tool_tip_text: str, parent=None):
        super().__init__(parent=parent)
        self._custom_tooltip = ""
        self._tool_tip_text = tool_tip_text
        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self._set_instant_tool_tip(self._tool_tip_text)

    def _set_instant_tool_tip(self, text) -> None:
        # There is a delay on the default tool tip, which might be missed if the user clicks too fast.
        self._custom_tooltip = text
        super().setToolTip("")

    @override
    def enterEvent(self, event: QEnterEvent) -> None:
        if self._custom_tooltip:
            global_pos = self.mapToGlobal(QPoint(10, self.height() + 5))
            QToolTip.showText(global_pos, self._custom_tooltip, self)
        super().enterEvent(event)

    @override
    def leaveEvent(self, event: QEvent) -> None:
        QToolTip.hideText()
        super().leaveEvent(event)


