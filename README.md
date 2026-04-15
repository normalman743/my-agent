# Star Agent 🤖

A practical LLM Agent with tool calling, built from scratch through 7 iterative versions.

This project documents my journey of building an AI Agent from a simple Ollama chat script to a modular, multi-provider system with automatic tool registration — learning by doing, not by framework.

## V7.0 — Current Version

The latest version features a clean architecture with three core ideas:

### 1. `@tool` Decorator Auto-Registration
Define a tool as a plain Python function. The registry inspects type hints and generates JSON Schema automatically — no manual schema writing.

```python
from agent.tools.registry import tool

@tool(description="Execute a shell command")
def terminal(command: str, sudo: bool = False, timeout: int = 60) -> str:
    ...
```

The agent passes these schemas to the LLM, and when the LLM calls a tool, the registry dispatches and executes it.

### 2. Provider Abstraction
Swap between Ollama (local) and OpenAI (cloud) with one flag. Both implement the same `BaseLLMProvider` interface, so the Agent core doesn't care which backend is running.

```bash
python main.py                    # Ollama (default)
python main.py --provider openai  # OpenAI
python main.py --model qwen2.5:14b
```

### 3. Recursive Tool Calling Loop
When the LLM requests a tool, the agent executes it, feeds the result back, and lets the LLM decide whether to call another tool or respond. This enables multi-step tasks like: diagnose → fix → verify.

## Project Structure

```
V7.0 Agent/
├── main.py                 # CLI entry point
├── agent/
│   ├── config.py           # Settings from .env (no hardcoded secrets)
│   ├── prompts.py          # System prompt
│   ├── core.py             # Agent loop + history management
│   ├── providers/
│   │   ├── base.py         # Abstract base class (ABC)
│   │   ├── ollama.py       # Ollama native tool calling
│   │   └── openai.py       # OpenAI function calling
│   └── tools/
│       ├── registry.py     # @tool decorator + schema generation
│       ├── terminal.py     # Local shell execution
│       ├── ssh.py          # Remote execution via SSH
│       └── search.py       # Google Custom Search
├── .env.example            # Environment template
└── requirements.txt
```

## Quick Start

```bash
cd "V7.0 Agent"
pip install -r requirements.txt
cp .env.example .env        # Edit .env with your settings
python main.py
```

**Requirements**: Python 3.9+, [Ollama](https://ollama.com/) running locally (for default mode)

## Bonus: Side Experiments

The repo also includes two side experiments that ran in parallel:

- **[`v0.1 star/`](v0.1%20star/)** — A PyQt5 desktop AI pet with 60fps render loop, particle effects, CPU/memory monitoring, and multiple mood states (`idle` / `processing` / `alert` / `sleep_mode`). Technically over-engineered for a pet, but good Qt/threading practice.
- **[`逆向/`](逆向/)** — JavaScript reverse-engineering experiments with AI-assisted game analysis (strategy maps, balanced AI scripts).

## Version History

This repo preserves all iterations to show the architectural evolution:

| Version | What Changed | Key Lesson |
|---------|-------------|------------|
| **V0.1** | Single-file Ollama chat | Streaming API basics |
| **V0.2** | Error handling, Chinese UX | Defensive programming |
| **V0.3** | Class refactor, vision, multi-model conversation | OOP patterns, `<think>` tag parsing |
| **V1.0** | First modular architecture (`app/models/config/`) | Separation of concerns, Factory pattern |
| **V2.0** | OpenAI Function Calling via `tools` parameter | Native tool calling > regex parsing |
| **V3.0** | ⚠️ **Stopped** — tried forcing local model to output JSON | Local models can't reliably produce structured output |
| **V4.0** | Recovered with tag-based detection + terminal tool | Pragmatism over elegance |
| **V5.0** | Full modular framework, multi-provider, token counting | Over-engineering without reliable tool calling = tech debt |
| **V6.0** | Stripped to 4 files, Ollama native tools, SSH support | Simple + working > complex + broken |
| **V7.0** | Clean architecture: `@tool` registry, provider abstraction, recursive tool loop | The synthesis of all lessons learned |

### The V3.0 Lesson
V3.0 was deliberately abandoned because local models (llama3.1) couldn't reliably output structured JSON, causing the entire tool-dispatch pipeline to break on parse failures. This led to a key insight: **don't fight the model's limitations — use the API's native tool calling instead**. V6.0 and V7.0 both use Ollama's native `tools` parameter, which solved the problem at the protocol level.

## Tools

| Tool | Description |
|------|-------------|
| `terminal` | Local shell execution with sudo confirmation and dangerous command detection |
| `ssh_exec` | Remote command execution via SSH (paramiko) |
| `web_search` | Google Custom Search API |

Adding a new tool is one function + one decorator:

```python
@tool(description="Read a file and return its contents")
def read_file(path: str) -> str:
    with open(path) as f:
        return f.read()
```

## Configuration

All secrets are loaded from `.env` — never hardcoded. See [.env.example](V7.0%20Agent/.env.example) for all available settings.

## License

MIT
