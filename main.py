import os

import discord
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
GUILD_ID = os.getenv("SERVER_ID")

if not TOKEN:
    raise ValueError("TOKEN not found in .env file.")
if not GUILD_ID:
    raise ValueError("GUILD_ID not found in .env file.")

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)
guild = discord.Object(id=GUILD_ID)


@tree.command(name="ping", description="Pong", guild=guild)
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("pong")


@client.event
async def on_ready():
    await tree.sync(guild=guild)
    print(f"Connected as {client.user}")


client.run(TOKEN)
