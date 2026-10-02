from typing import override

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QGroupBox, QLabel, QLayout, QPushButton, QVBoxLayout, QWidget

from src.py_correction.ui.components.base_components.widget_lifecycle_mixin import WidgetLifecycleMixin


class _CollapsibleSectionTitle(QLabel, WidgetLifecycleMixin):
    _is_final_component = True

    def __init__(self, title_size: int = 16, subtitle_size: int = 10, parent=None):
        super().__init__(parent=parent)
        self._title_size = title_size
        self._subtitle_size = subtitle_size

        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)  # type: ignore
        self.setWordWrap(True)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft)  # type: ignore

    def set_html_title(self, unicode_symbol: str, title: str, subtitle: str | None) -> None:
        subtitle_row = (f"<tr>"
                        f"<td></td>"
                        f"<td style='font-size: {self._subtitle_size}pt;'>{subtitle}</td>"
                        f"</tr>"
                        if subtitle else "")

        html_title = ("<table>"
                      "<tbody>"
                      "<tr>"
                      f"<td>{unicode_symbol}</td>"
                      f"<td style='font-size: {self._title_size}pt; font-weight: bold;'>{title}</td>"
                      "</tr>"
                      f"{subtitle_row}"
                      "</tbody>"
                      "</table>")

        self.setText(html_title)


class DefaultCollapsibleSection(QWidget, WidgetLifecycleMixin):
    _is_final_component = True

    def __init__(self, title: str, subtitle: str | None = None, parent=None):
        super().__init__(parent)
        self._title = title
        self._subtitle = subtitle

        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self.toggle_button = QPushButton()
        self.toggle_button.setObjectName("CollapsibleSectionTitle")
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)

        self.title_label = _CollapsibleSectionTitle()
        self.title_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)  # type: ignore

        self.content_group_box = QGroupBox()
        self.content_group_box.setProperty("class", "collapsible_section_group_box")
        self.content_group_box.setVisible(False)

    @override
    def _assemble_layout(self) -> None:
        self.button_layout = QVBoxLayout(self.toggle_button)
        self.button_layout.setContentsMargins(0, 0, 0, 0)

        self.button_layout.addWidget(self.title_label)

        self.content_layout = QVBoxLayout(self.content_group_box)
        self.content_layout.setContentsMargins(10, 5, 5, 5)

        section_layout = QVBoxLayout(self)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(0)
        section_layout.addWidget(self.toggle_button)
        section_layout.addWidget(self.content_group_box)

        # To initialize the section. Can be overridden by calling the method set_expand_state in the page.
        self.set_expand_state(expanded=False)

    @override
    def _connect_internal_signals(self) -> None:
        self.toggle_button.clicked.connect(self.set_expand_state)

    @Slot()
    def set_expand_state(self, expanded: bool):

        if expanded:
            self.title_label.set_html_title(unicode_symbol="\u25BC", title=self._title, subtitle=self._subtitle)
        else:
            self.title_label.set_html_title(unicode_symbol="\u25B6", title=self._title, subtitle=self._subtitle)

        self.content_group_box.setVisible(expanded)

    def add_widget(self, widget: QWidget):
        # For simple VBoxLayout
        self.content_layout.addWidget(widget)

    def insert_layout(self, layout: QLayout, index: int = 0):
        # For complex layout
        self.content_layout.insertLayout(index, layout)


class DefaultCollapsibleSubSection(QWidget, WidgetLifecycleMixin):
    _is_final_component = True

    def __init__(self, title: str, subtitle: str | None = None, parent=None):
        super().__init__(parent)
        self._title = title
        self._subtitle = subtitle
        self._init_ui()

    @override
    def _create_widgets(self) -> None:
        self.toggle_button = QPushButton()
        self.toggle_button.setObjectName("CollapsibleSectionTitle")
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)

        self.title_label = _CollapsibleSectionTitle(title_size=12)
        self.title_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)  # type: ignore

        self.content_container = QWidget()
        self.content_container.setVisible(False)

    @override
    def _assemble_layout(self) -> None:
        self.button_layout = QVBoxLayout(self.toggle_button)
        self.button_layout.setContentsMargins(0, 0, 0, 0)

        self.button_layout.addWidget(self.title_label)

        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)

        section_layout = QVBoxLayout(self)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.addWidget(self.toggle_button)
        section_layout.addWidget(self.content_container)

        # To initialize the section. Can be overridden by calling the method set_expand_state in the page.
        self.set_expand_state(expanded=False)

    @override
    def _connect_internal_signals(self) -> None:
        self.toggle_button.clicked.connect(self.set_expand_state)

    @Slot()
    def set_expand_state(self, expanded: bool):
        if expanded:
            self.title_label.set_html_title(unicode_symbol="\u25BC", title=self._title, subtitle=self._subtitle)
        else:
            self.title_label.set_html_title(unicode_symbol="\u25B6", title=self._title, subtitle=self._subtitle)

        self.content_container.setVisible(expanded)

    def add_widget(self, widget: QWidget):
        # For simple VBoxLayout
        self.content_layout.addWidget(widget)

    def insert_layout(self, layout: QLayout, index: int = 0):
        # For complex layout
        self.content_layout.insertLayout(index, layout)
