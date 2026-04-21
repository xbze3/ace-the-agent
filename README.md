# Autonomous Cognitive Engine (ACE) - The Agent

ACE is a modular AI agent designed to reason, plan, and execute tasks using tools.

It combines:

- Structured tool usage
- LLM-driven reasoning
- Safe execution environment
- CLI-based interaction

ACE functions as a lightweight developer agent capable of creating files, running code, managing processes, and retrieving information from the web.

---

## Features

- Multi-step reasoning loop
- Tool-based architecture (file, system, command, API, process tools)
- CLI interface (`ace`)
- Web search integration (Tavily)
- Multiple LLM providers:
    - Ollama (local or hosted)
    - OpenAI
- Safe execution environment
- Background process management

---

## Installation

#### Clone the repository

```bash
git clone https://github.com/xbze3/ace-the-agent.git
cd ace-the-agent
```

#### Create a virtual environment (recommended)

```bash
python -m venv venv
venv\Scripts\activate
```

#### Install ACE (editable mode)

```bash
pip install -e .
```

#### Run ACE

```bash
ace
```

---

## Configuration

Create a `.env` file in the project root.

#### Example:

```env
# Choose provider
LLM_PROVIDER=your_llm_provider   # "ollama" or "openai"

# Ollama
OLLAMA_BASE_URL=your_ollama_base_here
OLLAMA_MODEL=your_ollama_model
OLLAMA_API_KEY=your_ollama_api_key

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=your_openai_model

# Web Searches
TAVILY_API_KEY=your_tvly_api_key_here
```

---

## How It Works

ACE follows a structured loop:

1. Receive user input
2. Build prompt with tool context
3. Call LLM
4. Parse response
5. Execute tool (if requested)
6. Feed result back into loop
7. Repeat until completion

---

## Supported Capabilities

ACE supports a wide range of operations through its tool system:

#### File Operations

- Create, read, update, delete files
- Append content and perform targeted replacements

#### Directory & Workspace Management

- Create, inspect, and delete directories
- View workspace structure

#### Code Execution

- Run Python scripts
- Run Node.js scripts
- Install Python and Node packages
- Execute controlled system commands

#### Web & API Interaction

- Perform HTTP requests (GET, POST, PUT, DELETE)
- Search the web in real-time using Tavily

#### Process Management

- Start long-running background processes (servers, dev tools)
- Stop and manage running processes

---

## Workspace Model

ACE operates inside a controlled directory called the `workspace`.

- All files created by the agent are placed inside `workspace/`
- Any files you want ACE to read or modify must also be placed inside `workspace/`
- ACE cannot access files outside of the workspace for safety reasons

This ensures:

- Safe file operations
- No accidental modification of your system files
- Predictable behavior

---

## CLI Usage

#### Interactive mode

```bash
ace
```

---

## Project Structure

```
ace-agent/
│
├── core/         # Agent logic
├── llm/          # LLM client and parsing
├── runtime/      # Execution and logging
├── tools/        # Tool implementations
│
├── ace.py        # CLI entry point
├── workspace/    # Agent working directory
├── logs/         # Runtime logs
│
├── .env.example
├── .gitignore
├── README.md
├── pyproject.toml
```

---

## Safety Features

- Command restrictions (dangerous operations blocked)
- Workspace sandboxing (no path traversal)
- Controlled execution (no shell chaining)
- Separation of agent workspace from system files

---

## Limitations

- Depends on system environment (Node.js, Python, etc.)
- Background processes must be stopped before deleting directories
- No full sandboxing (yet)
- LLM output quality depends on provider

---

## Roadmap

- Smarter failure detection
- Environment diagnostics
- Persistent memory
- Plugin system
- Docker sandboxing
- Enhanced CLI commands

---

## License

This project is licensed under the **MIT License**
