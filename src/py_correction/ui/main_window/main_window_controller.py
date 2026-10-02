from PySide6.QtCore import QSize

from src.py_correction.core.dependency_injection import container


class MainWindowController:

    def __init__(self):
        self._settings_manager = container.settings_manager()

    @property
    def window_size(self) -> QSize | None:
        if (self._settings_manager.restored_settings.window_width and
                self._settings_manager.restored_settings.window_height):
            return QSize(self._settings_manager.restored_settings.window_width,
                         self._settings_manager.restored_settings.window_height)

        return None

    @property
    def restored_page_label_selected(self) -> str | None:
        return self._settings_manager.restored_settings.page_label_selected

    @property
    def restored_main_splitter_sizes(self) -> list[int]:
        return self._settings_manager.restored_settings.main_splitter_sizes

    def save_settings(self, window_width: int, window_height: int, splitter_sizes: list[int] | None,
                      page_label_selected: str) -> None:
        self._settings_manager.save_settings_on_shutdown(window_width=window_width,
                                                         window_height=window_height,
                                                         splitter_sizes=splitter_sizes,
                                                         page_label_selected=page_label_selected)
