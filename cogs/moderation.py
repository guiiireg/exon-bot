"""Moderation cog for the bot.

Provides administrative slash commands for server moderation, including message deletion and member kick with permission checks.
"""

import discord
from discord import app_commands
from discord.ext import commands


class Moderation(commands.Cog):
    """Cog handling moderation slash commands"""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the Moderation cog with the bot instance

        Args:
            bot: The main bot client instance
        """
        self.bot = bot

    @app_commands.command(
        name="clear",
        description="Deletes a specified number of recent messages from the channel",
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.describe(amount="The number of message to delete")
    async def clear(
        self, interaction: discord.Interaction, amount: app_commands.Range[int, 1, 100]
    ) -> None:
        """Handle the clear slash commands to bulk delete channel message

        Args:
            interaction: The discord interaction context
            amount: The number of messages to purge
        """
        channel = interaction.channel

        if not isinstance(
            channel, (discord.TextChannel, discord.Thread, discord.VoiceChannel)
        ):
            await interaction.response.send_message(
                "Cannot purge messages in this type of channel",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)

        deleted = await channel.purge(limit=amount)
        await interaction.followup.send(
            f"Successfully deleted {len(deleted)} messages.", ephemeral=True
        )

    @app_commands.command(
        name="kick", description="Kicks a specified member from the server"
    )
    @app_commands.checks.has_permissions(kick_members=True)
    @app_commands.describe(
        member="The guild member to kick", reason="Optional reason for the kick"
    )
    async def kick(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str | None = None,
    ) -> None:
        """Handle the kick slash command to eject a member from the guild

        Args:
            interaction: The discord interaction context
            member: The target guild member to kick
            reason: Optional justification recorded in audit logs
        """
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message(
                "This command can only be used within a server", ephemeral=True
            )
            return

        if member == interaction.user:
            await interaction.response.send_message(
                "You cannot kick yourself", ephemeral=True
            )
            return

        effective_reason = reason or "No reason provided"
        await member.kick(reason=effective_reason)

        embed = discord.Embed(
            title="Member Kicked",
            color=discord.Color.orange(),
        )
        embed.add_field(
            name="Target", value=f"{member.mention} ({member.name})", inline=False
        )
        embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
        embed.add_field(name="Reason", value=effective_reason, inline=True)

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """Entry point required by discord to load the cog"""
    await bot.add_cog(Moderation(bot))
