from tools.registry import get_tool_by_name
from runtime.logger import log_step


def normalize_arguments(arguments):
    """
    Fix common LLM mistakes where tool schema metadata is returned
    instead of direct tool arguments.
    """

    if not isinstance(arguments, dict):
        return arguments

    # Example bad shape:
    # {
    #   "type": "object",
    #   "properties": {
    #       "path": "server.js",
    #       "content": "..."
    #   },
    #   "required": ["path", "content"]
    # }
    if "properties" in arguments and isinstance(arguments["properties"], dict):
        props = arguments["properties"]

        # Only unwrap if these look like actual values,
        # not nested schema definitions.
        looks_like_runtime_values = True

        for value in props.values():
            if isinstance(value, dict) and any(
                key in value
                for key in ("type", "description", "properties", "required")
            ):
                looks_like_runtime_values = False
                break

        if looks_like_runtime_values:
            return props

    return arguments


def execute_tool(
    action: str,
    arguments: dict,
    allowed_tools: list[str] | None = None,
):
    """
    Executes a tool safely.
    Always returns a string result.

    If allowed_tools is provided, only tools in that list may be executed.
    This is used by ACE skills to enforce tool permissions at runtime.
    """

    if not action:
        return "ERROR: No action provided"

    if allowed_tools:
        if action not in allowed_tools:
            log_step(
                "EXECUTOR_BLOCKED_TOOL",
                {
                    "tool": action,
                    "allowed_tools": allowed_tools,
                },
            )

            return (
                f"ERROR: Tool '{action}' is not allowed for the active skill. "
                f"Allowed tools: {', '.join(allowed_tools)}"
            )

    tool = get_tool_by_name(action)

    if not tool:
        return f"ERROR: Unknown tool '{action}'"

    if not isinstance(arguments, dict):
        return "ERROR: Arguments must be a dictionary"

    arguments = normalize_arguments(arguments)

    arguments = filter_arguments(tool, arguments)

    missing = check_missing_params(tool, arguments)
    if missing:
        return (
            f"ERROR: Missing required parameters: {missing}. "
            f"Provide direct argument values only, not schema fields like "
            f"'type', 'properties', or 'required'."
        )

    try:
        log_step("EXECUTOR_START", {"tool": action, "arguments": arguments})

        result = tool.func(**arguments)

        if not isinstance(result, str):
            result = str(result)

        log_step("EXECUTOR_SUCCESS", {"tool": action, "result": result})

        return result

    except TypeError as e:
        error_msg = f"ERROR: Invalid arguments for tool '{action}' → {str(e)}"
        log_step("EXECUTOR_ERROR", {"tool": action, "error": str(e)})
        return error_msg

    except Exception as e:
        error_msg = f"ERROR: Tool '{action}' failed → {str(e)}"
        log_step("EXECUTOR_ERROR", {"tool": action, "error": str(e)})
        return error_msg


def check_missing_params(tool, arguments):
    """
    Checks if required parameters are missing.
    """

    required_keys = getattr(tool, "required", None)

    if required_keys is None:
        params = tool.parameters or {}
        required_keys = list(params.keys())

    missing = [key for key in required_keys if key not in arguments]

    return missing if missing else None


def filter_arguments(tool, arguments):
    """
    Removes arguments that are not accepted by the tool.
    This protects tools from LLM-added metadata like:
    created, timestamp, description, type, schema, etc.
    """

    if not isinstance(arguments, dict):
        return arguments

    params = getattr(tool, "parameters", None) or {}

    if not params:
        return arguments

    allowed_keys = set(params.keys())

    return {key: value for key, value in arguments.items() if key in allowed_keys}
