from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtCore import QThread

class WorkerRegistry:

    def __init__(self):
        self._active_workers = {}

    def register(self, name: str, worker: "QThread"):
        self._active_workers[name] = worker
        worker.finished.connect(lambda: self.unregister(name))

    def unregister(self, name: str):
        self._active_workers.pop(name, None)

    def cancel_all(self):
        for worker in list(self._active_workers.values()):
            if worker.isRunning():
                worker.requestInterruption()

    def wait_all(self, msecs: int) -> bool:
        all_finished = True
        for worker in list(self._active_workers.values()):
            if worker.isRunning():
                if not worker.wait(msecs):
                    worker.terminate()
                    all_finished = False
        return all_finished
