"""Extension (cog) loading for the bot."""

from discord.ext import commands

EXTENSIONS: list[str] = [
    "exon_bot.discord_app.cogs.general",
    "exon_bot.discord_app.cogs.administration",
]


async def load_extensions(bot: commands.Bot) -> None:
    """Load every extension listed in EXTENSIONS."""
    for extension in EXTENSIONS:
        await bot.load_extension(extension)
