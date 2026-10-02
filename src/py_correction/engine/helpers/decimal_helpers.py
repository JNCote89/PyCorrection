from decimal import Decimal, InvalidOperation
from typing import Any

def safe_decimal(cell_value: Any | None, default: None = None) -> Decimal | None:
    if cell_value is None:
        return default
    try:
        if isinstance(cell_value, str):
            cell_value = cell_value.replace(",", ".")
        return Decimal(str(cell_value).strip())
    except (InvalidOperation, TypeError, ValueError):
        return default
