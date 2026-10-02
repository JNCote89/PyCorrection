from enum import StrEnum


class ReferenceVerificationStatusEnum(StrEnum):
    VALID = "Valide"
    INVALID = "Invalide"
    TO_CHECK = "À vérifier"


class EvidenceLevelEnum(StrEnum):
    HIGH = "Élevé"
    MODERATE = "Moyen"
    LOW = "Faible"
    VERY_LOW = "Très faible"
    NO_EVIDENCE = "Aucun (Opinion d'experts / Anecdote)"


class RelevanceLevelEnum(StrEnum):
    RELEVANT = "Pertinent et aligné"
    MISALIGNED = "Pertinent, mais mal aligné"
    IRRELEVANT = "Non pertinent"


class ReferenceTypeEnum(StrEnum):
    SCIENTIFIC_PEER_REVIEW = "Scientifique (Révisé par les pairs)"
    SCIENTIFIC_NO_REVIEW = "Scientifique (Non révisé par les pairs)"
    GREY = "Grise"
