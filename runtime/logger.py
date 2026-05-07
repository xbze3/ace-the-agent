import os
import json
from datetime import datetime
from pathlib import Path
from typing import Any

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "ace.log"

_SHOW_LOGS = os.getenv("ACE_SHOW_LOGS", "false").lower() in {
    "1",
    "true",
    "yes",
    "on",
}


def set_console_logging(enabled: bool) -> None:
    """
    Enable or disable printing logs to the terminal.
    Logs are still written to file either way.
    """
    global _SHOW_LOGS
    _SHOW_LOGS = enabled


def get_console_logging() -> bool:
    return _SHOW_LOGS


def _format_payload(payload: Any) -> str:
    if isinstance(payload, (dict, list)):
        return json.dumps(payload, indent=2, ensure_ascii=False)

    return json.dumps(payload, indent=2, ensure_ascii=False)


def log_step(event: str, payload: Any = None) -> None:
    """
    Writes logs to file always.
    Prints logs to console only when console logging is enabled.
    """

    timestamp = datetime.now().isoformat()

    entry = {
        "timestamp": timestamp,
        "event": event,
        "payload": payload,
    }

    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(entry, ensure_ascii=False) + "\n")

    if not _SHOW_LOGS:
        return

    print("\nLOG ENTRY")
    print(timestamp)
    print(event)

    if payload is not None:
        print(_format_payload(payload))
