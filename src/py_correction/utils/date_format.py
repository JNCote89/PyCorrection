from datetime import datetime, timezone
import logging

logging.getLogger("tzlocal").setLevel(logging.WARNING)

def get_utc_now() -> datetime:
    return datetime.now(timezone.utc) # type: ignore[arg-type]

def return_user_date_str(date: datetime) -> str:
    return date.astimezone().strftime("%Y-%m-%d %H:%M:%S")

