import logging
from pathlib import Path

from typing_extensions import override

# Introduces bug with PySide. The fonts are set inside the theme manager module.
logging.getLogger('matplotlib.font_manager').disabled = True
logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtCore import Qt, QPoint, Slot, QStandardPaths
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import QMenu, QFileDialog

from src.py_correction.ui.components.base_components.widget_lifecycle_mixin import WidgetLifecycleMixin


class PartialFigure(FigureCanvasQTAgg, WidgetLifecycleMixin):

    def __init__(self, figure: Figure, figure_name: str, parent=None):
        super().__init__(figure=figure)
        self._is_first_show = True
        self._figure_name = figure_name
        self.setParent(parent)

        self.setContextMenuPolicy(Qt.CustomContextMenu)  # type: ignore[arg-type]
        self.customContextMenuRequested.connect(self._show_context_menu)

        self._save_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)  # type: ignore[arg-type]

    def save_figure(self, save_path: str | None = None) -> None:
        if save_path is None:
            save_path = f"{self._save_path}"

        file_path, _ = QFileDialog.getSaveFileName(self,
                                                   "Sauvegarder la figure",
                                                   save_path,
                                                   "PNG Files (*.png);;PDF Files (*.pdf);;All Files (*.*)")

        if file_path:
            self.figure.savefig(file_path, dpi=300, bbox_inches='tight')

    def update_save_path(self, save_path: Path | str) -> None:
        self._save_path = Path(save_path)

    @override
    def wheelEvent(self, event: QWheelEvent) -> None:
        """To prevent intercepting the mouse wheel and disrupting the page scroll area."""
        event.ignore()

    @Slot()
    def _show_context_menu(self, pos: QPoint) -> None:
        menu = QMenu(self)
        save_action = menu.addAction("Sauvegarder la figure")

        global_pos = self.mapToGlobal(pos)
        action = menu.exec(global_pos)

        if action == save_action:
            self.save_figure()