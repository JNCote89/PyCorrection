from decimal import Decimal
import logging
from pathlib import Path

from src.py_correction.engine.excel import excel_operations
from src.py_correction.engine.helpers import decimal_helpers

logger = logging.getLogger(__name__)


def return_student_grade_from_correction_file(template_path: Path, template_sheet: str | None, row_keyword: str | None,
                                              column_keyword: str | None) -> Decimal | None:
    if not template_sheet or not row_keyword or not column_keyword:
        logger.info(f"Le gabarit n'est pas configurée. Il manque la sélection d'une feuille Excel et des mots clés.")
        return None

    with excel_operations.safe_load_workbook(excel_path=template_path, data_only=True, read_only=True) as wb:
        if wb is None:
            logger.warning(f"""Le fichier de correction {template_path} n'a pas pu être chargé. 
                               Assurez-vous qu'il n'a pas été supprimé. """)
            return None

        ws_student_grade = wb[template_sheet]

        note_cell_row = None
        note_cell_column = None

        for row_grade in ws_student_grade.iter_rows():
            for cell_grade in row_grade:
                if cell_grade.value == row_keyword:
                    note_cell_row = cell_grade.row
                if cell_grade.value == column_keyword:
                    note_cell_column = cell_grade.column

                if note_cell_row and note_cell_column:

                    final_grade = ws_student_grade.cell(row=note_cell_row, column=note_cell_column).value

                    if isinstance(final_grade, (int, float)):
                        return decimal_helpers.safe_decimal(final_grade)
                    else:
                        logger.info(f"""La cellule pour extraire la note ne contient pas une valeur valide pour la 
                                        convertir en nombre : {final_grade}. Veuillez revérifier vos mots clés pour le
                                        gabarit {template_path}. 
                                        Mot clé pour la rangé : {row_keyword}.
                                        Mot clé pour la colonne: {column_keyword}""")

        return None