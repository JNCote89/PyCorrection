from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class MoodleImportCompletedResponseDTO:
    source_zip_file: Path
    target_extraction_directory: Path
    submission_archive_directory: Path
    new_archive_name: str


@dataclass(frozen=True, slots=True)
class MoodleMakeCorrectionFileResponseDTO:
    student_names: list[str]
    evaluation_correction_directory: Path
