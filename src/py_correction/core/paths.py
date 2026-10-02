from importlib.resources import files
import logging
import os
from pathlib import Path
import sys

from src.py_correction import assets

logger = logging.getLogger(__name__)


def get_base_dir() -> Path:
    if "APPIMAGE" in os.environ:
        return Path(os.environ["APPIMAGE"]).resolve().parent

    if getattr(sys, "frozen", False) or "__compiled__" in globals():
        return Path(sys.argv[0]).resolve().parent

    return Path(sys.argv[0]).resolve().parent.parent.parent


class UserDirectories:
    def __init__(self, base_dir: Path):
        self.data_dir = base_dir / "data"

    def _ensure_dir(self, name: str) -> Path:
        directory = self.data_dir / name
        try:
            directory.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            logger.warning(f"""Il n'est pas possible d'écrire dans le répertoire '{directory}'. Assurez-vous que le 
                               programme soit dans un répertoire où vous avez la permission de modifier des fichiers 
                               (e.g., Mes documents).
                            """)
        return directory

    def get_user_profile_directory(self) -> Path:
        return self._ensure_dir("user_profile")

    def get_log_directory(self) -> Path:
        return self._ensure_dir("logs")

    def get_database_directory(self) -> Path:
        return self._ensure_dir("database")


BASE_DIR = get_base_dir()
_user_directory = UserDirectories(BASE_DIR)

USER_PROFILE_DIRECTORY = _user_directory.get_user_profile_directory()
LOGS_DIRECTORY = _user_directory.get_log_directory()
DATABASE_DIRECTORY = _user_directory.get_database_directory()

ASSETS_DIR = Path(str(files(assets)))

CSL_STYLES = ASSETS_DIR / "csl"
FONT_DIRECTORY = ASSETS_DIR / "fonts"
THEME_DIRECTORY = ASSETS_DIR / "theme"
INSTRUCTION_IMAGES = ASSETS_DIR / "instruction_images"
LOGO = ASSETS_DIR / "logo"