from pathlib import Path
import requests

from tools.path_utils import resolve_path


DEFAULT_DOWNLOAD_TIMEOUT = 30


def download_file(url: str, output_path: str, timeout: int = DEFAULT_DOWNLOAD_TIMEOUT):
    try:
        if not url or not url.strip():
            return "ERROR: url is required"

        if not output_path or not output_path.strip():
            return "ERROR: output_path is required"

        file_path = resolve_path(output_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        response = requests.get(url, timeout=int(timeout))
        response.raise_for_status()

        file_path.write_bytes(response.content)

        size_bytes = file_path.stat().st_size

        return (
            f"Downloaded file successfully\n"
            f"path: {output_path}\n"
            f"size_bytes: {size_bytes}\n"
            f"url: {url}"
        )

    except requests.exceptions.Timeout:
        return f"ERROR: Download timed out after {timeout} seconds"
    except requests.exceptions.RequestException as e:
        return f"ERROR: Download failed → {str(e)}"
    except Exception as e:
        return f"ERROR: {str(e)}"
