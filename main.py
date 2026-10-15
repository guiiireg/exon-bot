import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load env variables from .env fil
load_dotenv()

TOKEN: str | None = os.getenv("TOKEN")
SERVER_ID_RAW: str | None = os.getenv("SERVER_ID")

if not TOKEN:
    raise ValueError("Error: TOKEN is missing in the .env file.")
if not SERVER_ID_RAW:
    raise ValueError("Error: SERVER_ID is missing in the .env file.")

# Target guild object used for instant local slash command sync
GUILD_OBJ = discord.Object(id=int(SERVER_ID_RAW))


class ExonBot(commands.Bot):
    """Custom Discord Bot client"""

    def __init__(self) -> None:
        """Initialize the bot instance with default intents and no message prefix"""
        intents = discord.Intents.default()
        super().__init__(command_prefix=[], intents=intents)

    async def setup_hook(self) -> None:
        """Execute async setup tasks prior to websocket connection.

        Syncs application commands once before startup to avoid rate-limiting issues
        associated with syncing inside the on_ready event
        """
        self.tree.copy_global_to(guild=GUILD_OBJ)
        synced_commands = await self.tree.sync(guild=GUILD_OBJ)
        print(f"Successfully synchronized {len(synced_commands)} commands to server.")

    async def on_ready(self) -> None:
        """Event handler triggered when the bot connection is established"""
        if self.user:
            print(f"Connected successfully as {self.user.name}.")


bot = ExonBot()


@bot.tree.command(name="ping", description="Responds with the bot latency")
async def ping(interaction: discord.Interaction):
    """Handle the /ping slash command to check responsiveness and WebSocket latency

    Args:
        interaction: The Discord interaction context triggered by the user.
    """
    latency_ms: int = round(bot.latency * 1000)
    await interaction.response.send_message(f"{latency_ms} ms")


if __name__ == "__main__":
    bot.run(TOKEN)
