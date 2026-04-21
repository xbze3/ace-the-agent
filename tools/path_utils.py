from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
WORKSPACE_DIR = BASE_DIR / "workspace"


def resolve_path(relative_path: str) -> Path:
    """
    Resolve a path safely inside the workspace.
    Prevents path traversal such as ../../etc/passwd
    """
    full_path = (WORKSPACE_DIR / relative_path).resolve()

    if not str(full_path).startswith(str(WORKSPACE_DIR.resolve())):
        raise ValueError("Access denied: Path outside workspace")

    return full_path
