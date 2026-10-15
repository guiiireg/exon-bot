"""Main entry point for the Bot.

Handles env config, custom bot init, dynamic extension loading, and
application command tree sync to establish the WebSocket connection.
"""

import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

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

    async def setup_hook(self) -> None:
        """Execute async setup tasks prior to websocket connection.

        Loads extensions and syncs application commands once before startup.
        """
        await self.load_extension("cogs.general")

        self.tree.copy_global_to(guild=GUILD_OBJ)
        synced_commands = await self.tree.sync(guild=GUILD_OBJ)
        print(f"Successfully sync {len(synced_commands)} commands to server.")

    async def on_ready(self) -> None:
        """Event handler triggered when the bot connection is established"""
        if self.user:
            print(f"Connected successfully as {self.user.name}")


bot = ExonBot()

if __name__ == "__main__":
    bot.run(TOKEN)
