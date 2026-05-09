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

from tools.project_tools import (
    check_node_environment,
    create_next_app,
    create_vite_app,
    create_react_app_vite,
    create_vue_app_vite,
    create_svelte_app_vite,
    create_astro_app,
    create_express_api,
    run_npm_dev,
    run_npm_build,
    run_npm_start,
    install_npm_packages,
    install_frontend_basics,
    install_backend_basics,
    install_typescript_node_dev_tools,
    init_shadcn,
    add_shadcn_component,
    add_shadcn_components,
    open_project_tree,
    list_processes,
    read_process_log,
    stop_process,
    stop_all_processes,
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
        name="check_node_environment",
        func=check_node_environment,
        description="Check whether Node.js, npm, and npx are available",
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
        name="create_next_app",
        func=create_next_app,
        description="Create a Next.js project non-interactively using create-next-app. Use this instead of raw run_command for Next.js projects.",
        parameters={
            "project_name": {
                "type": "string",
                "description": "Folder name for the new Next.js project",
            },
            "cwd": {
                "type": "string",
                "description": "Relative working directory inside workspace",
            },
            "use_typescript": {
                "type": "boolean",
                "description": "Whether to use TypeScript",
            },
            "use_tailwind": {
                "type": "boolean",
                "description": "Whether to configure Tailwind CSS",
            },
            "use_eslint": {
                "type": "boolean",
                "description": "Whether to configure ESLint",
            },
            "use_app_router": {
                "type": "boolean",
                "description": "Whether to use the Next.js App Router",
            },
            "use_src_dir": {
                "type": "boolean",
                "description": "Whether to use a src directory",
            },
            "import_alias": {
                "type": "string",
                "description": "Import alias, usually @/*",
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds",
            },
        },
        required=["project_name"],
    ),
    Tool(
        name="create_vite_app",
        func=create_vite_app,
        description="Create a Vite project non-interactively",
        parameters={
            "project_name": {
                "type": "string",
                "description": "Folder name for the new Vite project",
            },
            "template": {
                "type": "string",
                "description": "Vite template, such as react-ts, react, vue-ts, svelte-ts, vanilla-ts",
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
        required=["project_name"],
    ),
    Tool(
        name="create_react_app_vite",
        func=create_react_app_vite,
        description="Create a React + TypeScript app using Vite",
        parameters={
            "project_name": {
                "type": "string",
                "description": "Folder name for the new React project",
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
        required=["project_name"],
    ),
    Tool(
        name="create_vue_app_vite",
        func=create_vue_app_vite,
        description="Create a Vue + TypeScript app using Vite",
        parameters={
            "project_name": {
                "type": "string",
                "description": "Folder name for the new Vue project",
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
        required=["project_name"],
    ),
    Tool(
        name="create_svelte_app_vite",
        func=create_svelte_app_vite,
        description="Create a Svelte + TypeScript app using Vite",
        parameters={
            "project_name": {
                "type": "string",
                "description": "Folder name for the new Svelte project",
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
        required=["project_name"],
    ),
    Tool(
        name="create_astro_app",
        func=create_astro_app,
        description="Create an Astro project non-interactively",
        parameters={
            "project_name": {
                "type": "string",
                "description": "Folder name for the new Astro project",
            },
            "cwd": {
                "type": "string",
                "description": "Relative working directory inside workspace",
            },
            "template": {
                "type": "string",
                "description": "Astro template, usually basics",
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds",
            },
        },
        required=["project_name"],
    ),
    Tool(
        name="create_express_api",
        func=create_express_api,
        description="Create a small Express API project with package.json and src/server.js",
        parameters={
            "project_name": {
                "type": "string",
                "description": "Folder name for the new Express API project",
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
        required=["project_name"],
    ),
    Tool(
        name="run_npm_dev",
        func=run_npm_dev,
        description="Start npm run dev without blocking the agent",
        parameters={
            "cwd": {
                "type": "string",
                "description": "Relative working directory inside workspace",
            },
            "script": {
                "type": "string",
                "description": "Script name, usually dev",
            },
        },
        required=[],
    ),
    Tool(
        name="run_npm_build",
        func=run_npm_build,
        description="Run npm build and wait for completion",
        parameters={
            "cwd": {
                "type": "string",
                "description": "Relative working directory inside workspace",
            },
            "script": {
                "type": "string",
                "description": "Script name, usually build",
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds",
            },
        },
        required=[],
    ),
    Tool(
        name="run_npm_start",
        func=run_npm_start,
        description="Start npm run start without blocking the agent",
        parameters={
            "cwd": {
                "type": "string",
                "description": "Relative working directory inside workspace",
            },
            "script": {
                "type": "string",
                "description": "Script name, usually start",
            },
        },
        required=[],
    ),
    Tool(
        name="install_npm_packages",
        func=install_npm_packages,
        description="Install multiple npm packages from a space-separated string",
        parameters={
            "packages": {
                "type": "string",
                "description": "Space-separated npm packages to install",
            },
            "cwd": {
                "type": "string",
                "description": "Relative working directory inside workspace",
            },
            "dev": {
                "type": "boolean",
                "description": "Whether to install as dev dependencies",
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds",
            },
        },
        required=["packages"],
    ),
    Tool(
        name="install_frontend_basics",
        func=install_frontend_basics,
        description="Install common frontend libraries such as lucide-react, framer-motion, recharts, clsx, and tailwind-merge",
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
        name="install_backend_basics",
        func=install_backend_basics,
        description="Install common Node backend libraries such as express, cors, dotenv, and zod",
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
        name="install_typescript_node_dev_tools",
        func=install_typescript_node_dev_tools,
        description="Install TypeScript Node development tools",
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
        name="init_shadcn",
        func=init_shadcn,
        description="Initialize shadcn/ui non-interactively in an existing project",
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
        name="add_shadcn_component",
        func=add_shadcn_component,
        description="Add one shadcn/ui component",
        parameters={
            "component": {
                "type": "string",
                "description": "Component name, such as button, card, input, dialog",
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
        required=["component"],
    ),
    Tool(
        name="add_shadcn_components",
        func=add_shadcn_components,
        description="Add multiple shadcn/ui components from a space-separated string",
        parameters={
            "components": {
                "type": "string",
                "description": "Space-separated component names, such as button card input dialog",
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
        required=["components"],
    ),
    Tool(
        name="open_project_tree",
        func=open_project_tree,
        description="Return a simple project tree while ignoring large generated folders",
        parameters={
            "cwd": {
                "type": "string",
                "description": "Relative working directory inside workspace",
            },
            "max_depth": {
                "type": "integer",
                "description": "Maximum tree depth",
            },
        },
        required=[],
    ),
    Tool(
        name="list_processes",
        func=list_processes,
        description="List background processes started by project tools",
        parameters={},
        required=[],
    ),
    Tool(
        name="read_process_log",
        func=read_process_log,
        description="Read stdout or stderr logs from a background process started by project tools",
        parameters={
            "pid": {
                "type": "string",
                "description": "Process PID returned by a non-blocking project tool",
            },
            "stream": {
                "type": "string",
                "description": "stdout or stderr",
            },
            "lines": {
                "type": "integer",
                "description": "Number of recent lines to read",
            },
        },
        required=["pid"],
    ),
    Tool(
        name="stop_process",
        func=stop_process,
        description="Stop a background process started by project tools",
        parameters={
            "pid": {
                "type": "string",
                "description": "Process PID returned by a non-blocking project tool",
            },
        },
        required=["pid"],
    ),
    Tool(
        name="stop_all_processes",
        func=stop_all_processes,
        description="Stop all background processes started by project tools",
        parameters={},
        required=[],
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
