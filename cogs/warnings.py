"""User warnings management cog for the bot

Provides moderation commands to issue warnings and display
a member warning history.
"""

import discord
from discord import app_commands
from discord.ext import commands


class Warnings(commands.Cog):
    """Cog handling user warning slash command"""

    def __init__(self, bot: commands.Bot) -> None:
        """Init the warning cog with the bot instance

        Args:
            bot: The main bot client instance
        """
        self.bot = bot

    @app_commands.command(
        name="warn", description="Issues a formal warning to a server member"
    )
    @app_commands.checks.has_permissions(kick_members=True)
    @app_commands.describe(member="The member to warn", reason="Reason for the warning")
    async def warn(
        self, interaction: discord.Interaction, member: discord.Member, reason: str
    ) -> None:
        """Handle the warn slash command to record a warning

        Args:
            interaction: The discord interaction context.
            member: The guild member receiving the warning.
            reason: Text explaining the warning justification.
        """
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message(
                "This command can only be executed within a server.", ephemeral=True
            )
            return

        if member.bot:
            await interaction.response.send_message(
                "YOu cannot issue warnings to bot accounts.", ephemeral=True
            )
            return

        warning_id = await self.bot.db.add_warning(
            user_id=member.id,
            guild_id=guild.id,
            moderator_id=interaction.user.id,
            reason=reason,
        )

        embed = discord.Embed(title="Member Warned", color=discord.Color.gold())
        embed.add_field(name="Warning ID", value=f"#{warning_id}", inline=True)
        embed.add_field(name="Target", value=member.mention, inline=True)
        embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="warning", description="Displays warning history for a specified member"
    )
    @app_commands.describe(member="Optional target member to check")
    async def warnings(
        self, interaction: discord.Interaction, member: discord.Member | None = None
    ) -> None:
        """Handle the warning slash command to view warning history

        Args:
            interaction: The discord interaction context
            member: Optional target member to inspect
        """
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message(
                "This command can only be executed within a server", ephemeral=True
            )
            return

        target = member or interaction.user
        records = await self.bot.db.get_warnings(user_id=target.id, guild_id=guild.id)

        embed = discord.Embed(
            title=f"Warnings history: {target.display_name}",
            color=discord.Color.orange(),
        )

        if not records:
            embed.description = "No warnings found for this member"
        else:
            for record in records:
                embed.add_field(
                    name=f"Warning #{record['id']} | {record['created_at']}",
                    value=f"**Reason:** {record['reason']}\n**Moderator ID:** {record['moderator_id']}",
                    inline=False,
                )

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """Entry point required by discord to load the cog"""
    await bot.add_cog(Warnings(bot))
