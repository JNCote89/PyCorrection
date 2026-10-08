from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QAction, QTextCursor
from PySide6.QtWidgets import QMenu, QTextEdit

from src.py_correction.core import nuitka_helpers
from src.py_correction.core.logger import qt_log_bridge
from src.py_correction.ui.components.base_components.widget_lifecycle_mixin import WidgetLifecycleMixin


class PartialLogConsoleWidget(QTextEdit, WidgetLifecycleMixin):
    def __init__(self, parent=None):
        super().__init__(parent)
        # There is a conflict with the QtDarkTheme and native Qt, specifics properties must be set in qss,
        # so the placeholder is readable in both dark and light theme.
        self.setObjectName("Console")
        self.setPlaceholderText("Console")

        self.setReadOnly(True)
        self.document().setMaximumBlockCount(1000)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu) # type: ignore[arg-type]

        nuitka_helpers.safe_connect(signal=self.customContextMenuRequested, slot=self.show_context_menu)

        nuitka_helpers.safe_connect(signal=qt_log_bridge.log_emitted, slot=self.append_log)

    @Slot(str, str)
    def append_log(self, formatted_message: str, record_level: str):
        safe_msg = formatted_message.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        html_msg = f"<span>{safe_msg}</span>"

        self.append(html_msg)
        self.moveCursor(QTextCursor.MoveOperation.End) # type: ignore[arg-type]

    def show_context_menu(self, position) -> None:
        menu = QMenu(self)

        copy_action = QAction("Copier la sélection", self)
        nuitka_helpers.safe_connect(signal=copy_action.triggered, slot=self.copy)

        copy_action.setEnabled(self.textCursor().hasSelection())
        menu.addAction(copy_action)

        copy_all_action = QAction("Copier tous les logs", self)
        nuitka_helpers.safe_connect(signal=copy_all_action.triggered, slot=self.copy_all_logs)
        menu.addAction(copy_all_action)

        menu.addSeparator()

        clear_action = QAction("Effacer tous les logs", self)
        nuitka_helpers.safe_connect(signal=clear_action.triggered, slot=self.clear)
        menu.addAction(clear_action)

        menu.exec(self.mapToGlobal(position)) # type: ignore[arg-type]

    def copy_all_logs(self) -> None:
        original_cursor = self.textCursor()

        self.selectAll()
        self.copy()
        self.setTextCursor(original_cursor)
