# tests/conftest.py

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest


@pytest.fixture
def interaction():
    """Simulates a Discord interaction."""
    return SimpleNamespace(
        response=SimpleNamespace(
            send_message=AsyncMock(),
            is_done=lambda: False,
        ),
        followup=SimpleNamespace(
            send=AsyncMock(),
        ),
        guild=None,
        user=object(),
        command=SimpleNamespace(name="test"),
    )
