import logging
from pathlib import Path
from typing import TYPE_CHECKING

from src.py_correction.core.domains.course_path.course_path_dtos import ArchiveCoursePathResponseDTO
from src.py_correction.database.archive.archive_CRUD import ArchiveCourseCRUD

if TYPE_CHECKING:
    from sqlalchemy.orm import sessionmaker
    from src.py_correction.core.event_bus import EventBus

logger = logging.getLogger(__name__)


class ArchiveServices:

    def __init__(self, session_factory: "sessionmaker", event_bus: "EventBus"):
        self._session_factory = session_factory

        self._archive_CRUD = ArchiveCourseCRUD()

        self._event_bus = event_bus

    def archive_course(self, course_id: int, archive_database_path: Path) -> None:
        with self._session_factory.begin() as session:
            self._archive_CRUD.archive_course(main_session=session,
                                              course_id=course_id,
                                              archive_database_path=str(archive_database_path))
        self._event_bus.database.courseArchived.emit(course_id)

    def restore_course(self, db_path: Path) -> ArchiveCoursePathResponseDTO:
        with self._session_factory.begin() as session:
            course_orm = self._archive_CRUD.restore_course(main_session=session,
                                                           archive_database_path=str(db_path))
            session.flush()

            return ArchiveCoursePathResponseDTO(course_path_id=course_orm.course_path.id, # type: ignore
                                                course_id=course_orm.id,  # type: ignore
                                                user_root_directory=course_orm.course_path.user_root_directory, # type: ignore
                                                course_root_path=course_orm.course_path.course_root_path, # type: ignore
                                                semester=course_orm.semester, # type: ignore
                                                course_code=course_orm.code, # type: ignore
                                                group=course_orm.group) # type: ignore
