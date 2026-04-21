import json
import re


def parse_llm_response(raw_response: str):
    """
    Attempts to extract and parse JSON from LLM output.
    Returns dict or None.
    """

    if not raw_response:
        return None

    try:
        return json.loads(raw_response)
    except:
        pass

    json_str = extract_json(raw_response)

    if not json_str:
        return None

    try:
        return json.loads(json_str)
    except:
        fixed = fix_json(json_str)
        try:
            return json.loads(fixed)
        except:
            return None


def extract_json(text: str):
    """
    Extracts first JSON object from text.
    """

    match = re.search(r"\{.*\}", text, re.DOTALL)

    if match:
        return match.group(0)

    return None


def fix_json(bad_json: str):
    """
    Fixes common LLM JSON mistakes:
    - single quotes → double quotes
    - missing quotes around keys
    """

    fixed = bad_json

    fixed = fixed.replace("'", '"')

    fixed = re.sub(r"(\w+)\s*:", r'"\1":', fixed)

    return fixed
