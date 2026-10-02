from pathlib import Path
from typing import override

from PySide6.QtCore import QUrl

from src.py_correction.ui.feedbacks.messages.base_message import BaseMessageText
from src.py_correction.ui.feedbacks.styles.base_style import HREF_STYLE, UL_STYLE


class FileOverwriteWarningMessage(BaseMessageText):

    def __init__(self, directory: Path, overwritten_filename: str):
        super().__init__()
        self._directory = directory
        self._overwritten_file = overwritten_filename

    @property
    @override
    def title(self) -> str:
        return "Confirmation du remplacement d'un fichier"

    @property
    @override
    def html_text(self) -> str:
        directory_url = QUrl.fromLocalFile(self._directory).toString()
        return f"""<p> Le fichier {self._overwritten_file} existe déjà dans le répertoire <br>
               <a {HREF_STYLE} href='{directory_url}'>{self._directory}</a> <br>
               Êtes-vous sûr de vouloir le remplacer?</p>"""


class DirectoryOverwriteWarningMessage(BaseMessageText):

    def __init__(self, overwritten_directories: list[str]):
        self._overwritten_directories = overwritten_directories

    @property
    @override
    def title(self) -> str:
        return "Confirmation du remplacement des fichiers déjà importés"

    @property
    @override
    def html_text(self) -> str:
        if len(self._overwritten_directories) == 1:
            filename = "".join(f"{directory}" for directory in self._overwritten_directories)
            return f"Êtes-vous sûr de vouloir importer le fichier <br> {filename}?"

        elif len(self._overwritten_directories) > 10:
            file_count = len(self._overwritten_directories)
            item_html_list = "".join(f"<li>{directory}</li>" for directory in self._overwritten_directories[:10])
            return f"""<p>Êtes-vous sûr de vouloir remplacer ces 10 fichiers ?<br><br>
                    <ul {UL_STYLE}>
                    {item_html_list}
                    </ul></p>[...] <br> Ainsi que {file_count - 10} autres?"""

        else:
            file_count = len(self._overwritten_directories)
            item_html_list = "".join(f"<li>{directory}</li>" for directory in self._overwritten_directories)
            return f"""Êtes-vous sûr de vouloir remplacer ces {file_count} fichiers ?<br><br>
                    <ul {UL_STYLE}>
                    {item_html_list}
                    </ul>"""


class BatchFileImportVerificationMessage(BaseMessageText):

    def __init__(self, imported_paths: list[Path]):
        super().__init__()
        self._imported_paths = imported_paths

    @property
    @override
    def title(self) -> str:
        return "Confirmation des fichiers à importer"

    @property
    @override
    def html_text(self) -> str:
        if len(self._imported_paths) == 1:
            filename = "".join(f"{path.name}" for path in self._imported_paths)
            return f"Êtes-vous sûr de vouloir importer le fichier <br> {filename}?"

        elif len(self._imported_paths) > 10:
            file_count = len(self._imported_paths)
            item_html_list = "".join(f"<li>{path.name}</li>" for path in self._imported_paths[:10])
            return f"""<p>Êtes-vous sûr de vouloir remplacer ces 10 fichiers ?<br><br>
                    <ul {UL_STYLE}>
                    {item_html_list}
                    </ul></p>[...] <br> Ainsi que {file_count - 10} autres?"""
        else:
            file_count = len(self._imported_paths)
            item_html_list = "".join(f"<li>{path.name}</li>" for path in self._imported_paths)
            return f"""Êtes-vous sûr de vouloir importer ces {file_count} fichiers ?<br><br>
                    <ul {UL_STYLE}>
                    {item_html_list}
                    </ul>"""
