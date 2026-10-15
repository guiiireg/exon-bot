"""User utility cog for the Bot

Provides user-related slash commands, such as displaying detailed information
about a server member or the command invoker.
"""

import discord
from discord import app_commands
from discord.ext import commands


class User(commands.Cog):
    """Cog handling user-related slash commands"""

    def __init__(self, bot: commands.Bot) -> None:
        """Init the User cog with the bot instance.

        Args:
            bot: The main bot client instance.
        """
        self.bot = bot

    @app_commands.command(
        name="user-info",
        description="Displays information about a server member or yourself",
    )
    async def user_info(
        self, interaction: discord.Interaction, member: discord.Member | None = None
    ) -> None:
        """Handle the user-info slash commands to display member details

        Args:
            interaction: The Discord interaction context triggered by the user.
            member: Optional target guild member to inspect.
        """
        target = member or interaction.user

        if not isinstance(target, discord.Member):
            await interaction.response.send_message(
                "Unable to retrieve guild member details for this user.",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title=f"User Information: {target.display_name}",
            color=target.color
            if target.color != discord.Color.default()
            else discord.Color.blue(),
        )

        if target.display_avatar:
            embed.set_thumbnail(url=target.display_avatar.url)

        embed.add_field(name="Username", value=target.name, inline=True)
        embed.add_field(name="User ID", value=str(target.id), inline=True)

        embed.add_field(
            name="Created On",
            value=discord.utils.format_dt(target.created_at, style="F"),
            inline=False,
        )

        if target.joined_at:
            embed.add_field(
                name="Joined server",
                value=discord.utils.format_dt(target.joined_at, style="R"),
                inline=False,
            )

        roles = [role.mention for role in target.roles if not role.is_default()]
        if roles:
            role_display = (
                ", ".join(roles)
                if len(roles) <= 10
                else f"{len(roles)} roles assigned."
            )
            embed.add_field(
                name=f"Roles [{len(roles)}]", value=role_display, inline=False
            )

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """Entry point required by discord.py to load the cog"""
    await bot.add_cog(User(bot))
