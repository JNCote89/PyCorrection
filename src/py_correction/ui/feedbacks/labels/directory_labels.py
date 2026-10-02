from pathlib import Path

from PySide6.QtCore import QUrl
from typing_extensions import override

from src.py_correction.ui.feedbacks.labels.base_label import BaseLabelText
from src.py_correction.ui.feedbacks.styles.base_style import HREF_STYLE


class SubmissionCountLabelText(BaseLabelText):

    def __init__(self, directory: Path | None = None, submission_count: int = 0):
        super().__init__()
        self._directory = directory
        self._submission_count = submission_count

    @property
    @override
    def html_text(self) -> str:
        if self._submission_count == 0 or not self._directory:
            return "Il n'y a pas de remises étudiantes pour cette évaluation. Veuillez les importer."

        directory_url = QUrl.fromLocalFile(self._directory).toString()
        return f"""Il y a {self._submission_count} remises pour cette évaluation dans le répertoire : <br>
                <a {HREF_STYLE} href='{directory_url}'>{self._directory}</a>"""


class TemplateFilenameLabelText(BaseLabelText):
    def __init__(self, template_filename: str | None = None):
        super().__init__()
        self._template_filename = template_filename

    @property
    @override
    def html_text(self) -> str:
        if self._template_filename is None:
            return """Aucun gabarit de correction associé à l'évaluation. Veuillez utiliser la Page 2. Gestion des 
                      évaluations pour en ajouter."""
        return f"Gabarit de correction pour l'évaluation :<br> {self._template_filename}"


class StudentEvaluationSubmissionLabelText(BaseLabelText):

    def __init__(self, directories: list[Path] | None = None):
        super().__init__()
        self._directories = directories

    @property
    @override
    def html_text(self) -> str:
        directories = self._directories
        if directories is None:
            return """Aucun répertoire créé pour la soumission de cette évaluation. Vous devez le créer en important les 
                    travaux étudiants à la Page 4. Gestion des remises étudiantes - 
                    Section <i>Importer les travaux remis</i>."""

        label = "Répertoire de la soumission" if len(directories) == 1 else "Répertoires des soumissions"
        url_list = "".join(f"<a {HREF_STYLE} href='{QUrl.fromLocalFile(directory).toString()}'>"
                           f"{directory}</a> <br>" for directory in directories)  # type: ignore
        return f"{label} :<br> {url_list}"


class StudentEvaluationCorrectionLabelText(BaseLabelText):

    def __init__(self, directory: Path | None = None):
        super().__init__()
        self._directory = directory

    @property
    @override
    def html_text(self) -> str:
        if self._directory is None:
            return """Aucun répertoire créé pour la correction de cette évaluation. Vous devez le créer à la 
                    Page 4. Gestion des remises étudiantes en cliquant sur le bouton "Générer les grilles de 
                    correction". """

        directory_url = QUrl.fromLocalFile(self._directory).toString()
        return f"Répertoire de la correction :<br> <a {HREF_STYLE} href='{directory_url}'>{self._directory}</a>"


class MoodleCorrectionArchiveLabelText(BaseLabelText):

    def __init__(self, archive_directory: Path | None = None, has_evaluation_correction_directory: bool = False):
        super().__init__()
        self._archive_directory = archive_directory
        self._has_evaluation_correction_directory = has_evaluation_correction_directory

    @property
    @override
    def html_text(self) -> str:
        if self._archive_directory is None or not self._has_evaluation_correction_directory:
            return """Il n'y a pas de répertoire pour la correction de cette évaluation. Veuillez le créer à la 
            Page 4. Gestion des remises étudiantes en cliquant sur le bouton "Générer les grilles de correction". """

        directory_url = QUrl.fromLocalFile(self._archive_directory).toString()
        return (f"Répertoire du fichier .zip à déposer dans Moodle : <br>"
                f"<a {HREF_STYLE} href='{directory_url}'>{self._archive_directory}</a>")


class GeNoteLabelText(BaseLabelText):

    def __init__(self, directory: Path | None = None, template_is_configured: bool = False,
                 has_evaluation_correction_directory: bool = False):
        super().__init__()
        self._directory = directory
        self._template_is_configured = template_is_configured
        self._has_evaluation_correction_directory = has_evaluation_correction_directory

    @property
    @override
    def html_text(self) -> str:
        if self._directory is None:
            directory_message = """Aucun fichier GeNote disponible pour le cours. Il faut utiliser l'importation automatique à 
                    partir d'un fichier GeNote à la Page 1. Création de cours pour bénéficier de cette fonction."""
        else:
            directory_url = QUrl.fromLocalFile(self._directory).toString()
            directory_message = f"""<p>Répertoire du fichier Excel GeNote à déposer dans GeNote : <br>
                                    <a {HREF_STYLE} href='{directory_url}'>{self._directory}</a></p>"""

        messages = [directory_message]

        if not self._template_is_configured:
            template_configuration_message = """
            <p>Le gabarit de correction n'est pas bien configuré pour cette évaluation. Assurez-vous d'avoir importé et 
            sélectionné une feuille Excel avec des mots clés à la Page 2. Gestion des évaluations dans la section 
            <i>Configuration du gabarit de correction associé à l'évaluation</i></p>"""
            messages.append(template_configuration_message)

        if not self._has_evaluation_correction_directory:
            correction_evaluation_message = """
            <p>Il n'y a pas de répertoire pour la correction de cette évaluation. Veuillez le créer à la 
            Page 4. Gestion des remises étudiantes en cliquant sur le bouton "Générer les grilles de correction".</p>"""
            messages.append(correction_evaluation_message)

        return "".join(messages)


class ArchivePathLabelText(BaseLabelText):

    def __init__(self, directory: Path | None):
        super().__init__()
        self._directory = directory

    @property
    @override
    def html_text(self) -> str:
        if self._directory is None:
            return """Aucun répertoire disponible pour les archives. Il faut créer un cours dans le répertoire racine 
                    (root directory) choisi dans les configurations en premier. """

        directory_url = QUrl.fromLocalFile(self._directory).toString()
        return f"Répertoire des cours archivés :<br> <a {HREF_STYLE} href='{directory_url}'>{self._directory}</a>"
