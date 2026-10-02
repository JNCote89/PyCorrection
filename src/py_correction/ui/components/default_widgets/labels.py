from typing import override

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from src.py_correction.ui.components.base_components.widget_lifecycle_mixin import WidgetLifecycleMixin


class DefaultDynamicLabel(QLabel, WidgetLifecycleMixin):
    _is_final_component = True

    def __init__(self, text: str | None = None, custom_html_style: str | None = None):
        super().__init__()
        self._text = text
        self._custom_html_style = custom_html_style

        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        if self._text:
            if self._custom_html_style:
                self.setText(f"<div style='{self._custom_html_style}'>{self._text}</div>")
            else:
                self.setText(f"<div>{self._text}</div>")

        self.setWordWrap(True)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)  # type: ignore[arg-type]
        self.setOpenExternalLinks(True)


class DefaultLabel(QLabel, WidgetLifecycleMixin):
    _is_final_component = True

    SUBTEXT_STYLE = "style='font-size: 10pt;'"

    def __init__(self, text: str, subtext: str | None = None,
                 alignment_h_flag: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignRight,  # type: ignore[arg-type]
                 alignment_v_flag: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignVCenter,  # type: ignore[arg-type]
                 parent=None):
        super().__init__(parent=parent)
        self._text = text
        self._subtext = subtext
        self._alignment_h_flag = alignment_h_flag
        self._alignment_v_flag = alignment_v_flag

        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        label_text = f"<div><b>{self._text}</b></div>"
        if self._subtext:
            label_text = label_text + f"<br> <span {self.SUBTEXT_STYLE}>{self._subtext}</span>"

        self.setWordWrap(True)
        self.setAlignment(self._alignment_h_flag | self._alignment_v_flag)  # type: ignore[arg-type]
        self.setText(label_text)

        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)  # type: ignore[arg-type]
        self.setOpenExternalLinks(True)


class DefaultParagraphLabel(QLabel, WidgetLifecycleMixin):
    _is_final_component = True

    def __init__(self, text: str,
                 alignment_h_flag: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft,  # type: ignore[arg-type]
                 alignment_v_flag: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignTop,  # type: ignore[arg-type]
                 parent=None):
        super().__init__(parent=parent)
        self._text = text
        self._alignment_h_flag = alignment_h_flag
        self._alignment_v_flag = alignment_v_flag

        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        label_text = f"<p style='line-height:1.5;'>{self._text}</p>"

        self.setWordWrap(True)
        self.setAlignment(self._alignment_h_flag | self._alignment_v_flag)  # type: ignore[arg-type]
        self.setText(label_text)

        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)  # type: ignore[arg-type]
        self.setOpenExternalLinks(True)
