import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Successfully logged in as {bot.user}")


@bot.command()
async def hello(ctx):
    await ctx.send("Hello !")


def main() -> None:
    bot.run(TOKEN)
