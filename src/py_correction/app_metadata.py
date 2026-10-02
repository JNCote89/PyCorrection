from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AppMetadata:
    NAME: str = "PyCorrection"
    VERSION: str = "Beta"
    AUTHOR: str = "Jean-Nicolas Côté"
    CONTACT_EMAIL = "jean-nicolas.cote@usherbrooke.ca"
    DESCRIPTION: str = """Manage courses, evaluations and students for each semester. Also check references against 
                          CrossRef and OpenAlex database to detect AI plagiarism and hallucinations."""


METADATA = AppMetadata()
