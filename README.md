# Autonomous Cognitive Engine (ACE) - The Agent

ACE is a modular AI agent designed to reason, plan, and execute tasks using tools.

It combines:

- Structured tool usage
- LLM-driven reasoning
- Safe workspace execution
- Long-term memory retrieval
- Drop-in agent skills
- CLI-based interaction

ACE functions as a lightweight developer agent capable of creating files, running code, managing background processes, using project-specific skills, and retrieving information from the web.

---

## Features

- Multi-step reasoning loop
- Tool-based architecture for file, directory, command, API, and process operations
- CLI interface through the `ace` command
- Clean spinner-based runtime status display
- Optional detailed runtime logs with `/logs on`
- Long-term memory support
- Web search integration through Tavily
- Multiple LLM providers:
    - Ollama, local or hosted
    - OpenAI
- Safe workspace model with path traversal protection
- Background process management
- Drop-in skill system compatible with Anthropic-style `SKILL.md` files
- Project-local and global skill discovery

---

## Installation

### Clone the repository

```bash
git clone https://github.com/xbze3/ace-the-agent.git
cd ace-the-agent
```

### Create a virtual environment

On Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

On macOS/Linux:

```bash
python -m venv venv
source venv/bin/activate
```

### Install ACE in editable mode

```bash
pip install -e .
```

### Run ACE

```bash
ace
```

---

## Configuration

Create a `.env` file in the folder where you run ACE.

Example:

```env
# Choose provider
LLM_PROVIDER=your_llm_provider   # "ollama" or "openai"

# Number of steps agent is able to take before being forced to stop
MAX_STEPS=30

# Ollama
OLLAMA_BASE_URL=your_ollama_base_here
OLLAMA_MODEL=your_ollama_model
OLLAMA_API_KEY=your_ollama_api_key

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=your_openai_model

# Web Searches
TAVILY_API_KEY=your_tvly_api_key_here

# Embeddings
EMBEDDING_PROVIDER=your_embedding_provider
EMBEDDING_MODEL=your_embedding_model
EMBEDDING_BASE_URL=your_embedding_base_url
EMBEDDING_API_KEY=your_embedding_api_key
EMBEDDING_TIMEOUT=60

MEMORY_STORE_PROVIDER=your_memory_store_provider
MEMORY_DB_DIR=your_memory_db_path
MEMORY_COLLECTION=your_memory_collection
MEMORY_TOP_K=your_top_k
MEMORY_SIMILARITY_THRESHOLD=your_similarity_threshold

# Requests
LLM_REQUEST_TIMEOUT=your_request_timeout
LLM_MAX_RETRIES=your_max_retries
LLM_RETRY_BACKOFF_SECONDS=your_max_retry_backoff_in_seconds

# Show logs
ACE_SHOW_LOGS=false

# ACE Skills Directory Location
ACE_SKILLS_DIR=./.agents/skills

# ACE workspace
ACE_WORKSPACE_DIR=workspace
```

---

## Runtime Folder Model

ACE separates package code from runtime user/project data.

Recommended runtime layout:

```text
my-project/
├── .env
├── agents/
│   └── skills/
│       ├── frontend-design/
│       │   └── SKILL.md
│       ├── python-script-builder/
│       │   └── SKILL.md
│       └── nodejs-express-server/
│           └── SKILL.md
│
└── workspace/
    └── generated-files-here
```

Run ACE from inside `my-project/`:

```bash
ace
```

ACE will use the local `.env`, local skills, and local workspace.

---

## Workspace Model

ACE operates inside a controlled workspace directory.

By default:

```env
ACE_WORKSPACE_DIR=workspace
```

This means files are created inside:

```text
./workspace/
```

The workspace provides:

- Safe file operations
- Protection against path traversal
- Predictable file placement
- Separation between ACE package code and generated user files

Any files you want ACE to read, modify, or execute should be placed inside the workspace.

---

## Skill System

ACE supports drop-in skills using Anthropic-style `SKILL.md` files.

A skill is a folder containing a `SKILL.md` file with YAML frontmatter and Markdown instructions.

Example:

```text
agents/skills/frontend-design/SKILL.md
```

Example skill:

```md
---
name: frontend-design
description: Create distinctive, production-grade frontend interfaces, websites, landing pages, React components, and HTML/CSS layouts.
---

# Frontend Design

Use this skill when the user asks to create or improve a frontend interface.
```

### Skill discovery order

ACE can discover skills from multiple locations:

1. Paths provided by `ACE_SKILLS_DIR`
2. `./agents/skills`
3. `./.agents/skills`
4. `~/.agents/skills`

This allows ACE to use both project-local skills and globally installed skills.

### Multiple skill directories

You can provide multiple skill directories using semicolons:

```env
ACE_SKILLS_DIR=agents/skills;C:/Users/yourname/.agents/skills
```

### Manual skill invocation

You can force ACE to use a specific skill:

```text
/skill frontend-design create a single-page website
```

or:

```text
/frontend-design create a single-page website
```

### Global Anthropic skills

If you install skills globally with the `skills` CLI, they are commonly stored in:

```text
~/.agents/skills/
```

On Windows, that is usually:

```text
C:\Users\yourname\.agents\skills\
```

ACE can be configured to discover these automatically.

---

## CLI Usage

Start ACE:

```bash
ace
```

Available commands:

```text
/help       Show command help
/logs       Show current log display mode
/logs on    Show detailed runtime logs
/logs off   Show clean spinner/status mode
/clear      Clear terminal
/exit       End session
/quit       End session
```

Keyboard shortcuts:

```text
Ctrl+C              Gracefully stop ACE
Ctrl+Z then Enter   Gracefully stop ACE on Windows
```

---

## Logs

ACE has two terminal display modes.

Clean mode:

```text
ACE_SHOW_LOGS=false
```

This shows only high-level states such as:

```text
Selecting skill
Checking memory
Preparing context
Thinking
Parsing response
Running tool
Saving memory
```

Detailed mode:

```text
ACE_SHOW_LOGS=true
```

Or inside the CLI:

```text
/logs on
```

This shows detailed runtime information, including:

- Skill routing details
- LLM messages
- Raw LLM responses
- Parsed JSON
- Tool arguments
- Tool results
- Memory retrieval results

Runtime logs are still written to file even when terminal logs are hidden.

---

## How ACE Works

ACE follows a structured loop:

1. Receive user input
2. Select a relevant skill, if available
3. Search long-term memory
4. Build prompt with system rules, memory, active skill instructions, and available tools
5. Call the LLM
6. Parse the LLM response as JSON
7. Execute a tool if requested
8. Feed the tool result back into the loop
9. Repeat until a final answer is returned

The LLM must return exactly one of these formats:

```json
{
    "action": "tool_name",
    "arguments": {
        "param": "value"
    }
}
```

or:

```json
{
    "final_answer": "response text"
}
```

---

## Supported Capabilities

ACE supports a wide range of operations through its tool system.

### File Operations

- Create files
- Read files
- Update files
- Delete files
- Append content
- Perform targeted replacements

### Directory and Workspace Management

- Create directories
- Inspect directories
- Delete directories
- View workspace structure

### Code Execution

- Run Python scripts
- Run Node.js scripts
- Install Node dependencies
- Run npm scripts
- Execute controlled commands when no specialized tool fits

### Web and API Interaction

- Perform HTTP requests
- Search the web in real time using Tavily
- Test local servers and API endpoints

### Process Management

- Start long-running background processes
- Inspect tracked background processes
- Stop running processes

---

## Recommended Skills to Add

Good starter skills for testing ACE:

```text
frontend-design
python-script-builder
nodejs-express-server
code-review-debugger
api-client-tester
project-scaffolder
```

Example prompt:

```text
/skill python-script-builder create a Python script that reads a text file, counts the words, and outputs the top 10 most common words. Create a sample input file and run the script.
```

Example prompt:

```text
/skill frontend-design create a cute single-file HTML website and place it in the workspace.
```

Example prompt:

```text
/skill nodejs-express-server create a simple Express API with a health route, install dependencies, start the server, and test the endpoint.
```

---

## Project Structure

```text
ace-the-agent/
├── ace.py              # CLI entry point
├── core/               # Agent loop, prompt harness, state
├── llm/                # LLM client and response parser
├── memory/             # Long-term memory service
├── runtime/            # Executor, logger, spinner, process helpers
├── skills/             # Skill system code, not user skill content
│   └── core/
├── tools/              # Tool implementations and registry
├── pyproject.toml
├── README.md
└── .env.example
```

---

## Safety Features

- Workspace sandboxing
- Path traversal prevention
- Tool permission filtering for active skills
- Runtime enforcement of allowed tools
- Command restrictions
- No shell chaining for controlled command execution
- Background process tracking
- Graceful handling of tool failures
- JSON parsing and repair flow

---

## Limitations

- Not a full security sandbox
- LLM output quality depends on the selected provider and model
- Local models may time out on very large prompts
- Background processes must be managed carefully
- Some skills may need ACE-specific default tool permissions
- Skills are loaded at startup unless a reload command is added

---

## Roadmap

- `/skills list` command
- `/skills reload` command
- Embedding-based skill routing
- Hybrid skill routing: embeddings shortlist, LLM final decision
- Better environment diagnostics
- Docker-based sandboxing
- Richer memory controls
- Skill marketplace/import workflow
- Better package/runtime separation
- More robust automated code validation

---

## License

This project is licensed under the **MIT License**.
