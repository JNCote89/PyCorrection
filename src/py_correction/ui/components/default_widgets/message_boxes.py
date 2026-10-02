from typing import override

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox

from src.py_correction.ui.components.base_components.widget_lifecycle_mixin import WidgetLifecycleMixin


class DefaultInfoMessageBox(QMessageBox, WidgetLifecycleMixin):
    _is_final_component = True

    def __init__(self, window_title: str, parent=None):
        super().__init__(parent=parent)
        self._window_title = window_title

        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self.setWindowTitle(self._window_title)
        self.setTextFormat(Qt.TextFormat.RichText)  # type: ignore[arg-type]
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)  # type: ignore[arg-type]
        self.setIcon(QMessageBox.Icon.Information)  # type: ignore[arg-type]


class DefaultQuestionMessageBox(QMessageBox, WidgetLifecycleMixin):
    _is_final_component = True

    def __init__(self, window_title: str, html_message, parent=None):
        super().__init__(parent=parent)
        self._window_title = window_title
        self._html_message = html_message

        self._init_ui()

    @property
    def reply(self):
        return self._reply

    @override
    def _create_widgets(self) -> None:
        self.setWindowTitle(self._window_title)
        self.setTextFormat(Qt.TextFormat.RichText)  # type: ignore[arg-type]
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)  # type: ignore[arg-type]
        self.setIcon(QMessageBox.Icon.Question)  # type: ignore[arg-type]

        self._reply = self.question(self,
                                    self._window_title,
                                    self._html_message,
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,  # type: ignore[arg-type]
                                    QMessageBox.StandardButton.No)  # type: ignore[arg-type]

    def get_reply_bool(self) -> bool:
        if self.reply == QMessageBox.StandardButton.Yes:
            return True
        else:
            return False
