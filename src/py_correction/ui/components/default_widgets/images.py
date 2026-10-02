from typing import override

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPaintEvent, QPainter, QPixmap
from PySide6.QtWidgets import QLabel, QSizePolicy, QWidget


class ResponsiveImageLabel(QLabel):

    def __init__(self, image_path: str, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self.pixmap = QPixmap(image_path)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding) # type: ignore[arg-type]
        self.setMinimumSize(1, 1)

    @override
    def sizeHint(self) -> QSize:
        if not self.pixmap.isNull():
            return self.pixmap.size()
        return super().sizeHint()

    @override
    def hasHeightForWidth(self) -> bool:
        return not self.pixmap.isNull()

    @override
    def heightForWidth(self, width: int) -> int:
        if not self.pixmap.isNull() and self.pixmap.width() > 0:
            return int(width * (self.pixmap.height() / float(self.pixmap.width())))
        return super().heightForWidth(width)

    @override
    def paintEvent(self, event: QPaintEvent) -> None:
        if self.pixmap.isNull():
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform) # type: ignore[arg-type]
        painter.setRenderHint(QPainter.RenderHint.Antialiasing) # type: ignore[arg-type]

        scaled_size = self.pixmap.size().scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio)  # type: ignore[arg-type]

        x = (self.width() - scaled_size.width()) // 2
        y = (self.height() - scaled_size.height()) // 2

        painter.drawPixmap(x, y, scaled_size.width(), scaled_size.height(), self.pixmap)
