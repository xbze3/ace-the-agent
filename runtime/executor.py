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


def execute_tool(action: str, arguments: dict):
    """
    Executes a tool safely.
    Always returns a string result.
    """

    if not action:
        return "ERROR: No action provided"

    tool = get_tool_by_name(action)

    if not tool:
        return f"ERROR: Unknown tool '{action}'"

    if not isinstance(arguments, dict):
        return "ERROR: Arguments must be a dictionary"

    arguments = normalize_arguments(arguments)

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
