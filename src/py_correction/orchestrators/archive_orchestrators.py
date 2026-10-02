from datetime import datetime
from enum import StrEnum
import json
import logging
from pathlib import Path
import shutil
import tempfile
from typing import TYPE_CHECKING
import zipfile

from src.py_correction import app_metadata
from src.py_correction.core.domains.archive.archive_dtos import ArchiveResponseDTO
from src.py_correction.core.domains.course_path.course_path_dtos import (CoursePathCreateDTO)
from src.py_correction.core.domains.shared.shared_enums import AppDirectories
from src.py_correction.core.event_bus import EventBus
from src.py_correction.io_operations import archives
from src.py_correction.io_operations.filesystem import make_directories
from src.py_correction.services.domains.course_path.course_path_mappers import to_update_course_path_dto
from src.py_correction.utils import date_format

if TYPE_CHECKING:
    from src.py_correction.core.settings_manager import SettingsManager
    from src.py_correction.services.domains.course.course_services import CourseServices
    from src.py_correction.services.domains.course_path.course_path_services import CoursePathServices
    from src.py_correction.services.domains.archive.archive_services import ArchiveServices

logger = logging.getLogger(__name__)


class ManifestFields(StrEnum):
    APP_NAME = "app_name"
    VERSION = "version"
    COURSE_ID = "course_id"
    COURSE_ARCHIVE_NAME = "course_archive_name"
    CREATED_AT = "create_at"


class ArchiveOrchestrator:

    def __init__(self, course_services: "CourseServices", archive_services: "ArchiveServices",
                 course_path_services: "CoursePathServices",
                 settings_manager: "SettingsManager", event_bus: "EventBus"):
        self._course_services = course_services
        self._archive_services = archive_services
        self._settings_manager = settings_manager
        self._course_path_services = course_path_services

        self._event_bus = event_bus

    def get_archive_path(self) -> Path | None:
        py_correction_path = self._settings_manager.restored_settings.user_root_directory / AppDirectories.PYCORRECTION
        if py_correction_path.exists():
            archive_path = py_correction_path / AppDirectories.ARCHIVES
            archive_path.mkdir(parents=True, exist_ok=True)
            return archive_path

        return None

    def archive_course(self, course_id: int) -> ArchiveResponseDTO:
        course_archive_name = self._course_services.get_course_archive_name(course_id=course_id)
        archive_path = self.get_archive_path()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if archive_path and course_archive_name:

            archive_course_path = archive_path / f"{course_archive_name}_{timestamp}"
            archive_course_path.mkdir(parents=True, exist_ok=True)

            archive_database_path = archive_course_path / f"{course_archive_name}.db"

            archive_manifest = self._get_archive_manifest(course_id=course_id,
                                                          course_archive_name=course_archive_name)

            course_directories = self._course_path_services.get_course_root_directory(course_id=course_id)

            self._archive_services.archive_course(course_id=course_id,
                                                  archive_database_path=archive_database_path)

            with open(f"{archive_course_path}/manifest.json", 'w', encoding='utf-8') as f:
                json.dump(archive_manifest, f)

            shutil.move(course_directories, archive_course_path)
            archives.archive_and_remove(source_directory=archive_course_path)

            self._clean_directories(course_directories=course_directories)

            return ArchiveResponseDTO(course_name=course_archive_name,
                                      new_directory=archive_path)

        return ArchiveResponseDTO(course_name=None,
                                  new_directory=None)

    def restore_course(self, zip_file_path: Path) -> ArchiveResponseDTO | None:
        is_valid_zip = self._validate_zip_file(zip_path=zip_file_path)

        if is_valid_zip:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                archives.extract_archives(archive_path=zip_file_path, target_directory=temp_path)

                course_archive_name = self._get_course_archive_name(zip_file_path=zip_file_path)
                db_path = temp_path / f"{course_archive_name}.db"

                archive_course_path_dto = self._archive_services.restore_course(db_path=db_path)

                course_path_create_dto = CoursePathCreateDTO(
                    user_root_directory=self._settings_manager.restored_settings.user_root_directory,
                    semester=archive_course_path_dto.semester,
                    course_code=archive_course_path_dto.course_code,
                    group=archive_course_path_dto.group)

                if (archive_course_path_dto.user_root_directory !=
                        self._settings_manager.restored_settings.user_root_directory):

                    update_dto = to_update_course_path_dto(course_path_create_dto,
                                                           course_id=archive_course_path_dto.course_id,
                                                           course_path_id=archive_course_path_dto.course_path_id)
                    self._course_path_services.update_course_path_from_dto(update_dto=update_dto)
                    destination_file = course_path_create_dto.course_root_path

                else:
                    destination_file = archive_course_path_dto.course_root_path

                for directory in temp_path.iterdir():
                    if directory.name.startswith(CoursePathCreateDTO.group_directory_name):
                        shutil.move(directory, destination_file)

                make_directories(course_path_create_dto.directories)
                self._event_bus.database.courseRestored.emit()

                return ArchiveResponseDTO(course_name=course_archive_name,
                                          new_directory=archive_course_path_dto.course_root_path)

        return ArchiveResponseDTO(course_name=None,
                                  new_directory=None)

    @staticmethod
    def _get_archive_manifest(course_id: int, course_archive_name: str) -> dict:
        time_now = date_format.get_utc_now()
        return {ManifestFields.APP_NAME: app_metadata.METADATA.NAME,
                ManifestFields.VERSION: app_metadata.METADATA.VERSION,
                ManifestFields.COURSE_ID: course_id,
                ManifestFields.COURSE_ARCHIVE_NAME: course_archive_name,
                ManifestFields.CREATED_AT: date_format.return_user_date_str(date=time_now),}

    @staticmethod
    def _validate_zip_file(zip_path: Path) -> bool:
        if not zipfile.is_zipfile(zip_path):
            return False

        with zipfile.ZipFile(zip_path, "r") as zf:
            namelist = zf.namelist()

            if "manifest.json" not in namelist:
                return False

            try:
                manifest_data = json.loads(zf.read("manifest.json").decode("utf-8"))
                if manifest_data.get(ManifestFields.APP_NAME) != app_metadata.METADATA.NAME:
                    return False

            except (json.JSONDecodeError, KeyError):
                return False

        return True

    @staticmethod
    def _get_course_archive_name(zip_file_path: Path) -> str:
        with zipfile.ZipFile(zip_file_path, "r") as zf:
            manifest_bytes = zf.read("manifest.json")
            manifest_data = json.loads(manifest_bytes.decode("utf-8"))
            return manifest_data.get("course_archive_name")

    @staticmethod
    def _clean_directories(course_directories: Path) -> None:
        for directory in (course_directories.parent, course_directories.parent.parent):
            try:
                directory.rmdir()
            except OSError:
                pass
