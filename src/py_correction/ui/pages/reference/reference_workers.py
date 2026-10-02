from collections.abc import Callable
import logging

from PySide6.QtCore import QObject, QThread, Signal

from src.py_correction.core.domains.reference.reference_dtos import ReferenceTableDTO

logger = logging.getLogger(__name__)


class ReferenceVerificationWorker(QThread):
    progressBarStarted = Signal(int)
    progressBarUpdated = Signal(int)
    progressBarFinished = Signal()

    rowUpdated = Signal(ReferenceTableDTO)

    def __init__(self, reference_table_dtos: list[ReferenceTableDTO],
                 verification_function: Callable[[ReferenceTableDTO], ReferenceTableDTO],
                 parent: QObject | None = None):
        super().__init__(parent=parent)
        self._reference_table_dtos = reference_table_dtos
        self._verification_function = verification_function

    def run(self) -> None:
        try:
            self.progressBarStarted.emit(len(self._reference_table_dtos))

            for index, reference_table_dto in enumerate(self._reference_table_dtos):
                if reference_table_dto.verification_status:
                    continue

                if self.isInterruptionRequested():
                    break

                # To avoid spamming the CrossRef API endpoint and getting the IP temporarily blocked. The loop is for
                # being responsive to abort request.
                for _ in range(5):
                    if self.isInterruptionRequested():
                        break
                    QThread.msleep(100)

                if self.isInterruptionRequested():
                    break

                try:
                    reference_table_dto = self._verification_function(reference_table_dto=reference_table_dto) # type: ignore[arg-type]
                    self.rowUpdated.emit(reference_table_dto)

                except Exception as e:
                    logger.warning(e)

                self.progressBarUpdated.emit(index + 1)

        finally:
            self.progressBarFinished.emit()
