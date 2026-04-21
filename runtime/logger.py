import os
import json
from datetime import datetime

LOG_DIR = "logs"


def ensure_log_dir():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)


def get_log_file():
    ensure_log_dir()
    timestamp = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(LOG_DIR, f"{timestamp}.log")


def log_step(event_type: str, data):
    """
    Logs structured data to file + console
    """

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event": event_type,
        "data": data,
    }

    try:
        with open(get_log_file(), "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        print(f"Logger file write error: {e}")

    print_pretty(log_entry)


def print_pretty(entry):
    print("\nLOG ENTRY")
    print(f"{entry['timestamp']}")
    print(f"{entry['event']}")

    try:
        formatted = json.dumps(entry["data"], indent=2)
    except:
        formatted = str(entry["data"])

    print(formatted)
