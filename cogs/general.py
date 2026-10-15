"""General utility cog the the Bot.

Provides basic public slash commands for server interaction and diagnostics,
including latency and server stats.
"""

import discord
from discord import app_commands
from discord.ext import commands


class General(commands.Cog):
    """Cog handling general utility slash commands"""

    def __init__(self, bot: commands.Bot) -> None:
        """Init the general cog with the bot instance

        Args:
            bot: The main bot client instance
        """
        self.bot = bot

    @app_commands.command(name="ping", description="Responds with the bot latency")
    async def ping(self, interaction: discord.Interaction) -> None:
        """Handle the ping slash command to check responsiveness and WebSocket latency.

        Args:
            interaction: The discord interaction context triggered by the user
        """
        latency_ms: int = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"{latency_ms} ms")

    @app_commands.command(
        name="server-info",
        description="Displays details about the current server",
    )
    async def server_info(self, interaction: discord.Interaction) -> None:
        """Handle the server-info slash command to display server statistics

        Args:
            interaction: The discord interaction context triggered by the user.
        """
        guild = interaction.guild

        if not guild:
            await interaction.response.send_message(
                "This command can only be executed within a server", ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"Server Information: {guild.name}",
            color=discord.Color.blue(),
        )

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        embed.add_field(name="Server ID", value=str(guild.id), inline=True)
        embed.add_field(name="Member Count", value=str(guild.member_count), inline=True)

        if guild.created_at:
            formatted_date = discord.utils.format_dt(guild.created_at, style="F")
            embed.add_field(name="Created On", value=formatted_date, inline=False)

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """Entry point function required by discord.py to load the cog"""
    await bot.add_cog(General(bot))
