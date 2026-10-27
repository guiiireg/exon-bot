"""Application configuration loaded from the environment."""

import os
from dataclasses import dataclass
from pathlib import Path

_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


def _load_env_file() -> None:
    """Load variables from the .env file without overriding existing ones."""
    if not _ENV_FILE.is_file():
        return
    for line in _ENV_FILE.read_text(encoding="utf-8").splitlines():
        key, separator, value = line.strip().partition("=")
        if not separator or not key or key.startswith("#"):
            continue
        os.environ.setdefault(key, value)


@dataclass(frozen=True)
class BotConfig:
    """Runtime configuration for the bot."""

    token: str
    server_id: int | None = None


def load_config() -> BotConfig:
    """Build the configuration from the environment."""
    _load_env_file()
    token = os.environ.get("TOKEN", "")
    if not token:
        raise RuntimeError("TOKEN not found in the environment or .env file")
    raw_server_id = os.environ.get("SERVER_ID", "")
    server_id = int(raw_server_id) if raw_server_id.isdigit() else None
    return BotConfig(token=token, server_id=server_id)
