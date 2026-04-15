"""
V8.0 LangChain Demo

Replicates V7.0's core loop in ~50 lines using LangChain components.

V7.0 hand-rolled         →  LangChain equivalent
──────────────────────────────────────────────────────
@tool + _build_schema()  →  @tool (auto-generates JSON Schema)
providers/ollama.py      →  ChatOllama (wraps /api/chat internally)
agent/core._tool_loop()  →  AgentExecutor (handles the loop automatically)
"""

import subprocess
import shlex

from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate


# ── Tools ──────────────────────────────────────────────────────────────────

@tool
def terminal(command: str) -> str:
    """Execute a shell command and return its output."""
    try:
        result = subprocess.run(
            shlex.split(command),
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.stdout or result.stderr or "(no output)"
    except Exception as e:
        return f"Error: {e}"


# ── Model + Agent ───────────────────────────────────────────────────────────

llm = ChatOllama(model="llama3.1:8b")
tools = [terminal]

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant with access to shell tools. "
               "Always verify results before responding."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


# ── REPL ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("LangChain Agent (llama3.1:8b) — Ctrl+C or 'exit' to quit\n")
    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input or user_input.lower() in ("exit", "quit"):
                break
            result = executor.invoke({"input": user_input})
            print(f"\nAgent: {result['output']}\n")
        except (KeyboardInterrupt, EOFError):
            break
