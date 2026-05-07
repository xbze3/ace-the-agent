import json


def parse_llm_response(raw_response):
    """
    Parse an LLM response into either:
    {
        "action": "...",
        "arguments": {...}
    }

    or:
    {
        "final_answer": "..."
    }

    Returns None if no valid ACE response can be parsed.
    """

    if not raw_response:
        return None

    if isinstance(raw_response, dict):
        return _validate_response(raw_response)

    if not isinstance(raw_response, str):
        return None

    text = raw_response.strip()

    parsed = _try_json_loads(text)
    if parsed:
        return _validate_response(parsed)

    cleaned = _strip_code_fence(text)
    parsed = _try_json_loads(cleaned)
    if parsed:
        return _validate_response(parsed)

    extracted_objects = _extract_json_objects(cleaned)

    for obj in extracted_objects:
        parsed = _try_json_loads(obj)

        if parsed:
            validated = _validate_response(parsed)

            if validated:
                return validated

    return None


def _try_json_loads(text: str):
    try:
        return json.loads(text)
    except Exception:
        return None


def _strip_code_fence(text: str) -> str:
    text = text.strip()

    if not text.startswith("```"):
        return text

    lines = text.splitlines()

    if lines and lines[0].startswith("```"):
        lines = lines[1:]

    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]

    if lines and lines[0].strip().lower() == "json":
        lines = lines[1:]

    return "\n".join(lines).strip()


def _extract_json_objects(text: str) -> list[str]:
    """
    Extracts balanced JSON object candidates from a larger text response.
    Handles braces inside quoted strings.
    """

    objects = []
    start = None
    depth = 0
    in_string = False
    escape = False

    for index, char in enumerate(text):
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False

            continue

        if char == '"':
            in_string = True
            continue

        if char == "{":
            if depth == 0:
                start = index
            depth += 1

        elif char == "}":
            if depth > 0:
                depth -= 1

                if depth == 0 and start is not None:
                    objects.append(text[start : index + 1])
                    start = None

    return objects


def _validate_response(parsed):
    if not isinstance(parsed, dict):
        return None

    if "action" in parsed:
        action = parsed.get("action")
        arguments = parsed.get("arguments", {})

        if not action or not isinstance(action, str):
            return None

        if arguments is None:
            arguments = {}

        if not isinstance(arguments, dict):
            return None

        return {
            "action": action,
            "arguments": arguments,
        }

    if "final_answer" in parsed:
        final_answer = parsed.get("final_answer")

        if final_answer is None:
            return None

        return {
            "final_answer": str(final_answer),
        }

    return None
