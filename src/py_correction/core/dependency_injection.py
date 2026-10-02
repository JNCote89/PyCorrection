from src.py_correction.core.event_bus import EventBus
from src.py_correction.core.settings_manager import SettingsManager
from src.py_correction.core.theme_manager import ThemeManager
from src.py_correction.database import connection
from src.py_correction.orchestrators.archive_orchestrators import ArchiveOrchestrator
from src.py_correction.orchestrators.course_orchestrators import CourseFormOrchestrator, GeNoteOrchestrator
from src.py_correction.orchestrators.evaluation_orchestrators import EvaluationOrchestrator
from src.py_correction.orchestrators.grade_orchestrators import GradeOrchestrator
from src.py_correction.orchestrators.reference_orchestrators import ReferenceOrchestrator
from src.py_correction.orchestrators.submission_orchestrators import SubmissionOrchestrator
from src.py_correction.services.domains.archive.archive_services import ArchiveServices
from src.py_correction.services.domains.course.course_services import CourseServices
from src.py_correction.services.domains.course.course_student_services import CourseStudentServices
from src.py_correction.services.domains.course_path.course_path_services import CoursePathServices
from src.py_correction.services.domains.evaluation.evaluation_services import EvaluationServices
from src.py_correction.services.domains.reference.reference_services import ReferenceServices
from src.py_correction.services.domains.student.student_evaluation_services import StudentEvaluationServices
from src.py_correction.services.domains.student.student_services import StudentServices
from src.py_correction.services.path_resolver.path_resolver import PathResolver
from src.py_correction.services.workers.worker_registry import WorkerRegistry


class DependencyInjectionContainer:
    """
    Must use a pure Python container to avoid bugs with Nuitka. Third party libraries optimized in C are conflicting
    with object inspection when compiling.
    """

    def __init__(self) -> None:
        # --- Bus & Core ---
        self._event_bus: EventBus | None = None
        self._settings_manager: SettingsManager | None = None
        self._theme_manager: ThemeManager | None = None
        self._worker_registry: WorkerRegistry | None = None

        # --- Services ---
        self._course_services: CourseServices | None = None
        self._evaluation_services: EvaluationServices | None = None
        self._reference_services: ReferenceServices | None = None
        self._student_services: StudentServices | None = None
        self._course_path_services: CoursePathServices | None = None
        self._course_student_services: CourseStudentServices | None = None
        self._student_evaluation_services: StudentEvaluationServices | None = None
        self._archive_services: ArchiveServices | None = None
        self._path_resolver: PathResolver | None = None

        # --- Orchestrators ---
        self._course_genote_orchestrator: GeNoteOrchestrator | None = None
        self._course_form_orchestrator: CourseFormOrchestrator | None = None
        self._evaluation_orchestrator: EvaluationOrchestrator | None = None
        self._submission_orchestrator: SubmissionOrchestrator | None = None
        self._reference_orchestrator: ReferenceOrchestrator | None = None
        self._grade_orchestrator: GradeOrchestrator | None = None
        self._archive_orchestrator: ArchiveOrchestrator | None = None

    # --- Database Connection ---
    @staticmethod
    def session_factory_provider():
        return connection.SessionLocal

    # --- Bus & Core Singletons ---
    def event_bus(self) -> EventBus:
        if (instance := self._event_bus) is None:
            instance = self._event_bus = EventBus()
        return instance

    def settings_manager(self) -> SettingsManager:
        if (instance := self._settings_manager) is None:
            instance = self._settings_manager = SettingsManager(event_bus=self.event_bus())
        return instance

    def theme_manager(self) -> ThemeManager:
        if (instance := self._theme_manager) is None:
            instance = self._theme_manager = ThemeManager(event_bus=self.event_bus())
        return instance

    def worker_registry(self) -> WorkerRegistry:
        if (instance := self._worker_registry) is None:
            instance = self._worker_registry = WorkerRegistry()
        return instance

    # --- Services Singletons ---
    def course_services(self) -> CourseServices:
        if (instance := self._course_services) is None:
            instance = self._course_services = CourseServices(
                session_factory=self.session_factory_provider(),
                event_bus=self.event_bus())
        return instance

    def evaluation_services(self) -> EvaluationServices:
        if (instance := self._evaluation_services) is None:
            instance = self._evaluation_services = EvaluationServices(
                session_factory=self.session_factory_provider(),
                event_bus=self.event_bus())
        return instance

    def reference_services(self) -> ReferenceServices:
        if (instance := self._reference_services) is None:
            instance = self._reference_services = ReferenceServices(
                session_factory=self.session_factory_provider(),
                event_bus=self.event_bus())
        return instance

    def student_services(self) -> StudentServices:
        if (instance := self._student_services) is None:
            instance = self._student_services = StudentServices(
                session_factory=self.session_factory_provider(),
                event_bus=self.event_bus())
        return instance

    def course_path_services(self) -> CoursePathServices:
        if (instance := self._course_path_services) is None:
            instance = self._course_path_services = CoursePathServices(
                session_factory=self.session_factory_provider(),
                event_bus=self.event_bus())
        return instance

    def course_student_services(self) -> CourseStudentServices:
        if (instance := self._course_student_services) is None:
            instance = self._course_student_services = CourseStudentServices(
                session_factory=self.session_factory_provider(),
                event_bus=self.event_bus())
        return instance

    def student_evaluation_services(self) -> StudentEvaluationServices:
        if (instance := self._student_evaluation_services) is None:
            instance = self._student_evaluation_services = StudentEvaluationServices(
                session_factory=self.session_factory_provider(),
                event_bus=self.event_bus())
        return instance

    def archive_services(self) -> ArchiveServices:
        if (instance := self._archive_services) is None:
            instance = self._archive_services = ArchiveServices(
                session_factory=self.session_factory_provider(),
                event_bus=self.event_bus())
        return instance

    def path_resolver(self) -> PathResolver:
        if (instance := self._path_resolver) is None:
            instance = self._path_resolver = PathResolver(
                course_path_services=self.course_path_services(),
                evaluation_services=self.evaluation_services())
        return instance

    # --- Orchestrators Singletons ---
    def course_genote_orchestrator(self) -> GeNoteOrchestrator:
        if (instance := self._course_genote_orchestrator) is None:
            instance = self._course_genote_orchestrator = GeNoteOrchestrator(
                course_services=self.course_services(),
                student_services=self.student_services(),
                evaluation_services=self.evaluation_services(),
                course_path_services=self.course_path_services(),
                settings_manager=self.settings_manager(),
                event_bus=self.event_bus())
        return instance

    def course_form_orchestrator(self) -> CourseFormOrchestrator:
        if (instance := self._course_form_orchestrator) is None:
            instance = self._course_form_orchestrator = CourseFormOrchestrator(
                course_services=self.course_services(),
                course_path_services=self.course_path_services(),
                settings_manager=self.settings_manager(),
                event_bus=self.event_bus())
        return instance

    def evaluation_orchestrator(self) -> EvaluationOrchestrator:
        if (instance := self._evaluation_orchestrator) is None:
            instance = self._evaluation_orchestrator = EvaluationOrchestrator(
                settings_manager=self.settings_manager(),
                course_services=self.course_services(),
                evaluation_services=self.evaluation_services(),
                course_path_services=self.course_path_services())
        return instance

    def submission_orchestrator(self) -> SubmissionOrchestrator:
        if (instance := self._submission_orchestrator) is None:
            instance = self._submission_orchestrator = SubmissionOrchestrator(
                course_services=self.course_services(),
                evaluation_services=self.evaluation_services(),
                course_path_services=self.course_path_services(),
                path_resolver=self.path_resolver(),
                event_bus=self.event_bus())
        return instance

    def reference_orchestrator(self) -> ReferenceOrchestrator:
        if (instance := self._reference_orchestrator) is None:
            instance = self._reference_orchestrator = ReferenceOrchestrator(
                settings_manager=self.settings_manager(),
                course_services=self.course_services(),
                evaluation_services=self.evaluation_services(),
                course_path_services=self.course_path_services(),
                student_services=self.student_services(),
                reference_services=self.reference_services(),
                student_evaluation_services=self.student_evaluation_services(),
                event_bus=self.event_bus())
        return instance

    def grade_orchestrator(self) -> GradeOrchestrator:
        if (instance := self._grade_orchestrator) is None:
            instance = self._grade_orchestrator = GradeOrchestrator(
                course_services=self.course_services(),
                evaluation_services=self.evaluation_services(),
                course_path_services=self.course_path_services(),
                student_evaluation_services=self.student_evaluation_services(),
                course_student_services=self.course_student_services(),
                path_resolver=self.path_resolver(),
                event_bus=self.event_bus())
        return instance

    def archive_orchestrator(self) -> ArchiveOrchestrator:
        if (instance := self._archive_orchestrator) is None:
            instance = self._archive_orchestrator = ArchiveOrchestrator(
                settings_manager=self.settings_manager(),
                course_services=self.course_services(),
                course_path_services=self.course_path_services(),
                archive_services=self.archive_services(),
                event_bus=self.event_bus())
        return instance

# --- App wide singleton ---
container = DependencyInjectionContainer()