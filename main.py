import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN: str | None = os.getenv("TOKEN")
SERVER_ID_RAW: str | None = os.getenv("SERVER_ID")

if not TOKEN:
    raise ValueError("Error: TOKEN is missing in the .env file.")
if not SERVER_ID_RAW:
    raise ValueError("Error: SERVER_ID is missing in the .env file.")

GUILD_OBJ = discord.Object(id=int(SERVER_ID_RAW))


class ExonBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        super().__init__(command_prefix=[], intents=intents)

    async def setup_hook(self) -> None:
        self.tree.copy_global_to(guild=GUILD_OBJ)
        synced_commands = await self.tree.sync(guild=GUILD_OBJ)
        print(f"Successfully synchronized {len(synced_commands)} commands to server.")

    async def on_ready(self) -> None:
        if self.user:
            print(f"Connected successfully as {self.user.name}.")


bot = ExonBot()


@bot.tree.command(name="ping", description="Responds with the bot latency")
async def ping(interaction: discord.Interaction):
    latency_ms: int = round(bot.latency * 1000)
    await interaction.response.send_message(f"{latency_ms} ms")


if __name__ == "__main__":
    bot.run(TOKEN)
