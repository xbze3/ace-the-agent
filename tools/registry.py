from tools.file_tools import (
    create_file,
    read_file,
    update_file,
    delete_file,
    append_file,
    list_files,
    replace_in_file,
    get_file_info,
)

from tools.system_tools import (
    create_directory,
    list_directory,
    delete_directory,
    delete_directory_recursive,
    tree,
)

from tools.command_tools import (
    run_command,
    run_python_file,
    run_node_file,
    run_npm_script,
    run_npm_install,
    install_python_package,
    install_npm_package,
)

from tools.api_tools import (
    http_get,
    http_post,
    http_put,
    http_delete,
)

from tools.process_tools import (
    start_background_command,
    list_background_processes,
    stop_background_process,
)

from tools.download_tools import download_file

from tools.web_search_tools import web_search


class Tool:
    def __init__(self, name, func, description, parameters, required=None):
        self.name = name
        self.func = func
        self.description = description
        self.parameters = parameters
        self.required = required or []


TOOLS = [
    Tool(
        name="create_file",
        func=create_file,
        description="Create a new file inside the workspace",
        parameters={
            "path": {
                "type": "string",
                "description": "Relative file path inside workspace",
            },
            "content": {
                "type": "string",
                "description": "Content to write into the file",
            },
        },
        required=["path", "content"],
    ),
    Tool(
        name="read_file",
        func=read_file,
        description="Read a file from the workspace",
        parameters={
            "path": {
                "type": "string",
                "description": "Relative file path inside workspace",
            },
        },
        required=["path"],
    ),
    Tool(
        name="update_file",
        func=update_file,
        description="Overwrite an existing file in the workspace",
        parameters={
            "path": {
                "type": "string",
                "description": "Relative file path inside workspace",
            },
            "content": {
                "type": "string",
                "description": "New full content of the file",
            },
        },
        required=["path", "content"],
    ),
    Tool(
        name="delete_file",
        func=delete_file,
        description="Delete a file from the workspace",
        parameters={
            "path": {
                "type": "string",
                "description": "Relative file path inside workspace",
            },
        },
        required=["path"],
    ),
    Tool(
        name="append_file",
        func=append_file,
        description="Append content to a file",
        parameters={
            "path": {
                "type": "string",
                "description": "Relative file path inside workspace",
            },
            "content": {
                "type": "string",
                "description": "Content to append",
            },
        },
        required=["path", "content"],
    ),
    Tool(
        name="list_files",
        func=list_files,
        description="List files in a directory inside the workspace",
        parameters={
            "directory": {
                "type": "string",
                "description": "Relative directory path inside workspace",
            },
        },
        required=[],
    ),
    Tool(
        name="replace_in_file",
        func=replace_in_file,
        description="Replace text inside a file",
        parameters={
            "path": {
                "type": "string",
                "description": "Relative file path inside workspace",
            },
            "old": {
                "type": "string",
                "description": "Text to find",
            },
            "new": {
                "type": "string",
                "description": "Replacement text",
            },
        },
        required=["path", "old", "new"],
    ),
    Tool(
        name="get_file_info",
        func=get_file_info,
        description="Get metadata about a file or directory",
        parameters={
            "path": {
                "type": "string",
                "description": "Relative path inside workspace",
            },
        },
        required=["path"],
    ),
    Tool(
        name="create_directory",
        func=create_directory,
        description="Create a directory inside the workspace",
        parameters={
            "path": {
                "type": "string",
                "description": "Relative directory path inside workspace",
            },
        },
        required=["path"],
    ),
    Tool(
        name="list_directory",
        func=list_directory,
        description="List contents of a directory inside the workspace",
        parameters={
            "path": {
                "type": "string",
                "description": "Relative directory path inside workspace",
            },
        },
        required=[],
    ),
    Tool(
        name="delete_directory",
        func=delete_directory,
        description="Delete an empty directory",
        parameters={
            "path": {
                "type": "string",
                "description": "Relative directory path inside workspace",
            },
        },
        required=["path"],
    ),
    Tool(
        name="delete_directory_recursive",
        func=delete_directory_recursive,
        description="Delete a directory and all its contents",
        parameters={
            "path": {
                "type": "string",
                "description": "Relative directory path inside workspace",
            },
        },
        required=["path"],
    ),
    Tool(
        name="tree",
        func=tree,
        description="Show a tree view of the workspace structure",
        parameters={
            "path": {
                "type": "string",
                "description": "Relative directory path inside workspace",
            },
            "depth": {
                "type": "integer",
                "description": "Maximum recursion depth",
            },
        },
        required=[],
    ),
    Tool(
        name="run_command",
        func=run_command,
        description="Run a system command safely inside the workspace without shell expansion",
        parameters={
            "command": {
                "type": "string",
                "description": "Command string to execute",
            },
            "cwd": {
                "type": "string",
                "description": "Relative working directory inside workspace",
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds",
            },
        },
        required=["command"],
    ),
    Tool(
        name="run_python_file",
        func=run_python_file,
        description="Run a Python file inside the workspace",
        parameters={
            "path": {
                "type": "string",
                "description": "Relative path to a Python file",
            },
            "args": {
                "type": "string",
                "description": "Optional command line arguments",
            },
            "cwd": {
                "type": "string",
                "description": "Relative working directory inside workspace",
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds",
            },
        },
        required=["path"],
    ),
    Tool(
        name="run_node_file",
        func=run_node_file,
        description="Run a Node.js file inside the workspace",
        parameters={
            "path": {
                "type": "string",
                "description": "Relative path to a Node.js file",
            },
            "args": {
                "type": "string",
                "description": "Optional command line arguments",
            },
            "cwd": {
                "type": "string",
                "description": "Relative working directory inside workspace",
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds",
            },
        },
        required=["path"],
    ),
    Tool(
        name="run_npm_script",
        func=run_npm_script,
        description="Run an npm script inside a workspace project",
        parameters={
            "script": {
                "type": "string",
                "description": "The npm script name, e.g. dev or test",
            },
            "cwd": {
                "type": "string",
                "description": "Relative working directory inside workspace",
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds",
            },
        },
        required=["script"],
    ),
    Tool(
        name="run_npm_install",
        func=run_npm_install,
        description="Run npm install inside a workspace project to install dependencies from package.json",
        parameters={
            "cwd": {
                "type": "string",
                "description": "Relative working directory inside workspace",
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds",
            },
        },
        required=[],
    ),
    Tool(
        name="install_python_package",
        func=install_python_package,
        description="Install a Python package using pip",
        parameters={
            "package": {
                "type": "string",
                "description": "Package name to install",
            },
            "cwd": {
                "type": "string",
                "description": "Relative working directory inside workspace",
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds",
            },
        },
        required=["package"],
    ),
    Tool(
        name="install_npm_package",
        func=install_npm_package,
        description="Install an npm package using npm install",
        parameters={
            "package": {
                "type": "string",
                "description": "Package name to install",
            },
            "cwd": {
                "type": "string",
                "description": "Relative working directory inside workspace",
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds",
            },
        },
        required=["package"],
    ),
    Tool(
        name="http_get",
        func=http_get,
        description="Make an HTTP GET request to an external API or website",
        parameters={
            "url": {
                "type": "string",
                "description": "Target URL",
            },
            "headers_json": {
                "type": "string",
                "description": "Optional JSON string of request headers",
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds",
            },
        },
        required=["url"],
    ),
    Tool(
        name="http_post",
        func=http_post,
        description="Make an HTTP POST request with a JSON body",
        parameters={
            "url": {
                "type": "string",
                "description": "Target URL",
            },
            "body_json": {
                "type": "string",
                "description": "Optional JSON string body",
            },
            "headers_json": {
                "type": "string",
                "description": "Optional JSON string of request headers",
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds",
            },
        },
        required=["url"],
    ),
    Tool(
        name="http_put",
        func=http_put,
        description="Make an HTTP PUT request with a JSON body",
        parameters={
            "url": {
                "type": "string",
                "description": "Target URL",
            },
            "body_json": {
                "type": "string",
                "description": "Optional JSON string body",
            },
            "headers_json": {
                "type": "string",
                "description": "Optional JSON string of request headers",
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds",
            },
        },
        required=["url"],
    ),
    Tool(
        name="http_delete",
        func=http_delete,
        description="Make an HTTP DELETE request",
        parameters={
            "url": {
                "type": "string",
                "description": "Target URL",
            },
            "headers_json": {
                "type": "string",
                "description": "Optional JSON string of request headers",
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds",
            },
        },
        required=["url"],
    ),
    Tool(
        name="download_file",
        func=download_file,
        description="Download a file from a URL into the workspace",
        parameters={
            "url": {
                "type": "string",
                "description": "File URL",
            },
            "output_path": {
                "type": "string",
                "description": "Relative destination path inside workspace",
            },
        },
        required=["url", "output_path"],
    ),
    Tool(
        name="start_background_command",
        func=start_background_command,
        description="Start a long-running command in the background, such as a dev server",
        parameters={
            "command": {
                "type": "string",
                "description": "Command string to execute in the background",
            },
            "cwd": {
                "type": "string",
                "description": "Relative working directory inside workspace",
            },
            "startup_wait": {
                "type": "integer",
                "description": "Seconds to wait before checking if the process started",
            },
        },
        required=["command"],
    ),
    Tool(
        name="list_background_processes",
        func=list_background_processes,
        description="List tracked background processes started by the agent",
        parameters={},
        required=[],
    ),
    Tool(
        name="stop_background_process",
        func=stop_background_process,
        description="Stop a tracked background process using its process_id",
        parameters={
            "process_id": {
                "type": "string",
                "description": "Tracked background process identifier",
            },
        },
        required=["process_id"],
    ),
    Tool(
        name="web_search",
        func=web_search,
        description="Search the live web for current information using a web search API",
        parameters={
            "query": {
                "type": "string",
                "description": "Search query to look up on the web",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of search results to return",
            },
            "search_depth": {
                "type": "string",
                "description": "Search depth, usually 'basic' or 'advanced'",
            },
            "topic": {
                "type": "string",
                "description": "Search topic, such as 'general' or 'news'",
            },
            "include_answer": {
                "type": "boolean",
                "description": "Whether to include a synthesized answer",
            },
            "include_raw_content": {
                "type": "boolean",
                "description": "Whether to include extracted raw webpage content",
            },
        },
        required=["query"],
    ),
]


TOOL_MAP = {tool.name: tool for tool in TOOLS}


def get_tool_by_name(name: str):
    return TOOL_MAP.get(name)


def get_tool_schemas():
    """
    Format tools for LLM prompt consumption.
    """
    return [
        {
            "name": tool.name,
            "description": tool.description,
            "parameters": {
                "type": "object",
                "properties": tool.parameters,
                "required": tool.required,
            },
        }
        for tool in TOOLS
    ]
