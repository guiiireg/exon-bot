import os
import sys

import discord
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("DISCORD_TOKEN")
guild_str = os.getenv("GUILD_ID")

if guild_str is None:
    print(
        "[WARNING] GUILD_ID is missing, check if .env or variable is named correctly."
    )
    sys.exit(1)

guild = int(guild_str)

intents = discord.Intents.default()

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@tree.command(guild=discord.Object(id=guild))
async def ping(interaction: discord.Interaction) -> None:
    """
    Get the bot's latency

    Parameters
    ----------
    interaction : discord.Interaction
        The interaction object
    """
    await interaction.response.send_message("Pong")


if token is None:
    print(
        "[WARNING] DISCORD_TOKEN is missing, check if .env or variable is named correctly."
    )
    sys.exit(1)


@client.event
async def on_ready():
    print("[INFORMATIONS] Bot is ready to be used.")
    await tree.sync(guild=discord.Object(id=guild))


client.run(token=token)
