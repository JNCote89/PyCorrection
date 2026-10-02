from dataclasses import MISSING, dataclass, fields


@dataclass
class ResetWorkflowMixin:
    def reset_workflow(self, excluded_field_names: list[str] | None = None) -> None:
        excluded = set(excluded_field_names) if excluded_field_names else set()

        for f in fields(self):
            if f.name in excluded:
                continue
            if f.default_factory is not MISSING:
                setattr(self, f.name, f.default_factory())
            elif f.default is not MISSING:
                setattr(self, f.name, f.default)
            else:
                setattr(self, f.name, None)
