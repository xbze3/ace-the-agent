from tools.path_utils import resolve_path


def create_file(path: str, content: str):
    try:
        file_path = resolve_path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        return f"File created at '{path}'"
    except Exception as e:
        return f"ERROR: {str(e)}"


def read_file(path: str):
    try:
        file_path = resolve_path(path)

        if not file_path.exists():
            return f"ERROR: File '{path}' does not exist"

        if not file_path.is_file():
            return f"ERROR: '{path}' is not a file"

        return file_path.read_text(encoding="utf-8")
    except Exception as e:
        return f"ERROR: {str(e)}"


def update_file(path: str, content: str):
    try:
        file_path = resolve_path(path)

        if not file_path.exists():
            return f"ERROR: File '{path}' does not exist"

        if not file_path.is_file():
            return f"ERROR: '{path}' is not a file"

        file_path.write_text(content, encoding="utf-8")
        return f"File '{path}' updated successfully"
    except Exception as e:
        return f"ERROR: {str(e)}"


def delete_file(path: str):
    try:
        file_path = resolve_path(path)

        if not file_path.exists():
            return f"ERROR: File '{path}' does not exist"

        if not file_path.is_file():
            return f"ERROR: '{path}' is not a file"

        file_path.unlink()
        return f"File '{path}' deleted successfully"
    except Exception as e:
        return f"ERROR: {str(e)}"


def append_file(path: str, content: str):
    try:
        file_path = resolve_path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "a", encoding="utf-8") as f:
            f.write(content)

        return f"Content appended to '{path}'"
    except Exception as e:
        return f"ERROR: {str(e)}"


def list_files(directory: str = ""):
    try:
        dir_path = resolve_path(directory)

        if not dir_path.exists():
            return f"ERROR: Directory '{directory}' does not exist"

        if not dir_path.is_dir():
            return f"ERROR: '{directory}' is not a directory"

        files = [item.name for item in dir_path.iterdir() if item.is_file()]

        return "\n".join(sorted(files)) if files else "No files found"
    except Exception as e:
        return f"ERROR: {str(e)}"


def replace_in_file(path: str, old: str, new: str):
    try:
        file_path = resolve_path(path)

        if not file_path.exists():
            return f"ERROR: File '{path}' does not exist"

        if not file_path.is_file():
            return f"ERROR: '{path}' is not a file"

        content = file_path.read_text(encoding="utf-8")

        if old not in content:
            return "ERROR: Text to replace not found"

        updated = content.replace(old, new)
        file_path.write_text(updated, encoding="utf-8")

        return f"Replaced text in '{path}'"
    except Exception as e:
        return f"ERROR: {str(e)}"


def get_file_info(path: str):
    try:
        file_path = resolve_path(path)

        if not file_path.exists():
            return f"ERROR: File '{path}' does not exist"

        return {
            "name": file_path.name,
            "path": path,
            "size_bytes": file_path.stat().st_size,
            "is_file": file_path.is_file(),
            "is_directory": file_path.is_dir(),
        }
    except Exception as e:
        return f"ERROR: {str(e)}"
