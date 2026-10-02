from pathlib import Path
from typing import override

from PySide6.QtCore import QUrl

from src.py_correction.ui.feedbacks.messages.base_message import BaseMessageText
from src.py_correction.ui.feedbacks.styles.base_style import HREF_STYLE, UL_STYLE


class EvaluationFormCompletedMessage(BaseMessageText):

    def __init__(self, evaluation_title: str):
        self.evaluation_title = evaluation_title

    @property
    @override
    def title(self) -> str:
        return "Importation manuelle réussie d'une évaluation"

    @property
    @override
    def html_text(self) -> str:
        return f"""<p>L'évaluation {self.evaluation_title} a été créée manuellement avec succès. Vous pouvez 
               maintenant gérer l'évaluation dans la section Gestion des évaluations. <br> 
               À noter que l'importation manuelle ne permet pas de lier l'évaluation à GeNote, mais permet tout de 
               même de valider les références, organiser les fichiers et générer des grilles de correction 
               automatique.</p>"""


class EvaluationTemplateCompletedMessage(BaseMessageText):

    def __init__(self, template_directory: str | Path, original_path: str | Path):
        super().__init__()
        self._original_path = Path(original_path).resolve()
        self._original_parent_path = self._original_path.parent
        self._template_directory = Path(template_directory).resolve()

    @property
    @override
    def title(self) -> str:
        return "Importation réussie des gabarits de correction"

    @property
    @override
    def html_text(self) -> str:
        template_directory_url = QUrl.fromLocalFile(self._template_directory).toString()
        original_parent_path_url = QUrl.fromLocalFile(self._original_parent_path).toString()

        return f"""<p>Votre gabarit de correction a été importé avec succès dans le répertoire <br> 
                <a {HREF_STYLE} href='{template_directory_url}'>{self._template_directory}</a> <br>
                Celui-ci sera utilisé pour générer des grilles de correction pour chaque étudiant. 
                Les instructions pour configurer le gabarit sont dans la page À propos et instructions - 
                Section <i>Guide de démarrage rapide</i></p> 
                Le gabarit de correction original est toujours disponible dans le répertoire <br>
                <a {HREF_STYLE} href='{original_parent_path_url}'>{self._original_parent_path}</a>.</p>"""


class GeNoteFailedMessage(BaseMessageText):

    def __init__(self, wrong_filename: str):
        super().__init__()
        self._wrong_filename = wrong_filename

    @property
    @override
    def title(self) -> str:
        return "Erreur d'importation du fichier GeNote"

    @property
    @override
    def html_text(self) -> str:
        return f"""<p>Attention, vous devez importer le fichier en provenance de GeNote qui a le format 
                  notes-SIGXXXGrYY-S20XX.xlsx. <br>
                  Vous avez importé un fichier avec le format {self._wrong_filename} 
                  qui est invalide.</p>"""


class GeNoteCompletedMessage(BaseMessageText):

    def __init__(self, new_source_path: Path, grade_directory_path: Path):
        self._new_source_path = Path(new_source_path).resolve()
        self._new_source_parent_directory = self._new_source_path.parent
        self._new_source_parent_filename = self._new_source_path.name
        self._grade_directory_path = Path(grade_directory_path).resolve()

    @property
    @override
    def title(self) -> str:
        return "Importation réussie du fichier GeNote"

    @property
    @override
    def html_text(self) -> str:
        new_source_parent_path_url = QUrl.fromLocalFile(self._new_source_parent_directory).toString()
        grade_directory_path_url = QUrl.fromLocalFile(self._grade_directory_path).toString()
        return f"""<p>Attention, le fichier qui sera modifié par l'application et qui devra être importé dans 
                Genote est maintenant dans le répertoire <br>
                <a {HREF_STYLE} href='{grade_directory_path_url}'>{self._grade_directory_path}</a>
                </p>
                <p> Une copie de sauvegarde du fichier que vous avez importé est toujours disponible dans le répertoire 
                original <br>
                <a {HREF_STYLE} href='{new_source_parent_path_url}'>{self._new_source_parent_directory}</a> <br> 
                sous le nom <br> {self._new_source_parent_filename}</p>"""


class CourseFormCompletedMessage(BaseMessageText):

    def __init__(self, course_code: str, course_name: str, course_semester: str, course_group: str):
        super().__init__()
        self._course_code = course_code
        self._course_name = course_name
        self._course_semester = course_semester
        self._course_group = course_group

    @property
    @override
    def title(self) -> str:
        return "Importation manuelle réussie d'un cours"

    @property
    @override
    def html_text(self) -> str:
        return f"""<p>Le cours {self._course_code} - {self._course_name} pour la session {self._course_semester} et le 
                groupe {self._course_group} a été importé manuellement avec succès. Veuillez noter que plusieurs 
                fonctionnalités de l'application, comme l'importation automatique des notes, ne seront pas possibles 
                sans un fichier GeNote. <br> Si vous souhaitez utiliser un fichier GeNote, veuillez archiver cette 
                entrée manuelle et recommencer via l'importation automatique.</p>"""


class StudentFormCompletedMessage(BaseMessageText):

    def __init__(self, cip: str, first_name: str, last_name: str):
        super().__init__()
        self._cip = cip
        self._first_name = first_name
        self._last_name = last_name

    @property
    @override
    def title(self) -> str:
        return "Importation manuelle réussie d'un étudiant"

    @property
    @override
    def html_text(self) -> str:
        return f"""<p>L'importation manuelle pour {self._last_name}, {self._first_name} ({self._cip}) a été effectuée 
                avec succès. Veuillez noter qu'il sera impossible d'attribuer les notes automatiquement dans le fichier 
                GeNote pour une importation manuelle. </p>"""


class MoodleImportCompletedMessage(BaseMessageText):

    def __init__(self, source_zip_file: Path, target_extraction_directory: Path, submission_archive_directory: Path,
                 new_archive_name: str):
        self._source_zip_file = Path(source_zip_file).resolve()
        self._target_extraction_path = Path(target_extraction_directory).resolve()

        self._submission_archive_path = Path(submission_archive_directory).resolve()
        self._new_archive_name = new_archive_name

    @property
    @override
    def title(self) -> str:
        return "Importation réussie du fichier zip"

    @property
    @override
    def html_text(self) -> str:
        target_extraction_path_url = QUrl.fromLocalFile(self._target_extraction_path).toString()
        submission_archive_path_url = QUrl.fromLocalFile(self._submission_archive_path).toString()

        return f"""<p>Le fichier <br> {self._source_zip_file} a été décompressé avec succès dans le répertoire <br>
                <a {HREF_STYLE} href='{target_extraction_path_url}'>{self._target_extraction_path}</a>
                </p>
                <p> Une copie du fichier zip est maintenant disponible dans le répertoire 
                <br>
                <a {HREF_STYLE} href='{submission_archive_path_url}'>{self._submission_archive_path}</a>
                <br> sous le nom suivant (la date et l'heure ont été ajoutées au nom du fichier) <br> 
                {self._new_archive_name}</p>"""


class MakeCorrectionFileCompletedMessage(BaseMessageText):

    def __init__(self, student_names: list[str], evaluation_correction_directory: Path):
        self._student_names = student_names
        self._evaluation_correction_directory = Path(evaluation_correction_directory).resolve()

    @property
    @override
    def title(self) -> str:
        return "Création réussie de fichiers de correction"

    @property
    @override
    def html_text(self) -> str:
        evaluation_correction_directory_url = QUrl.fromLocalFile(self._evaluation_correction_directory).toString()

        if len(self._student_names) > 10:
            file_count = len(self._student_names)
            item_html_list = "".join(f"<li> {student_name} </li>" for student_name in self._student_names[:10])
            return f"""<p>Les grilles de correction ont été générées avec succès pour les étudiants suivants :<br><br>
                    <ul {UL_STYLE}>
                    {item_html_list}
                    </ul><br> Ainsi que {file_count - 10} autres étudiants. <br>
                    Les dossiers de corrections sont maintenant disponibles dans ce répertoire <br>
                    <a {HREF_STYLE} href='{evaluation_correction_directory_url}'>
                    {self._evaluation_correction_directory}</a>"""
        else:
            item_html_list = "".join(f"<li> {student_name} </li>" for student_name in self._student_names)
            return f"""<p>Les grilles de correction ont été générées avec succès pour les étudiants suivants :<br><br>
                    <ul {UL_STYLE}>
                    {item_html_list}
                    </ul><br>
                    Les dossiers de corrections sont maintenant disponibles dans ce répertoire <br>
                    <a {HREF_STYLE} href='{evaluation_correction_directory_url}'>
                    {self._evaluation_correction_directory}</a>"""


class MakeCorrectionFileFailedMessage(BaseMessageText):

    def __init__(self, student_names: list[str], evaluation_correction_directory: Path):
        self._student_names = student_names
        self._evaluation_correction_directory = Path(evaluation_correction_directory).resolve()

    @property
    @override
    def title(self) -> str:
        return "Création non effectuée de fichiers de correction"

    @property
    @override
    def html_text(self) -> str:
        evaluation_correction_directory_url = QUrl.fromLocalFile(self._evaluation_correction_directory).toString()

        if len(self._student_names) > 10:
            file_count = len(self._student_names)
            item_html_list = "".join(f"<li> {student_name} </li>" for student_name in self._student_names[:10])
            return f"""<p>Les grilles de correction pour ces étudiants existent déjà<br><br>
                    <ul {UL_STYLE}>
                    {item_html_list}
                    </ul><br> Ainsi que pour {file_count - 10} autres étudiants. <br>
                    Vous devez supprimer manuellement le dossier des étudiants dans ce répertoire 
                    si vous souhaitez recommencer l'importation <br>
                    <a {HREF_STYLE} href='{evaluation_correction_directory_url}'>
                    {self._evaluation_correction_directory}</a>"""
        else:
            item_html_list = "".join(f"<li> {student_name} </li>" for student_name in self._student_names)
            return f"""<p>Les grilles de correction pour ces étudiants existent déjà<br><br>
                    <ul {UL_STYLE}>
                    {item_html_list}
                    </ul><br>
                    Vous devez supprimer manuellement le dossier des étudiants dans ce répertoire 
                    si vous souhaitez recommencer l'importation <br>
                    <a {HREF_STYLE} href='{evaluation_correction_directory_url}'>
                    {self._evaluation_correction_directory}</a>"""

class GeNoteUpdateMessage(BaseMessageText):

    def __init__(self, failed_operations: list[str] | None, evaluation_title: str):
        self._failed_operations = failed_operations
        self._evaluation_title = evaluation_title

    @property
    @override
    def title(self) -> str:
        return "Mise à jour du fichier GeNote"

    @property
    @override
    def html_text(self) -> str:
        # None return if the operation has failed
        if self._failed_operations is None:
            return f"""La mise à jour du fichier GeNote a échoué pour l'évaluation {self._evaluation_title}.
             Veuillez-vous assurez que les répertoires et la feuille GeNote n'ont pas été modifiée après 
             l'importation du cours."""

        # Empty list returned if operation successful
        if not self._failed_operations:
            return f"""Le fichier GeNote a été mis à jour avec succès pour l'évaluation {self._evaluation_title}. 
            L'ensemble des transactions est disponible dans la console. <br> 
            Veuillez faire une vérification manuelle avant d'importer le fichier dans GeNote pour vous assurer 
            que les notes correspondent bien à l'évaluation et à l'étudiant. <br> 
            Une mauvaise configuration des mots clés à la Page 2. Gestion des évaluations ou une disparité entre le 
            nom de l'étudiant sur Moodle et GeNote peuvent introduire des erreurs. 
            """

        elif len(self._failed_operations) > 10:
            file_count = len(self._failed_operations)
            item_html_list = "".join(f"<li> {student_name} </li>" for student_name in self._failed_operations[:10]) # type: ignore
            return f"""<p>L'ajout de la note dans le fichier GeNote pour l'évaluation {self._evaluation_title} 
                    a échoué pour les étudiants suivants :<br><br>
                    <ul {UL_STYLE}>
                    {item_html_list}
                    </ul><br> Ainsi que {file_count - 10} autres étudiants. <br>
                    Veuillez faire une vérification manuelle. Une mauvaise configuration des mots 
                    clés à la Page 2. Gestion des évaluations ou une disparité entre le nom de l'étudiant sur Moodle 
                    et GeNote peuvent introduire des erreurs.
                    """
        else:
            item_html_list = "".join(f"<li> {student_name} </li>" for student_name in self._failed_operations) # type: ignore
            return f"""<p>L'ajout de la note dans le fichier GeNote pour l'évaluation {self._evaluation_title} 
                    a échoué pour les étudiants suivants :<br><br>
                    <ul {UL_STYLE}>
                    {item_html_list}
                    </ul><br>
                    Veuillez faire une vérification manuelle. Une mauvaise configuration des mots 
                    clés à la Page 2. Gestion des évaluations ou une disparité entre le nom de l'étudiant sur Moodle 
                    et GeNote peuvent introduire des erreurs.
                    """


class MoodleArchiveCompletedMessage(BaseMessageText):

    def __init__(self, source_file: Path | None, destination_directory: Path | None):

        self._source_file_path = source_file
        self._destination_directory_path = destination_directory

    @property
    @override
    def title(self) -> str:
        return "Archivage réussie du dossier de correction pour Moodle"

    @property
    @override
    def html_text(self) -> str:
        if self._source_file_path is None or self._destination_directory_path is None:
            return """Le répertoire de correction n'a pas pu être archivé. Assurez-vous que les répertoires n'ont pas
                      été modifiés suite à la création du cours."""
        else:

            source_file_path_url = QUrl.fromLocalFile(self._source_file_path.resolve()).toString()
            destination_directory_path_url = QUrl.fromLocalFile(self._destination_directory_path.resolve()).toString()

            return f"""<p>Le répertoire <br>
                    <a {HREF_STYLE} href='{source_file_path_url}'>{self._source_file_path}</a> <br>
                    a été compressé avec succès vers le répertoire des archives Moodle
                    <br>
                    <a {HREF_STYLE} href='{destination_directory_path_url}'>{self._destination_directory_path}</a></p>
                    <p>Vous pouvez utiliser le fichier .zip pour déposer les rétroactions en lot dans Moodle 
                    (voir le <i>Guide de démarrage rapide</i> dans la page "À propos et instructions" pour la procédure) 
                    </p>
                    """


class CourseArchiveCompletedMessage(BaseMessageText):

    def __init__(self, course_name: str | None, new_directory: Path | None):
        self._course_name = course_name
        self._new_directory = new_directory

    @property
    @override
    def title(self) -> str:
        return "Résultat de l'archivage du cours"

    @property
    @override
    def html_text(self) -> str:
        if self._new_directory is None:
            return """L'archivage du cours a échoué. Veuillez vérifier que vous avez la permission de modifier le 
                      répertoire de destination."""

        new_directory_url = QUrl.fromLocalFile(self._new_directory.resolve()).toString()
        return f"""L'archivage du cours {self._course_name} est complété. Vous pouvez restaurer le cours ou 
                   le supprimer manuellement de votre ordinateur dans le répertoire suivant : <br>
                   <a {HREF_STYLE} href='{new_directory_url}'>{self._new_directory}</a>"""

class CourseRestoreCompletedMessage(BaseMessageText):

    def __init__(self, course_name: str | None, new_directory: Path | None):
        self._course_name = course_name
        self._new_directory = new_directory

    @property
    @override
    def title(self) -> str:
        return "Résultat de la restauration du cours"

    @property
    @override
    def html_text(self) -> str:
        if self._new_directory is None:
            return """La restauration du cours a échoué. Veuillez vérifier que vous avez la permission de modifier le 
                      répertoire de destination."""

        new_directory_url = QUrl.fromLocalFile(self._new_directory.resolve()).toString()
        return f"""La restauration du cours {self._course_name} est complété. Vous pouvez désormais sélectionner le 
                   cours dans l'application et consulter les documents dans le répertoire suivant : <br>
                   <a {HREF_STYLE} href='{new_directory_url}'>{self._new_directory}</a>"""