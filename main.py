"""Main entry point for the Bot.

Handles env config, custom bot init, dynamic extension loading, and
application command tree sync to establish the WebSocket connection.
"""

import os
import traceback

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from database.db import DatabaseManager

# Load env variables
load_dotenv()

TOKEN: str | None = os.getenv("TOKEN")
SERVER_ID_RAW: str | None = os.getenv("SERVER_ID")

if not TOKEN:
    raise ValueError("Error: TOKEN is missing in the .env file.")
if not SERVER_ID_RAW:
    raise ValueError("Error: SERVER_ID is missing in the .env file.")

GUILD_OBJ = discord.Object(id=int(SERVER_ID_RAW))


class ExonBot(commands.Bot):
    """Custom Bot client"""

    def __init__(self) -> None:
        """Initialize the bot instance with default intents and no message prefix"""
        intents = discord.Intents.default()
        super().__init__(command_prefix=[], intents=intents)
        self.db = DatabaseManager()

    async def on_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:
        """Global error handler for app slash commands

        Args:
            interaction: The interaction context where the error occurred.
            error: The exception raised during command execution.
        """
        if isinstance(error, app_commands.CommandOnCooldown):
            message = f"This command is on cooldown. Try again {error.retry_after:.1f} seconds"
        elif isinstance(error, app_commands.MissingPermissions):
            missing_perms = ", ".join(error.missing_permissions)
            message = f"You are missing required permissions: {missing_perms}"
        elif isinstance(error, app_commands.BotMissingPermissions):
            missing_perms = ", ".join(error.missing_permissions)
            message = (
                f"I am missing required permissions to execute this: {missing_perms}"
            )
        else:
            message = "An unexpected error occurred while processing this command"
            print(
                f"Unhandled command error in '/{interaction.command.name if interaction.command else 'unknown'}:"
            )
            traceback.print_exception(type(error), error, error.__traceback__)

        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)

    async def setup_hook(self) -> None:
        """Execute async setup tasks prior to websocket connection

        Dynamically load all valid cogs from the cogs directory and syncs
        application commands once before startup.
        """
        cogs_dir = "./cogs"
        if os.path.exists(cogs_dir):
            for filename in os.listdir(cogs_dir):
                if filename.endswith(".py") and not filename.startswith("_"):
                    extension_name = f"cogs.{filename[:-3]}"
                    await self.load_extension(extension_name)
                    print(f"Loaded extensions: {extension_name}")

        self.tree.copy_global_to(guild=GUILD_OBJ)
        synced_commands = await self.tree.sync(guild=GUILD_OBJ)
        print(f"Successfully synchronized {len(synced_commands)} commands to server")

        await self.db.init_db()
        print("Database initialized successfully.")

    async def on_ready(self) -> None:
        """Event handler triggered when the bot connection is established"""
        if self.user:
            print(f"Connected successfully as {self.user.name}")


bot = ExonBot()

if __name__ == "__main__":
    bot.run(TOKEN)
