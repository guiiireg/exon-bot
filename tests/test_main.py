"""Unit tests for ExonBot error handling in main.py.

Tests cover the on_app_command_error handler for:
- CommandOnCooldown
- MissingPermissions
- BotMissingPermissions
- Unexpected / unhandled errors
"""

import sys
import types
import unittest
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

import pytest

# ---------------------------------------------------------------------------
# Patch env variables BEFORE importing main so the module-level guards pass
# ---------------------------------------------------------------------------
ENV_PATCH = {
    "TOKEN": "fake-token",
    "SERVER_ID": "123456789",
}


@pytest.fixture(autouse=True)
def _patch_env(monkeypatch):
    for key, value in ENV_PATCH.items():
        monkeypatch.setenv(key, value)


# We import ExonBot lazily inside each test so env patches are applied first.
def _get_bot():
    # Re-import each time to pick up mocked env
    import importlib

    with patch("discord.ext.commands.Bot.__init__", return_value=None):
        with patch("discord.Object"):
            # Avoid re-running module-level code
            import main as m

            bot = object.__new__(m.ExonBot)
    return bot


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_interaction(*, response_done: bool = False, command_name: str = "test"):
    """Build a minimal mock discord.Interaction."""
    interaction = MagicMock()
    interaction.command = MagicMock()
    interaction.command.name = command_name
    interaction.response = MagicMock()
    interaction.response.is_done.return_value = response_done
    interaction.response.send_message = AsyncMock()
    interaction.followup = MagicMock()
    interaction.followup.send = AsyncMock()
    return interaction


def _make_cooldown_error(retry_after: float = 5.0):
    from discord import app_commands

    error = MagicMock(spec=app_commands.CommandOnCooldown)
    error.retry_after = retry_after
    return error


def _make_missing_perms_error(missing: list[str] | None = None):
    from discord import app_commands

    error = MagicMock(spec=app_commands.MissingPermissions)
    error.missing_permissions = missing or ["administrator"]
    return error


def _make_bot_missing_perms_error(missing: list[str] | None = None):
    from discord import app_commands

    error = MagicMock(spec=app_commands.BotMissingPermissions)
    error.missing_permissions = missing or ["send_messages", "embed_links"]
    return error


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestOnAppCommandError:
    @pytest.fixture(autouse=True)
    def setup(self, monkeypatch):
        for key, value in ENV_PATCH.items():
            monkeypatch.setenv(key, value)

        with (
            patch("discord.ext.commands.Bot.__init__", return_value=None),
            patch("discord.Object", return_value=MagicMock()),
        ):
            import main as m

            self.bot = object.__new__(m.ExonBot)

    # --- CommandOnCooldown --------------------------------------------------

    async def test_cooldown_sends_retry_message(self):
        """on_app_command_error should reply with the cooldown duration."""
        interaction = _make_interaction(response_done=False)
        error = _make_cooldown_error(retry_after=7.3)

        await self.bot.on_app_command_error(interaction, error)

        interaction.response.send_message.assert_awaited_once()
        sent_text: str = interaction.response.send_message.call_args[0][0]
        assert "7.3" in sent_text
        assert "cooldown" in sent_text.lower()

    async def test_cooldown_uses_ephemeral(self):
        """Cooldown reply must be ephemeral."""
        interaction = _make_interaction(response_done=False)
        error = _make_cooldown_error()

        await self.bot.on_app_command_error(interaction, error)

        _, kwargs = interaction.response.send_message.call_args
        assert kwargs.get("ephemeral") is True

    # --- MissingPermissions -------------------------------------------------

    async def test_missing_perms_lists_permissions(self):
        """on_app_command_error should list the user's missing permissions."""
        interaction = _make_interaction(response_done=False)
        error = _make_missing_perms_error(missing=["ban_members", "kick_members"])

        await self.bot.on_app_command_error(interaction, error)

        sent_text: str = interaction.response.send_message.call_args[0][0]
        assert "ban_members" in sent_text
        assert "kick_members" in sent_text

    async def test_missing_perms_single_permission(self):
        """Works correctly with a single missing permission."""
        interaction = _make_interaction(response_done=False)
        error = _make_missing_perms_error(missing=["administrator"])

        await self.bot.on_app_command_error(interaction, error)

        sent_text: str = interaction.response.send_message.call_args[0][0]
        assert "administrator" in sent_text

    # --- BotMissingPermissions ----------------------------------------------

    async def test_bot_missing_perms_lists_permissions(self):
        """on_app_command_error should list the bot's missing permissions."""
        interaction = _make_interaction(response_done=False)
        error = _make_bot_missing_perms_error(missing=["embed_links", "attach_files"])

        await self.bot.on_app_command_error(interaction, error)

        sent_text: str = interaction.response.send_message.call_args[0][0]
        assert "embed_links" in sent_text
        assert "attach_files" in sent_text

    async def test_bot_missing_perms_message_mentions_bot(self):
        """The bot missing perms message should reference the bot, not the user."""
        interaction = _make_interaction(response_done=False)
        error = _make_bot_missing_perms_error()

        await self.bot.on_app_command_error(interaction, error)

        sent_text: str = interaction.response.send_message.call_args[0][0]
        # Should mention "I" (bot perspective), not "You"
        assert sent_text[0].upper() == "I"

    # --- Unexpected error ---------------------------------------------------

    async def test_unexpected_error_sends_generic_message(self):
        """Unhandled errors should reply with a generic message."""
        from discord import app_commands

        interaction = _make_interaction(response_done=False)
        error = MagicMock(spec=app_commands.AppCommandError)

        with patch("traceback.print_exception"):
            await self.bot.on_app_command_error(interaction, error)

        interaction.response.send_message.assert_awaited_once()
        sent_text: str = interaction.response.send_message.call_args[0][0]
        assert "unexpected" in sent_text.lower() or "error" in sent_text.lower()

    async def test_unexpected_error_uses_followup_when_response_done(self):
        """If the response is already sent, followup.send should be used."""
        from discord import app_commands

        interaction = _make_interaction(response_done=True)
        error = MagicMock(spec=app_commands.AppCommandError)

        with patch("traceback.print_exception"):
            await self.bot.on_app_command_error(interaction, error)

        interaction.followup.send.assert_awaited_once()
        interaction.response.send_message.assert_not_awaited()

    async def test_unexpected_error_uses_send_message_when_response_not_done(self):
        """If the response is not yet sent, send_message should be used."""
        from discord import app_commands

        interaction = _make_interaction(response_done=False)
        error = MagicMock(spec=app_commands.AppCommandError)

        with patch("traceback.print_exception"):
            await self.bot.on_app_command_error(interaction, error)

        interaction.response.send_message.assert_awaited_once()
        interaction.followup.send.assert_not_awaited()

    async def test_unexpected_error_followup_is_ephemeral(self):
        """Followup reply for unexpected errors must be ephemeral."""
        from discord import app_commands

        interaction = _make_interaction(response_done=True)
        error = MagicMock(spec=app_commands.AppCommandError)

        with patch("traceback.print_exception"):
            await self.bot.on_app_command_error(interaction, error)

        _, kwargs = interaction.followup.send.call_args
        assert kwargs.get("ephemeral") is True

    async def test_unexpected_error_prints_traceback(self):
        """Unhandled errors should log the traceback to stdout."""
        from discord import app_commands

        interaction = _make_interaction(response_done=False)
        error = MagicMock(spec=app_commands.AppCommandError)

        with patch("traceback.print_exception") as mock_tb:
            await self.bot.on_app_command_error(interaction, error)

        mock_tb.assert_called_once()

    # --- Ephemeral on all known errors --------------------------------------

    @pytest.mark.parametrize(
        "make_error",
        [
            lambda: _make_cooldown_error(),
            lambda: _make_missing_perms_error(),
            lambda: _make_bot_missing_perms_error(),
        ],
        ids=["cooldown", "user_missing_perms", "bot_missing_perms"],
    )
    async def test_known_errors_are_ephemeral(self, make_error):
        """All known error replies should be ephemeral."""
        interaction = _make_interaction(response_done=False)
        error = make_error()

        await self.bot.on_app_command_error(interaction, error)

        interaction.response.send_message.assert_awaited_once()
        _, kwargs = interaction.response.send_message.call_args
        assert kwargs.get("ephemeral") is True
