"""Discord client definition."""

import discord
from discord.ext import commands

from exon_bot.core.config import BotConfig
from exon_bot.discord_app.extensions import load_extensions


class ExonBot(commands.Bot):
    """Bot handling the connection and command dispatch."""

    def __init__(self, config: BotConfig) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self.config = config

    async def setup_hook(self) -> None:
        await load_extensions(self)
        if self.config.server_id:
            guild = discord.Object(id=self.config.server_id)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        else:
            await self.tree.sync()
