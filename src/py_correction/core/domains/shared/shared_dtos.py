from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WidgetItem[T_value]:
    label: str
    internal_value: T_value


@dataclass(frozen=True, slots=True)
class ComboBoxPayload[T_selection]:
    current_data_selection: T_selection
    items: list[WidgetItem]
    is_enabled: bool


@dataclass(frozen=True, slots=True)
class SelectionWidgetDTO:
    id: int
    label: str