import os
import platform
import re
import shlex
import shutil
import signal
import subprocess
from pathlib import Path

from tools.path_utils import WORKSPACE_DIR, resolve_path

DEFAULT_TIMEOUT = 20
SCAFFOLD_TIMEOUT = 180
INSTALL_TIMEOUT = 120
IS_WINDOWS = platform.system().lower() == "windows"

RUNNING_PROCESSES = {}


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


def _normalize_timeout(timeout, default=DEFAULT_TIMEOUT):
    try:
        timeout = int(timeout)
    except Exception:
        return default

    if timeout <= 0:
        return default

    return timeout


def _find_executable(name: str):
    candidates = [name]

    if IS_WINDOWS:
        lower = name.lower()
        if lower == "npm":
            candidates = ["npm.cmd", "npm.exe", "npm"]
        elif lower == "npx":
            candidates = ["npx.cmd", "npx.exe", "npx"]
        elif lower == "node":
            candidates = ["node.exe", "node"]
        elif lower == "python":
            candidates = ["python.exe", "python", "py.exe", "py"]
        elif lower == "pip":
            candidates = ["pip.exe", "pip"]

    for candidate in candidates:
        found = shutil.which(candidate)
        if found:
            return found

    return name


def _prepare_command_parts(command_parts):
    if not command_parts:
        return command_parts

    prepared = command_parts[:]
    prepared[0] = _find_executable(prepared[0])
    return prepared


def _validate_command_parts(command_parts):
    if not command_parts:
        return "Command cannot be empty"

    executable = Path(command_parts[0]).name.strip().lower()

    if not executable:
        return "Command cannot be empty"

    executable_stem = executable
    if executable_stem.endswith(".exe") or executable_stem.endswith(".cmd"):
        executable_stem = executable_stem.rsplit(".", 1)[0]

    if executable in BLOCKED_COMMANDS or executable_stem in BLOCKED_COMMANDS:
        return f"Command '{command_parts[0]}' is blocked on this platform"

    for token in command_parts:
        if token in BLOCKED_TOKENS:
            return f"Command blocked due to disallowed token: '{token}'"

    full_command = " ".join(command_parts).lower()

    for pattern in DANGEROUS_PATTERNS:
        if pattern in full_command:
            return f"Command blocked due to dangerous pattern: '{pattern}'"

    return None


def _command_not_found_message(command_name: str):
    cmd = Path(command_name).name.lower()

    if cmd in {
        "npm",
        "npm.cmd",
        "npm.exe",
        "node",
        "node.exe",
        "npx",
        "npx.cmd",
        "npx.exe",
    }:
        return (
            f"Command not found: {command_name}. "
            "Node.js does not appear to be installed or is not in PATH."
        )

    if cmd in {"pip", "pip3", "pip.exe"}:
        return "pip is not available. Ensure Python and pip are installed and in PATH."

    if cmd in {"python", "python3", "py", "python.exe", "py.exe"}:
        return "Python is not available. Ensure Python is installed and added to PATH."

    return f"Command not found: {command_name}. Check whether it is installed or use a different tool."


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
        return {
            "success": False,
            "returncode": None,
            "stdout": "",
            "stderr": _command_not_found_message(command_parts[0]),
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


def _start_background_process(command_parts, cwd: str = "", label: str = "process"):
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

    safe_label = _safe_process_log_name(label)
    stdout_path = log_dir / f"{safe_label}_stdout.log"
    stderr_path = log_dir / f"{safe_label}_stderr.log"

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
    except FileNotFoundError:
        stdout_file.close()
        stderr_file.close()
        return _format_command_result(
            {
                "success": False,
                "returncode": None,
                "stdout": "",
                "stderr": _command_not_found_message(command_parts[0]),
                "cwd": str(workdir),
                "command": command_parts,
            }
        )
    except Exception as e:
        stdout_file.close()
        stderr_file.close()
        return _format_command_result(
            {
                "success": False,
                "returncode": None,
                "stdout": "",
                "stderr": str(e),
                "cwd": str(workdir),
                "command": command_parts,
            }
        )

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
                f"Started process without blocking.\n"
                f"PID: {process.pid}\n"
                f"stdout log: {stdout_path}\n"
                f"stderr log: {stderr_path}"
            ),
            "stderr": "",
            "cwd": str(workdir),
            "command": command_parts,
        }
    )


def _npm_executable():
    return "npm.cmd" if IS_WINDOWS else "npm"


def _npx_executable():
    return "npx.cmd" if IS_WINDOWS else "npx"


def _validate_project_name(project_name: str):
    if not project_name or not project_name.strip():
        return "project_name is required"

    name = project_name.strip()

    if any(token in name for token in BLOCKED_TOKENS):
        return "project_name contains blocked shell token"

    if "/" in name or "\\" in name:
        return "project_name must be a folder name, not a path"

    if name in {".", ".."}:
        return "project_name cannot be '.' or '..'"

    return None


def _project_path(project_name: str, cwd: str = "") -> Path:
    return _safe_working_directory(cwd) / project_name.strip()


def run_command(command: str, cwd: str = "", timeout: int = DEFAULT_TIMEOUT):
    """
    Run a command safely without shell expansion.
    Best for short commands that finish quickly.
    """
    try:
        if not command or not command.strip():
            return "ERROR: command is required"

        command_parts = shlex.split(command)
        result = _run_subprocess(command_parts, cwd=cwd, timeout=timeout)
        return _format_command_result(result)

    except Exception as e:
        return f"ERROR: Failed to run command → {str(e)}"


def run_command_background(command: str, cwd: str = "", label: str = "command"):
    """
    Start a command without blocking.
    Best for long-running commands like dev servers.
    """
    try:
        if not command or not command.strip():
            return "ERROR: command is required"

        command_parts = shlex.split(command)
        return _start_background_process(command_parts, cwd=cwd, label=label)

    except Exception as e:
        return f"ERROR: Failed to start command → {str(e)}"


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


def run_npm_script(
    script: str, cwd: str = "", background: bool = True, timeout: int = DEFAULT_TIMEOUT
):
    """
    Run an npm script.
    Defaults to non-blocking because npm scripts are often dev servers.
    """
    try:
        if not script or not script.strip():
            return "ERROR: script is required"

        script_name = script.strip()
        command_parts = [_npm_executable(), "run", script_name]

        if background:
            return _start_background_process(
                command_parts,
                cwd=cwd,
                label=f"npm_{script_name}",
            )

        result = _run_subprocess(command_parts, cwd=cwd, timeout=timeout)
        return _format_command_result(result)

    except Exception as e:
        return f"ERROR: Failed to run npm script → {str(e)}"


def run_npm_dev(cwd: str = "", script: str = "dev"):
    """
    Start npm run dev without blocking.
    """
    return run_npm_script(script=script, cwd=cwd, background=True)


def run_npm_build(cwd: str = "", script: str = "build", timeout: int = 180):
    """
    Run npm build and wait for completion.
    """
    return run_npm_script(script=script, cwd=cwd, background=False, timeout=timeout)


def run_npm_start(cwd: str = "", script: str = "start"):
    """
    Start npm run start without blocking.
    """
    return run_npm_script(script=script, cwd=cwd, background=True)


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


def install_npm_package(
    package: str, cwd: str = "", dev: bool = False, timeout: int = INSTALL_TIMEOUT
):
    """
    Install an npm package.
    """
    try:
        if not package or not package.strip():
            return "ERROR: package is required"

        command_parts = [_npm_executable(), "install", package.strip()]

        if dev:
            command_parts.append("--save-dev")

        result = _run_subprocess(command_parts, cwd=cwd, timeout=timeout)
        return _format_command_result(result)

    except Exception as e:
        return f"ERROR: Failed to install npm package → {str(e)}"


def install_npm_packages(
    packages: str, cwd: str = "", dev: bool = False, timeout: int = INSTALL_TIMEOUT
):
    """
    Install multiple npm packages.
    packages can be a space-separated string like: lucide-react framer-motion
    """
    try:
        if not packages or not packages.strip():
            return "ERROR: packages is required"

        package_parts = shlex.split(packages)
        command_parts = [_npm_executable(), "install"] + package_parts

        if dev:
            command_parts.append("--save-dev")

        result = _run_subprocess(command_parts, cwd=cwd, timeout=timeout)
        return _format_command_result(result)

    except Exception as e:
        return f"ERROR: Failed to install npm packages → {str(e)}"


def run_npm_install(cwd: str = "", timeout: int = INSTALL_TIMEOUT):
    """
    Run npm install inside a workspace project.
    """
    try:
        command_parts = [_npm_executable(), "install"]
        result = _run_subprocess(command_parts, cwd=cwd, timeout=timeout)
        return _format_command_result(result)

    except Exception as e:
        return f"ERROR: Failed to run npm install → {str(e)}"


def check_node_environment(cwd: str = "", timeout: int = DEFAULT_TIMEOUT):
    """
    Check Node, npm, and npx availability.
    """
    outputs = []

    for command_parts in (
        ["node", "--version"],
        [_npm_executable(), "--version"],
        [_npx_executable(), "--version"],
    ):
        result = _run_subprocess(command_parts, cwd=cwd, timeout=timeout)
        outputs.append(_format_command_result(result))

    return "\n\n---\n\n".join(outputs)


def create_next_app(
    project_name: str,
    cwd: str = "",
    use_typescript: bool = True,
    use_tailwind: bool = True,
    use_eslint: bool = True,
    use_app_router: bool = True,
    use_src_dir: bool = True,
    import_alias: str = "@/*",
    timeout: int = SCAFFOLD_TIMEOUT,
):
    """
    Create a Next.js app non-interactively.
    """
    try:
        validation_error = _validate_project_name(project_name)
        if validation_error:
            return f"ERROR: {validation_error}"

        target_path = _project_path(project_name, cwd)
        if target_path.exists():
            return f"ERROR: Project folder already exists: {target_path}"

        command_parts = [
            _npm_executable(),
            "exec",
            "--yes",
            "create-next-app@latest",
            "--",
            project_name.strip(),
            "--use-npm",
        ]

        command_parts.append("--typescript" if use_typescript else "--javascript")
        command_parts.append("--tailwind" if use_tailwind else "--no-tailwind")
        command_parts.append("--eslint" if use_eslint else "--no-eslint")
        command_parts.append("--app" if use_app_router else "--no-app")
        command_parts.append("--src-dir" if use_src_dir else "--no-src-dir")

        if import_alias and import_alias.strip():
            command_parts.extend(["--import-alias", import_alias.strip()])

        result = _run_subprocess(command_parts, cwd=cwd, timeout=timeout)
        return _format_command_result(result)

    except Exception as e:
        return f"ERROR: Failed to create Next.js app → {str(e)}"


def create_vite_app(
    project_name: str,
    template: str = "react-ts",
    cwd: str = "",
    timeout: int = SCAFFOLD_TIMEOUT,
):
    """
    Create a Vite app non-interactively.
    Common templates: react, react-ts, vue, vue-ts, vanilla, vanilla-ts, svelte, svelte-ts.
    """
    try:
        validation_error = _validate_project_name(project_name)
        if validation_error:
            return f"ERROR: {validation_error}"

        target_path = _project_path(project_name, cwd)
        if target_path.exists():
            return f"ERROR: Project folder already exists: {target_path}"

        command_parts = [
            _npm_executable(),
            "create",
            "vite@latest",
            project_name.strip(),
            "--",
            "--template",
            template.strip() or "react-ts",
        ]

        result = _run_subprocess(command_parts, cwd=cwd, timeout=timeout)
        return _format_command_result(result)

    except Exception as e:
        return f"ERROR: Failed to create Vite app → {str(e)}"


def create_react_app_vite(
    project_name: str, cwd: str = "", timeout: int = SCAFFOLD_TIMEOUT
):
    """
    Create a React + TypeScript app using Vite.
    """
    return create_vite_app(
        project_name=project_name, template="react-ts", cwd=cwd, timeout=timeout
    )


def create_vue_app_vite(
    project_name: str, cwd: str = "", timeout: int = SCAFFOLD_TIMEOUT
):
    """
    Create a Vue + TypeScript app using Vite.
    """
    return create_vite_app(
        project_name=project_name, template="vue-ts", cwd=cwd, timeout=timeout
    )


def create_svelte_app_vite(
    project_name: str, cwd: str = "", timeout: int = SCAFFOLD_TIMEOUT
):
    """
    Create a Svelte + TypeScript app using Vite.
    """
    return create_vite_app(
        project_name=project_name, template="svelte-ts", cwd=cwd, timeout=timeout
    )


def create_astro_app(
    project_name: str,
    cwd: str = "",
    template: str = "basics",
    timeout: int = SCAFFOLD_TIMEOUT,
):
    """
    Create an Astro app non-interactively.
    """
    try:
        validation_error = _validate_project_name(project_name)
        if validation_error:
            return f"ERROR: {validation_error}"

        target_path = _project_path(project_name, cwd)
        if target_path.exists():
            return f"ERROR: Project folder already exists: {target_path}"

        command_parts = [
            _npm_executable(),
            "create",
            "astro@latest",
            project_name.strip(),
            "--",
            "--yes",
            "--template",
            template.strip() or "basics",
            "--install",
            "--no-git",
        ]

        result = _run_subprocess(command_parts, cwd=cwd, timeout=timeout)
        return _format_command_result(result)

    except Exception as e:
        return f"ERROR: Failed to create Astro app → {str(e)}"


def create_express_api(
    project_name: str,
    cwd: str = "",
    timeout: int = INSTALL_TIMEOUT,
):
    """
    Create a small Express API project.
    """
    try:
        validation_error = _validate_project_name(project_name)
        if validation_error:
            return f"ERROR: {validation_error}"

        root = _project_path(project_name, cwd)
        if root.exists():
            return f"ERROR: Project folder already exists: {root}"

        root.mkdir(parents=True, exist_ok=False)
        (root / "src").mkdir(parents=True, exist_ok=True)

        package_json = f"""{{
  "name": "{project_name.strip()}",
  "version": "0.1.0",
  "type": "module",
  "scripts": {{
    "dev": "node --watch src/server.js",
    "start": "node src/server.js"
  }},
  "dependencies": {{
    "cors": "latest",
    "dotenv": "latest",
    "express": "latest"
  }}
}}
"""

        server_js = """import express from "express";
import cors from "cors";
import "dotenv/config";

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

app.get("/", (req, res) => {
  res.json({
    ok: true,
    message: "Express API is running",
  });
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
"""

        (root / "package.json").write_text(package_json, encoding="utf-8")
        (root / "src" / "server.js").write_text(server_js, encoding="utf-8")
        (root / ".env.example").write_text("PORT=3000\n", encoding="utf-8")

        result = _run_subprocess(
            [_npm_executable(), "install"], cwd=str(root), timeout=timeout
        )

        if result["success"]:
            result["stdout"] = f"Created Express API at {root}\n\n{result['stdout']}"

        return _format_command_result(result)

    except Exception as e:
        return f"ERROR: Failed to create Express API → {str(e)}"


def init_shadcn(cwd: str = "", timeout: int = INSTALL_TIMEOUT):
    """
    Initialize shadcn/ui non-interactively in an existing project.
    """
    try:
        command_parts = [
            _npx_executable(),
            "shadcn@latest",
            "init",
            "-y",
        ]

        result = _run_subprocess(command_parts, cwd=cwd, timeout=timeout)
        return _format_command_result(result)

    except Exception as e:
        return f"ERROR: Failed to initialize shadcn/ui → {str(e)}"


def add_shadcn_component(component: str, cwd: str = "", timeout: int = INSTALL_TIMEOUT):
    """
    Add one shadcn/ui component.
    Example component values: button, card, input, dialog, dropdown-menu.
    """
    try:
        if not component or not component.strip():
            return "ERROR: component is required"

        command_parts = [
            _npx_executable(),
            "shadcn@latest",
            "add",
            component.strip(),
            "-y",
        ]

        result = _run_subprocess(command_parts, cwd=cwd, timeout=timeout)
        return _format_command_result(result)

    except Exception as e:
        return f"ERROR: Failed to add shadcn component → {str(e)}"


def add_shadcn_components(
    components: str, cwd: str = "", timeout: int = INSTALL_TIMEOUT
):
    """
    Add multiple shadcn/ui components.
    components can be a space-separated string like: button card input dialog
    """
    try:
        if not components or not components.strip():
            return "ERROR: components is required"

        component_parts = shlex.split(components)

        command_parts = [
            _npx_executable(),
            "shadcn@latest",
            "add",
            *component_parts,
            "-y",
        ]

        result = _run_subprocess(command_parts, cwd=cwd, timeout=timeout)
        return _format_command_result(result)

    except Exception as e:
        return f"ERROR: Failed to add shadcn components → {str(e)}"


def install_frontend_basics(cwd: str = "", timeout: int = INSTALL_TIMEOUT):
    """
    Install common frontend libraries.
    """
    return install_npm_packages(
        packages="lucide-react framer-motion recharts clsx tailwind-merge",
        cwd=cwd,
        dev=False,
        timeout=timeout,
    )


def install_backend_basics(cwd: str = "", timeout: int = INSTALL_TIMEOUT):
    """
    Install common Node backend libraries.
    """
    return install_npm_packages(
        packages="express cors dotenv zod",
        cwd=cwd,
        dev=False,
        timeout=timeout,
    )


def install_typescript_node_dev_tools(cwd: str = "", timeout: int = INSTALL_TIMEOUT):
    """
    Install common TypeScript backend dev tools.
    """
    return install_npm_packages(
        packages="typescript tsx @types/node",
        cwd=cwd,
        dev=True,
        timeout=timeout,
    )


def open_project_tree(cwd: str = "", max_depth: int = 3):
    """
    Return a simple file tree for a workspace folder.
    """
    try:
        root = _safe_working_directory(cwd)
        max_depth = _normalize_timeout(max_depth, default=3)

        lines = [str(root)]

        def walk(path: Path, depth: int):
            if depth > max_depth:
                return

            try:
                items = sorted(
                    [
                        item
                        for item in path.iterdir()
                        if item.name
                        not in {"node_modules", ".git", ".next", "dist", "build"}
                    ],
                    key=lambda p: (not p.is_dir(), p.name.lower()),
                )
            except Exception:
                return

            for item in items:
                indent = "  " * depth
                suffix = "/" if item.is_dir() else ""
                lines.append(f"{indent}- {item.name}{suffix}")

                if item.is_dir():
                    walk(item, depth + 1)

        walk(root, 1)

        return "\n".join(lines)

    except Exception as e:
        return f"ERROR: Failed to read project tree → {str(e)}"


def read_process_log(pid: str, stream: str = "stdout", lines: int = 80):
    """
    Read the latest lines from a background process log.
    """
    try:
        if not pid or not str(pid).strip():
            return "ERROR: pid is required"

        pid = str(pid).strip()
        record = RUNNING_PROCESSES.get(pid)

        if not record:
            return f"ERROR: No running process found with PID {pid}"

        stream = stream.strip().lower() if stream else "stdout"

        if stream not in {"stdout", "stderr"}:
            return "ERROR: stream must be stdout or stderr"

        log_path = Path(record[stream])

        if not log_path.exists():
            return f"ERROR: Log file does not exist: {log_path}"

        line_count = _normalize_timeout(lines, default=80)

        all_lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
        latest = all_lines[-line_count:]

        return "\n".join(latest) if latest else "(empty)"

    except Exception as e:
        return f"ERROR: Failed to read process log → {str(e)}"


def list_processes():
    """
    List background processes started by ACE.
    """
    try:
        if not RUNNING_PROCESSES:
            return "No running processes tracked by ACE."

        rows = []

        for pid, record in list(RUNNING_PROCESSES.items()):
            process = record["process"]
            status = (
                "running"
                if process.poll() is None
                else f"stopped({process.returncode})"
            )

            rows.append(
                f"PID: {pid}\n"
                f"status: {status}\n"
                f"cwd: {record['cwd']}\n"
                f"command: {' '.join(record['command'])}\n"
                f"stdout: {record['stdout']}\n"
                f"stderr: {record['stderr']}"
            )

        return "\n\n---\n\n".join(rows)

    except Exception as e:
        return f"ERROR: Failed to list processes → {str(e)}"


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

        if IS_WINDOWS:
            process.terminate()
        else:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)

        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            if IS_WINDOWS:
                process.kill()
            else:
                os.killpg(os.getpgid(process.pid), signal.SIGKILL)

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


def stop_all_processes():
    """
    Stop all background processes started by ACE.
    """
    try:
        if not RUNNING_PROCESSES:
            return "No running processes tracked by ACE."

        pids = list(RUNNING_PROCESSES.keys())
        results = [stop_process(pid) for pid in pids]

        return "\n\n---\n\n".join(results)

    except Exception as e:
        return f"ERROR: Failed to stop all processes → {str(e)}"
