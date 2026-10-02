from datetime import datetime
import logging
import os
from pathlib import Path
import shutil

logger = logging.getLogger(__name__)

def check_writable_path(path: Path) -> Path | None:
    if not os.path.isdir(path):
        logger.info(f"""Il n'est pas possible de choisir le répertoire {path}, car ce n'est pas un répertoire. 
                        Veuillez choisir un répertoire comme "Mes documents". """)
        return None

    elif not os.access(path, os.W_OK):
        logger.info(f"""Il n'est pas possible de choisir le répertoire {path}, car vous n'avez pas le niveau de 
                       privilège requis pour modifier ce répertoire. Veuillez choisir un répertoire comme 
                       "Mes documents". """)
        return None
    else:
        return path


def get_top_directory_names(directory: Path) -> list[str] | None:
    if directory.exists():
        return [path.name for path in Path(directory).iterdir() if path.is_dir()]

    return None

def make_directories(directories: list[Path]):
    directories = directories or []

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def copy_and_rename_source(file_path: Path, destination_path: Path,
                           source_suffix: str = "_copie_de_sauvegarde") -> Path:
    shutil.copy(file_path, destination_path)

    new_source_path = file_path.with_stem(f"{file_path.stem}{source_suffix}")
    file_path.rename(new_source_path)
    return new_source_path


def move_with_timestamp(source_directory: Path, destination_directory: Path):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.move(source_directory, f"{destination_directory}_{timestamp}")
