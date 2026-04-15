# utils/llm_client.py
from models.LLM.openai_client import OpenAIClient
# from models.LLM.claude_client import ClaudeClient
from models.LLM.ollama_client import OllamaClient
from models.LLM.base_client import BaseLLMClient

def get_llm_client(provider: str) -> BaseLLMClient:
    if provider == "openai":
        return OpenAIClient()
#     elif provider == "claude":
#         return ClaudeClient()
    elif provider == "ollama":
        return OllamaClient()
    else:
        raise ValueError(f"Unsupport provider: {provider}")

