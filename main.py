import os
import sys

import discord
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@tree.command()
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


client.run(token=token)
