"""Administration commands."""

from typing import cast

import discord
from discord import app_commands
from discord.ext import commands


class Administration(commands.Cog):
    """Commands for server administration."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(
        name="purge", description="Bulk delete messages in this channel."
    )
    @app_commands.guild_only()
    @app_commands.describe(count="Number of messages to delete (1-100)")
    @app_commands.default_permissions(manage_messages=True)
    async def purge(
        self,
        interaction: discord.Interaction,
        count: app_commands.Range[int, 1, 100],
    ) -> None:
        channel = cast(discord.TextChannel, interaction.channel)
        await interaction.response.defer(ephemeral=True)
        deleted = await channel.purge(limit=count)
        await interaction.followup.send(
            f"Deleted {len(deleted)} message(s) in {channel.mention}.",
            ephemeral=True,
        )

    @app_commands.command(
        name="slowmode", description="Set the slowmode delay of this channel."
    )
    @app_commands.guild_only()
    @app_commands.describe(
        seconds="Delay in seconds between 0 and 21600; 0 disables slowmode"
    )
    @app_commands.default_permissions(manage_channels=True)
    async def slowmode(
        self,
        interaction: discord.Interaction,
        seconds: app_commands.Range[int, 0, 21600],
    ) -> None:
        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel):
            await interaction.response.send_message(
                "Slowmode can only be set on a text channel.",
                ephemeral=True,
            )
            return
        await channel.edit(slowmode_delay=seconds)
        if seconds == 0:
            await interaction.response.send_message(
                f"Slowmode disabled in {channel.mention}."
            )
        else:
            await interaction.response.send_message(
                f"Slowmode set to {seconds}s in {channel.mention}."
            )

    @app_commands.command(name="nick", description="Change a member's nickname.")
    @app_commands.guild_only()
    @app_commands.describe(
        member="Member to rename; defaults to you",
        nickname="New nickname; leave empty to reset",
    )
    @app_commands.default_permissions(manage_nicknames=True)
    async def nick(
        self,
        interaction: discord.Interaction,
        member: discord.Member | None = None,
        nickname: str | None = None,
    ) -> None:
        member = member or cast(discord.Member, interaction.user)
        if interaction.user != member and not (
            interaction.guild is not None
            and (
                interaction.user.id == interaction.guild.owner_id
                or interaction.user.top_role > member.top_role
            )
        ):
            await interaction.response.send_message(
                "Your top role is not high enough to rename that member.",
                ephemeral=True,
            )
            return
        me = interaction.guild.me if interaction.guild else None
        if me and member != me and member.top_role >= me.top_role:
            await interaction.response.send_message(
                "My top role is not high enough to rename that member.",
                ephemeral=True,
            )
            return
        try:
            await member.edit(nick=nickname)
        except discord.Forbidden:
            await interaction.response.send_message(
                "I don't have permission to rename that member.",
                ephemeral=True,
            )
            return
        if nickname:
            await interaction.response.send_message(
                f"Changed nickname of {member.mention} to **{nickname}**."
            )
        else:
            await interaction.response.send_message(
                f"Reset nickname of {member.mention}."
            )


async def setup(bot: commands.Bot) -> None:
    """Entry point required by load_extension to register the cog."""
    await bot.add_cog(Administration(bot))
