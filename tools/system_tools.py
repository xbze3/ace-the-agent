import shutil
from tools.path_utils import resolve_path, WORKSPACE_DIR


def create_directory(path: str):
    try:
        dir_path = resolve_path(path)
        dir_path.mkdir(parents=True, exist_ok=True)
        return f"Directory '{path}' created"
    except Exception as e:
        return f"ERROR: {str(e)}"


def list_directory(path: str = ""):
    try:
        dir_path = resolve_path(path)

        if not dir_path.exists():
            return f"ERROR: Directory '{path}' does not exist"

        if not dir_path.is_dir():
            return f"ERROR: '{path}' is not a directory"

        items = []
        for item in dir_path.iterdir():
            if item.is_dir():
                items.append(f"[DIR] {item.name}")
            else:
                items.append(f"[FILE] {item.name}")

        return "\n".join(sorted(items)) if items else "Directory is empty"
    except Exception as e:
        return f"ERROR: {str(e)}"


def delete_directory(path: str):
    try:
        dir_path = resolve_path(path)

        if not dir_path.exists():
            return f"ERROR: Directory '{path}' does not exist"

        if not dir_path.is_dir():
            return f"ERROR: '{path}' is not a directory"

        if dir_path == WORKSPACE_DIR.resolve():
            return "ERROR: Cannot delete root workspace directory"

        if any(dir_path.iterdir()):
            return "ERROR: Directory not empty (refusing to delete)"

        dir_path.rmdir()
        return f"Directory '{path}' deleted"
    except Exception as e:
        return f"ERROR: {str(e)}"


def delete_directory_recursive(path: str):
    """
    Deletes a directory and all its contents.
    Use with caution.
    """
    try:
        dir_path = resolve_path(path)

        if not dir_path.exists():
            return f"ERROR: Directory '{path}' does not exist"

        if not dir_path.is_dir():
            return f"ERROR: '{path}' is not a directory"

        if dir_path == WORKSPACE_DIR.resolve():
            return "ERROR: Cannot delete root workspace directory"

        shutil.rmtree(dir_path)
        return f"Directory '{path}' deleted recursively"
    except Exception as e:
        return f"ERROR: {str(e)}"


def tree(path: str = "", depth: int = 2):
    """
    Returns a simple tree view of the workspace.
    Useful for agent awareness.
    """
    try:
        dir_path = resolve_path(path)

        if not dir_path.exists():
            return f"ERROR: Directory '{path}' does not exist"

        if not dir_path.is_dir():
            return f"ERROR: '{path}' is not a directory"

        if depth < 0:
            return "ERROR: depth must be >= 0"

        lines = []

        def walk(current_path, current_depth):
            if current_depth > depth:
                return

            for item in sorted(
                current_path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())
            ):
                prefix = "  " * current_depth
                if item.is_dir():
                    lines.append(f"{prefix}[DIR] {item.name}/")
                    walk(item, current_depth + 1)
                else:
                    lines.append(f"{prefix}[FILE] {item.name}")

        walk(dir_path, 0)
        return "\n".join(lines) if lines else "Empty"
    except Exception as e:
        return f"ERROR: {str(e)}"
