import platform
import shlex
import subprocess
from pathlib import Path
import os
import shutil
import re

from tools.path_utils import WORKSPACE_DIR, resolve_path

DEFAULT_TIMEOUT = 20
IS_WINDOWS = platform.system().lower() == "windows"

RUNNING_PROCESSES = {}

# Commands that are dangerous across platforms
BASE_BLOCKED_COMMANDS = {
    "rm",
    "rmdir",
    "del",
    "erase",
    "shutdown",
    "reboot",
    "poweroff",
    "halt",
    "mkfs",
    "format",
    "sudo",
    "su",
    "chmod",
    "chown",
}

# Commands particularly risky on Windows
WINDOWS_BLOCKED_COMMANDS = {
    "powershell",
    "taskkill",
    "sc",
    "reg",
    "net",
    "takeown",
    "icacls",
    "diskpart",
    "bcdedit",
    "cipher",
}

# Commands particularly risky on Unix/Linux/macOS
UNIX_BLOCKED_COMMANDS = {
    "kill",
    "killall",
    "pkill",
    "mount",
    "umount",
    "dd",
    "init",
    "service",
    "systemctl",
    "launchctl",
}

BLOCKED_COMMANDS = (
    BASE_BLOCKED_COMMANDS | WINDOWS_BLOCKED_COMMANDS
    if IS_WINDOWS
    else BASE_BLOCKED_COMMANDS | UNIX_BLOCKED_COMMANDS
)

# Pattern blocking helps catch dangerous flag combinations
DANGEROUS_PATTERNS = [
    "rm -rf",
    "rm -fr",
    "rm -r",
    "del /s",
    "del /f",
    "erase /s",
    "format ",
    "mkfs",
    "shutdown",
    "reboot",
    "poweroff",
    "taskkill /f",
    "reg delete",
    "sc delete",
    "diskpart",
    "bcdedit",
    "dd if=",
]

# Keep shell metacharacters blocked even though shell=False,
# because models may still output suspicious commands.
BLOCKED_TOKENS = {
    "&&",
    "||",
    ";",
    "|",
    ">",
    ">>",
    "<",
}


def _safe_working_directory(cwd: str = "") -> Path:
    return resolve_path(cwd) if cwd else WORKSPACE_DIR.resolve()


def _normalize_timeout(timeout):
    try:
        timeout = int(timeout)
    except Exception:
        return DEFAULT_TIMEOUT

    if timeout <= 0:
        return DEFAULT_TIMEOUT

    return timeout


def _validate_command_parts(command_parts):
    if not command_parts:
        return "Command cannot be empty"

    executable = command_parts[0].strip().lower()

    if not executable:
        return "Command cannot be empty"

    if executable in BLOCKED_COMMANDS:
        return f"Command '{command_parts[0]}' is blocked on this platform"

    for token in command_parts:
        if token in BLOCKED_TOKENS:
            return f"Command blocked due to disallowed token: '{token}'"

    full_command = " ".join(command_parts).lower()

    for pattern in DANGEROUS_PATTERNS:
        if pattern in full_command:
            return f"Command blocked due to dangerous pattern: '{pattern}'"

    return None


def _run_subprocess(command_parts, cwd: str = "", timeout: int = DEFAULT_TIMEOUT):
    workdir = _safe_working_directory(cwd)
    timeout = _normalize_timeout(timeout)

    validation_error = _validate_command_parts(command_parts)
    if validation_error:
        return {
            "success": False,
            "returncode": None,
            "stdout": "",
            "stderr": validation_error,
            "cwd": str(workdir),
            "command": command_parts,
        }

    try:
        prepared_command_parts = _prepare_command_parts(command_parts)

        result = subprocess.run(
            prepared_command_parts,
            cwd=str(workdir),
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
            stdin=subprocess.DEVNULL,
        )

        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "cwd": str(workdir),
            "command": command_parts,
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "returncode": None,
            "stdout": "",
            "stderr": f"Command timed out after {timeout} seconds",
            "cwd": str(workdir),
            "command": command_parts,
        }
    except FileNotFoundError:
        cmd = command_parts[0].lower()

        if cmd in {"npm", "npm.cmd", "node", "npx"}:
            hint = (
                "Node.js does not appear to be installed or is not in PATH. "
                "Install Node.js to use npm/node commands."
            )
        elif cmd in {"pip", "pip3"}:
            hint = (
                "pip is not available. Ensure Python and pip are installed and in PATH."
            )
        elif cmd in {"python", "python3", "py"}:
            hint = (
                "Python is not available. Ensure Python is installed and added to PATH."
            )
        else:
            hint = "Check whether it is installed or use a different tool."

        return {
            "success": False,
            "returncode": None,
            "stdout": "",
            "stderr": f"Command not found: {command_parts[0]}. {hint}",
            "cwd": str(workdir),
            "command": command_parts,
        }
    except Exception as e:
        return {
            "success": False,
            "returncode": None,
            "stdout": "",
            "stderr": str(e),
            "cwd": str(workdir),
            "command": command_parts,
        }


def _format_command_result(result) -> str:
    command_text = " ".join(result["command"]) if result.get("command") else ""

    return (
        f"success: {result['success']}\n"
        f"returncode: {result['returncode']}\n"
        f"cwd: {result['cwd']}\n"
        f"command: {command_text}\n\n"
        f"STDOUT:\n{result['stdout'] or '(empty)'}\n\n"
        f"STDERR:\n{result['stderr'] or '(empty)'}"
    )


def _safe_process_log_name(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_.-]+", "_", value.strip())
    return cleaned.strip("_") or "process"


def _close_process_files(record):
    for key in ("stdout_file", "stderr_file"):
        file_obj = record.get(key)

        if file_obj:
            try:
                file_obj.close()
            except Exception:
                pass


def run_command(command: str, cwd: str = "", timeout: int = DEFAULT_TIMEOUT):
    """
    Run a command safely without shell expansion.
    """
    try:
        if not command or not command.strip():
            return "ERROR: command is required"

        command_parts = shlex.split(command)
        result = _run_subprocess(command_parts, cwd=cwd, timeout=timeout)
        return _format_command_result(result)

    except Exception as e:
        return f"ERROR: Failed to run command → {str(e)}"


def run_python_file(
    path: str, args: str = "", cwd: str = "", timeout: int = DEFAULT_TIMEOUT
):
    """
    Run a Python file inside the workspace.
    """
    try:
        file_path = resolve_path(path)

        if not file_path.exists():
            return f"ERROR: File '{path}' does not exist"

        if not file_path.is_file():
            return f"ERROR: '{path}' is not a file"

        extra_args = shlex.split(args) if args else []
        command_parts = ["python", str(file_path)] + extra_args

        result = _run_subprocess(command_parts, cwd=cwd, timeout=timeout)
        return _format_command_result(result)

    except Exception as e:
        return f"ERROR: Failed to run Python file → {str(e)}"


def run_node_file(
    path: str, args: str = "", cwd: str = "", timeout: int = DEFAULT_TIMEOUT
):
    """
    Run a Node.js file inside the workspace.
    """
    try:
        file_path = resolve_path(path)

        if not file_path.exists():
            return f"ERROR: File '{path}' does not exist"

        if not file_path.is_file():
            return f"ERROR: '{path}' is not a file"

        extra_args = shlex.split(args) if args else []
        command_parts = ["node", str(file_path)] + extra_args

        result = _run_subprocess(command_parts, cwd=cwd, timeout=timeout)
        return _format_command_result(result)

    except Exception as e:
        return f"ERROR: Failed to run Node file → {str(e)}"


def run_npm_script(script: str, cwd: str = "", timeout: int = DEFAULT_TIMEOUT):
    """
    Start an npm script, e.g. npm run dev, without blocking the agent.
    """
    try:
        if not script or not script.strip():
            return "ERROR: script is required"

        executable = "npm.cmd" if IS_WINDOWS else "npm"
        script_name = script.strip()
        command_parts = [executable, "run", script_name]

        workdir = _safe_working_directory(cwd)

        validation_error = _validate_command_parts(command_parts)
        if validation_error:
            return _format_command_result(
                {
                    "success": False,
                    "returncode": None,
                    "stdout": "",
                    "stderr": validation_error,
                    "cwd": str(workdir),
                    "command": command_parts,
                }
            )

        prepared_command_parts = _prepare_command_parts(command_parts)

        log_dir = workdir / ".ace_process_logs"
        log_dir.mkdir(exist_ok=True)

        safe_script_name = _safe_process_log_name(script_name)
        stdout_path = log_dir / f"npm_{safe_script_name}_stdout.log"
        stderr_path = log_dir / f"npm_{safe_script_name}_stderr.log"

        stdout_file = open(stdout_path, "a", encoding="utf-8")
        stderr_file = open(stderr_path, "a", encoding="utf-8")

        try:
            process = subprocess.Popen(
                prepared_command_parts,
                cwd=str(workdir),
                stdout=stdout_file,
                stderr=stderr_file,
                stdin=subprocess.DEVNULL,
                text=True,
                shell=False,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if IS_WINDOWS else 0,
                start_new_session=not IS_WINDOWS,
            )
        except Exception:
            stdout_file.close()
            stderr_file.close()
            raise

        RUNNING_PROCESSES[str(process.pid)] = {
            "process": process,
            "command": command_parts,
            "cwd": str(workdir),
            "stdout": str(stdout_path),
            "stderr": str(stderr_path),
            "stdout_file": stdout_file,
            "stderr_file": stderr_file,
        }

        return _format_command_result(
            {
                "success": True,
                "returncode": None,
                "stdout": (
                    f"Started npm script '{script_name}' without blocking.\n"
                    f"PID: {process.pid}\n"
                    f"stdout log: {stdout_path}\n"
                    f"stderr log: {stderr_path}"
                ),
                "stderr": "",
                "cwd": str(workdir),
                "command": command_parts,
            }
        )

    except FileNotFoundError:
        return (
            "ERROR: Command not found: npm. "
            "Node.js does not appear to be installed or is not in PATH."
        )
    except Exception as e:
        return f"ERROR: Failed to start npm script → {str(e)}"


def stop_process(pid: str):
    """
    Stop a process started by ACE.
    """
    try:
        if not pid or not str(pid).strip():
            return "ERROR: pid is required"

        pid = str(pid).strip()
        record = RUNNING_PROCESSES.get(pid)

        if not record:
            return f"ERROR: No running process found with PID {pid}"

        process = record["process"]

        if process.poll() is not None:
            RUNNING_PROCESSES.pop(pid, None)
            _close_process_files(record)

            return _format_command_result(
                {
                    "success": True,
                    "returncode": process.returncode,
                    "stdout": "Process was already stopped.",
                    "stderr": "",
                    "cwd": record["cwd"],
                    "command": record["command"],
                }
            )

        process.terminate()

        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)

        RUNNING_PROCESSES.pop(pid, None)
        _close_process_files(record)

        return _format_command_result(
            {
                "success": True,
                "returncode": process.returncode,
                "stdout": f"Stopped process {pid}.",
                "stderr": "",
                "cwd": record["cwd"],
                "command": record["command"],
            }
        )

    except Exception as e:
        return f"ERROR: Failed to stop process → {str(e)}"


def install_python_package(package: str, cwd: str = "", timeout: int = 60):
    """
    Install a Python package using pip.
    """
    try:
        if not package or not package.strip():
            return "ERROR: package is required"

        command_parts = ["pip", "install", package.strip()]
        result = _run_subprocess(command_parts, cwd=cwd, timeout=timeout)
        return _format_command_result(result)

    except Exception as e:
        return f"ERROR: Failed to install Python package → {str(e)}"


def install_npm_package(package: str, cwd: str = "", timeout: int = 60):
    """
    Install an npm package using npm install.
    """
    try:
        if not package or not package.strip():
            return "ERROR: package is required"

        executable = "npm.cmd" if IS_WINDOWS else "npm"
        command_parts = [executable, "install", package.strip()]
        result = _run_subprocess(command_parts, cwd=cwd, timeout=timeout)
        return _format_command_result(result)

    except Exception as e:
        return f"ERROR: Failed to install npm package → {str(e)}"


def run_npm_install(cwd: str = "", timeout: int = 60):
    """
    Run npm install inside a workspace project.
    Intended for installing dependencies from package.json.
    """
    try:
        executable = "npm.cmd" if IS_WINDOWS else "npm"
        command_parts = [executable, "install"]
        result = _run_subprocess(command_parts, cwd=cwd, timeout=timeout)
        return _format_command_result(result)

    except Exception as e:
        return f"ERROR: Failed to run npm install → {str(e)}"


def _find_executable(name: str):
    """
    Resolve an executable path in a Windows-friendly way.
    Returns a usable executable string or the original name.
    """
    candidates = [name]

    if IS_WINDOWS:
        lower = name.lower()
        if lower == "npm":
            candidates = ["npm.cmd", "npm.exe", "npm"]
        elif lower == "npx":
            candidates = ["npx.cmd", "npx.exe", "npx"]
        elif lower == "node":
            candidates = ["node.exe", "node"]

    for candidate in candidates:
        found = shutil.which(candidate)
        if found:
            return found

    return name


def _prepare_command_parts(command_parts):
    """
    Resolve the executable before launching the subprocess.
    """
    if not command_parts:
        return command_parts

    prepared = command_parts[:]
    prepared[0] = _find_executable(prepared[0])
    return prepared
