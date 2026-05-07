import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def get_workspace_dir() -> Path:
    """
    Resolve ACE's runtime workspace directory.

    Priority:
    1. ACE_WORKSPACE_DIR from .env / environment
    2. ./workspace relative to the current folder where ACE is run
    """

    workspace = os.getenv("ACE_WORKSPACE_DIR", "workspace")
    workspace_path = Path(workspace).expanduser()

    if workspace_path.is_absolute():
        return workspace_path.resolve()

    return (Path.cwd() / workspace_path).resolve()


WORKSPACE_DIR = get_workspace_dir()


def resolve_path(relative_path: str) -> Path:
    """
    Resolve a path safely inside the workspace.
    Prevents path traversal such as ../../etc/passwd
    """

    WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)

    full_path = (WORKSPACE_DIR / relative_path).resolve()

    if not str(full_path).startswith(str(WORKSPACE_DIR.resolve())):
        raise ValueError("Access denied: Path outside workspace")

    return full_path
