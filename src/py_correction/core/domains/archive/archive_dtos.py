from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ArchiveResponseDTO:
    course_name: str | None
    new_directory: Path | None