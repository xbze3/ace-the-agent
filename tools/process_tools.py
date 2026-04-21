import json
import subprocess
import time
import uuid
from pathlib import Path

from tools.path_utils import WORKSPACE_DIR, resolve_path


PROCESS_REGISTRY_PATH = WORKSPACE_DIR / ".ace_processes.json"
DEFAULT_STARTUP_WAIT = 2


def _safe_working_directory(cwd: str = "") -> Path:
    return resolve_path(cwd) if cwd else WORKSPACE_DIR.resolve()


def _load_registry():
    if not PROCESS_REGISTRY_PATH.exists():
        return {}

    try:
        return json.loads(PROCESS_REGISTRY_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_registry(registry):
    PROCESS_REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROCESS_REGISTRY_PATH.write_text(
        json.dumps(registry, indent=2),
        encoding="utf-8",
    )


def _normalize_command(command: str):
    if not command or not command.strip():
        raise ValueError("command is required")
    return command.strip()


def _normalize_timeout_value(value, default):
    try:
        value = int(value)
    except Exception:
        return default

    if value < 0:
        return default

    return value


def start_background_command(
    command: str,
    cwd: str = "",
    startup_wait: int = DEFAULT_STARTUP_WAIT,
):
    """
    Start a long-running command in the background and track it.
    Suitable for dev servers and watchers.
    """
    try:
        command = _normalize_command(command)
        workdir = _safe_working_directory(cwd)
        startup_wait = _normalize_timeout_value(startup_wait, DEFAULT_STARTUP_WAIT)

        process = subprocess.Popen(
            command,
            cwd=str(workdir),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            shell=True,
        )

        time.sleep(startup_wait)

        process_id = str(uuid.uuid4())
        is_running = process.poll() is None

        registry = _load_registry()
        registry[process_id] = {
            "process_id": process_id,
            "pid": process.pid,
            "command": command,
            "cwd": str(workdir),
            "status": "running" if is_running else "exited",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        _save_registry(registry)

        return (
            f"Background process started\n"
            f"process_id: {process_id}\n"
            f"pid: {process.pid}\n"
            f"status: {'running' if is_running else 'exited'}\n"
            f"cwd: {workdir}\n"
            f"command: {command}"
        )

    except Exception as e:
        return f"ERROR: Failed to start background command → {str(e)}"


def list_background_processes():
    """
    List tracked background processes.
    """
    try:
        registry = _load_registry()

        if not registry:
            return "No background processes found"

        lines = []
        for process_id, info in registry.items():
            lines.append(
                f"process_id: {process_id}\n"
                f"pid: {info.get('pid')}\n"
                f"status: {info.get('status', 'unknown')}\n"
                f"cwd: {info.get('cwd')}\n"
                f"command: {info.get('command')}\n"
            )

        return "\n".join(lines).strip()

    except Exception as e:
        return f"ERROR: Failed to list background processes → {str(e)}"


def stop_background_process(process_id: str):
    """
    Stop a tracked background process by process_id.
    """
    try:
        if not process_id or not process_id.strip():
            return "ERROR: process_id is required"

        registry = _load_registry()

        if process_id not in registry:
            return f"ERROR: Unknown process_id '{process_id}'"

        info = registry[process_id]
        pid = info.get("pid")

        if pid is None:
            return f"ERROR: No pid recorded for process_id '{process_id}'"

        try:
            proc = subprocess.Popen(
                ["taskkill", "/PID", str(pid), "/T", "/F"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            stdout, stderr = proc.communicate(timeout=10)
            success = proc.returncode == 0
        except FileNotFoundError:
            # likely non-Windows
            proc = subprocess.Popen(
                ["kill", str(pid)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            stdout, stderr = proc.communicate(timeout=10)
            success = proc.returncode == 0

        info["status"] = "stopped" if success else "stop_failed"
        registry[process_id] = info
        _save_registry(registry)

        return (
            f"Stop request completed\n"
            f"process_id: {process_id}\n"
            f"pid: {pid}\n"
            f"success: {success}\n"
            f"STDOUT:\n{stdout.strip() or '(empty)'}\n\n"
            f"STDERR:\n{stderr.strip() or '(empty)'}"
        )

    except Exception as e:
        return f"ERROR: Failed to stop background process → {str(e)}"
