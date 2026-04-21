import json
import requests


DEFAULT_HTTP_TIMEOUT = 20
MAX_TEXT_PREVIEW = 10000


def _safe_json_loads(text: str):
    try:
        return json.loads(text)
    except Exception:
        return None


def _parse_json_input(value: str, field_name: str):
    if not value:
        return {}

    try:
        parsed = json.loads(value)
    except Exception as e:
        raise ValueError(f"{field_name} must be valid JSON: {str(e)}")

    if not isinstance(parsed, dict):
        raise ValueError(f"{field_name} must decode to a JSON object")

    return parsed


def _format_response(response: requests.Response):
    content_type = response.headers.get("Content-Type", "")
    text = response.text
    parsed_json = None

    if "application/json" in content_type.lower():
        parsed_json = _safe_json_loads(text)

    result = {
        "status_code": response.status_code,
        "ok": response.ok,
        "url": response.url,
        "content_type": content_type,
        "headers": dict(response.headers),
        "body": parsed_json if parsed_json is not None else text[:MAX_TEXT_PREVIEW],
    }

    return json.dumps(result, indent=2, ensure_ascii=False)


def _request(
    method: str,
    url: str,
    headers_json: str = "",
    body_json: str = "",
    timeout: int = DEFAULT_HTTP_TIMEOUT,
):
    if not url or not url.strip():
        return "ERROR: url is required"

    try:
        headers = (
            _parse_json_input(headers_json, "headers_json") if headers_json else {}
        )
        body = _parse_json_input(body_json, "body_json") if body_json else {}
        timeout = int(timeout) if timeout else DEFAULT_HTTP_TIMEOUT

        response = requests.request(
            method=method.upper(),
            url=url,
            headers=headers,
            json=body if method.upper() in {"POST", "PUT", "PATCH"} else None,
            timeout=timeout,
        )

        return _format_response(response)

    except ValueError as e:
        return f"ERROR: {str(e)}"
    except requests.exceptions.Timeout:
        return f"ERROR: HTTP {method.upper()} request timed out after {timeout} seconds"
    except requests.exceptions.RequestException as e:
        return f"ERROR: HTTP {method.upper()} request failed → {str(e)}"
    except Exception as e:
        return f"ERROR: Unexpected HTTP {method.upper()} error → {str(e)}"


def http_get(url: str, headers_json: str = "", timeout: int = DEFAULT_HTTP_TIMEOUT):
    return _request("GET", url, headers_json=headers_json, timeout=timeout)


def http_post(
    url: str,
    body_json: str = "",
    headers_json: str = "",
    timeout: int = DEFAULT_HTTP_TIMEOUT,
):
    return _request(
        "POST", url, headers_json=headers_json, body_json=body_json, timeout=timeout
    )


def http_put(
    url: str,
    body_json: str = "",
    headers_json: str = "",
    timeout: int = DEFAULT_HTTP_TIMEOUT,
):
    return _request(
        "PUT", url, headers_json=headers_json, body_json=body_json, timeout=timeout
    )


def http_patch(
    url: str,
    body_json: str = "",
    headers_json: str = "",
    timeout: int = DEFAULT_HTTP_TIMEOUT,
):
    return _request(
        "PATCH", url, headers_json=headers_json, body_json=body_json, timeout=timeout
    )


def http_delete(url: str, headers_json: str = "", timeout: int = DEFAULT_HTTP_TIMEOUT):
    return _request("DELETE", url, headers_json=headers_json, timeout=timeout)
