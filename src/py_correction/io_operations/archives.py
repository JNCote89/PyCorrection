from datetime import datetime
import logging
import os
from pathlib import Path
import shutil
import tempfile
import zipfile

from src.py_correction.io_operations.filesystem import get_top_directory_names

logger = logging.getLogger(__name__)


def get_archive_top_directory_names(archive_path: Path) -> list[str] | None:
    if archive_path.exists():
        top_level_directories = set()

        with zipfile.ZipFile(archive_path, "r") as zf:
            all_members = zf.infolist()
            for member in all_members:
                top_level_directory = Path(member.filename).parts[0]
                top_level_directories.add(top_level_directory)

        return list(top_level_directories)

    return None


def get_overwrite_directory_name_conflicts(archives_path: Path, target_path: Path) -> list[str] | None:
    if archives_path.exists() and target_path.exists():
        archive_top_directory_names = get_archive_top_directory_names(archive_path=archives_path)
        submission_directory_names = get_top_directory_names(directory=target_path)

        name_conflicts = [directory_name for directory_name in submission_directory_names  # noqa
                          if directory_name in archive_top_directory_names]
        if name_conflicts:
            return name_conflicts

    return None


def extract_archives(archive_path: Path | None, target_directory: Path | None,
                     skip_directory_names: list[str] | None = None) -> None:
    if not archive_path or not target_directory:
        logger.warning("Archive path or target directory is missing.")
        return

    archive_path = Path(archive_path)
    target_directory = Path(target_directory)
    skip_directory_names = skip_directory_names or []
    try:
        target_directory.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(archive_path, "r") as zf:
            for member in zf.infolist():
                path = Path(member.filename)
                top_level_name = path.parts[0] if path.parts else ""

                if top_level_name not in skip_directory_names:
                    zf.extract(member, target_directory)

    except FileNotFoundError:
        logger.warning("The selected zip file or target directory no longer exists.")
    except NotADirectoryError:
        logger.warning("A path conflict occurred: a required directory is actually a file.")


def move_to_archives_with_timestamp(source_file: Path, archive_directory: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_archive_name = f"{source_file.stem}_{timestamp}{source_file.suffix}"

    destination = archive_directory / new_archive_name
    shutil.move(source_file, destination)

    return destination


def archive_and_move_directory(source_directory: Path, destination_directory: Path) -> Path:
    destination_directory.mkdir(parents=True, exist_ok=True)

    archive_path = destination_directory / f"{source_directory.name}.zip"

    with zipfile.ZipFile(archive_path, mode="w", compression=zipfile.ZIP_DEFLATED, ) as zipf:
        for path in source_directory.rglob("*"):
            if not path.is_file():
                continue
            arcname = path.relative_to(source_directory).as_posix()
            zipf.write(path, arcname=arcname)

    return archive_path


def archive_and_remove(source_directory: str | Path) -> Path | None:
    source = Path(source_directory).resolve()

    if not source.is_dir():
        logger.warning(f"Source path {source} is not a valid directory.")

    archive_path = source.with_suffix(".zip")

    if archive_path.exists():
        logger.warning(f"Archive already exists: {archive_path}")

    with tempfile.NamedTemporaryFile(dir=source.parent, prefix=f".{source.name}.", suffix=".tmp", delete=False
                                     ) as temp_file:
        temp_archive = Path(temp_file.name)

    try:
        with zipfile.ZipFile(temp_archive, mode="w", compression=zipfile.ZIP_DEFLATED,) as zipf:
            for path in source.rglob("*"):
                if not path.is_file():
                    continue

                archive_name = path.relative_to(source).as_posix()
                zipf.write(path, arcname=archive_name)

        with zipfile.ZipFile(temp_archive, mode="r") as zipf:
            corrupt_file = zipf.testzip()

            if corrupt_file is not None:
                logger.warning(f"Archive verification failed on file: {corrupt_file}. Directory preserved.")

        os.replace(temp_archive, archive_path)

        shutil.rmtree(source)

        return archive_path

    except Exception:
        temp_archive.unlink(missing_ok=True)
