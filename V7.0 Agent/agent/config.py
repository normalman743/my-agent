"""
Configuration management - loads all settings from .env file.
No hardcoded secrets. Ever.
"""
import os
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)


def _env(key: str, default: str = "") -> str:
    return os.getenv(key, default)


def _env_bool(key: str, default: bool = False) -> bool:
    return _env(key, str(default)).lower() in ("true", "1", "yes")


def _env_int(key: str, default: int = 0) -> int:
    try:
        return int(_env(key, str(default)))
    except ValueError:
        return default


@dataclass(frozen=True)
class OllamaConfig:
    api_url: str = field(default_factory=lambda: _env("OLLAMA_API_URL", "http://localhost:11434/api/chat"))
    model: str = field(default_factory=lambda: _env("OLLAMA_MODEL", "llama3.1:8b"))


@dataclass(frozen=True)
class OpenAIConfig:
    api_key: str = field(default_factory=lambda: _env("OPENAI_API_KEY"))
    model: str = field(default_factory=lambda: _env("OPENAI_MODEL", "gpt-4o-mini"))
    base_url: str = field(default_factory=lambda: _env("OPENAI_BASE_URL", "https://api.openai.com/v1"))


@dataclass(frozen=True)
class SSHConfig:
    host: str = field(default_factory=lambda: _env("SSH_HOST"))
    port: int = field(default_factory=lambda: _env_int("SSH_PORT", 22))
    user: str = field(default_factory=lambda: _env("SSH_USER"))
    key_path: str = field(default_factory=lambda: _env("SSH_KEY_PATH"))

    @property
    def enabled(self) -> bool:
        return bool(self.host and self.user)


@dataclass(frozen=True)
class SearchConfig:
    google_api_key: str = field(default_factory=lambda: _env("GOOGLE_SEARCH_API_KEY"))
    google_cse_id: str = field(default_factory=lambda: _env("GOOGLE_CSE_ID"))

    @property
    def google_enabled(self) -> bool:
        return bool(self.google_api_key and self.google_cse_id)


@dataclass(frozen=True)
class Settings:
    """Immutable application settings. All values from environment."""
    ollama: OllamaConfig = field(default_factory=OllamaConfig)
    openai: OpenAIConfig = field(default_factory=OpenAIConfig)
    ssh: SSHConfig = field(default_factory=SSHConfig)
    search: SearchConfig = field(default_factory=SearchConfig)
    trust: bool = field(default_factory=lambda: _env_bool("TRUST"))


# Singleton
settings = Settings()
