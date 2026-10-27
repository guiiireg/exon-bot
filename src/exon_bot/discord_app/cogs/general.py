"""General purpose commands."""

import platform
import time
from importlib.metadata import version as package_version
from typing import cast

import discord
from discord import app_commands
from discord.ext import commands


def _format_duration(seconds: float) -> str:
    """Format a duration as a human-readable string."""
    minutes, sec = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours or days:
        parts.append(f"{hours}h")
    parts.append(f"{minutes}m {sec}s")
    return " ".join(parts)


class General(commands.Cog):
    """Commands available to everyone."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.started_at = time.monotonic()

    @app_commands.command(name="ping", description="Check the bot's latency.")
    async def ping(self, interaction: discord.Interaction) -> None:
        latency_ms = self.bot.latency * 1000
        await interaction.response.send_message(f"Pong! Latency: {latency_ms:.0f} ms")

    @app_commands.command(name="info", description="Show information about the bot.")
    async def info(self, interaction: discord.Interaction) -> None:
        uptime = time.monotonic() - self.started_at
        embed = discord.Embed(
            title="Bot Information",
            color=self.bot.user.color if self.bot.user else discord.Color.blurple(),
        )
        if self.bot.user:
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.add_field(name="Servers", value=str(len(self.bot.guilds)))
        embed.add_field(name="Latency", value=f"{self.bot.latency * 1000:.0f} ms")
        embed.add_field(name="Uptime", value=_format_duration(uptime))
        embed.add_field(name="Version", value=package_version("exon-bot"))
        embed.add_field(name="discord.py", value=discord.__version__)
        embed.add_field(name="Python", value=platform.python_version())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="userinfo", description="Show information about a member."
    )
    @app_commands.guild_only()
    @app_commands.describe(member="Member to inspect; defaults to you")
    async def userinfo(
        self,
        interaction: discord.Interaction,
        member: discord.Member | None = None,
    ) -> None:
        member = member or cast(discord.Member, interaction.user)
        embed = discord.Embed(
            title=str(member),
            color=member.color if member.color.value else discord.Color.blurple(),
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="ID", value=str(member.id))
        embed.add_field(name="Nickname", value=member.nick or "None")
        embed.add_field(name="Bot", value="Yes" if member.bot else "No")
        embed.add_field(
            name="Created", value=discord.utils.format_dt(member.created_at, "f")
        )
        if member.joined_at:
            embed.add_field(
                name="Joined",
                value=discord.utils.format_dt(member.joined_at, "f"),
            )
        roles = [
            role.mention for role in reversed(member.roles) if not role.is_default()
        ]
        if len(roles) > 10:
            visible = ", ".join(roles[:10])
            roles_display = f"{visible} (+{len(roles) - 10} more)"
        else:
            roles_display = ", ".join(roles) or "None"
        embed.add_field(name=f"Roles ({len(roles)})", value=roles_display, inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="serverinfo", description="Show information about this server."
    )
    @app_commands.guild_only()
    async def serverinfo(self, interaction: discord.Interaction) -> None:
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message(
                "This command is only available inside a server.",
                ephemeral=True,
            )
            return
        text_channels = sum(
            1 for c in guild.channels if isinstance(c, discord.TextChannel)
        )
        voice_channels = sum(
            1 for c in guild.channels if isinstance(c, discord.VoiceChannel)
        )
        categories = sum(
            1 for c in guild.channels if isinstance(c, discord.CategoryChannel)
        )
        embed = discord.Embed(title=guild.name, color=discord.Color.blurple())
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="ID", value=str(guild.id))
        embed.add_field(name="Owner", value=f"<@{guild.owner_id}>")
        embed.add_field(name="Members", value=str(guild.member_count))
        embed.add_field(
            name="Created", value=discord.utils.format_dt(guild.created_at, "f")
        )
        embed.add_field(
            name="Boosts",
            value=f"Level {guild.premium_tier} ({guild.premium_subscription_count} boosts)",
        )
        embed.add_field(
            name="Channels",
            value=f"{text_channels} text / {voice_channels} voice / {categories} categories",
        )
        embed.add_field(name="Roles", value=str(len(guild.roles) - 1))
        embed.add_field(name="Emojis", value=str(len(guild.emojis)))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="avatar", description="Show a member's avatar in full size."
    )
    @app_commands.guild_only()
    @app_commands.describe(member="Member to inspect; defaults to you")
    async def avatar(
        self,
        interaction: discord.Interaction,
        member: discord.Member | None = None,
    ) -> None:
        member = member or cast(discord.Member, interaction.user)
        embed = discord.Embed(
            title=f"{member.display_name}'s avatar",
            color=member.color if member.color.value else discord.Color.blurple(),
        )
        embed.set_image(url=member.display_avatar.replace(size=4096).url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="help", description="List the available commands.")
    async def help_command(self, interaction: discord.Interaction) -> None:
        groups: dict[str, list[str]] = {}
        for command in self.bot.tree.get_commands():
            cmd = cast(app_commands.Command, command)
            label = getattr(cmd.binding, "qualified_name", None) or "Other"
            groups.setdefault(label, []).append(f"`/{cmd.name}` — {cmd.description}")
        embed = discord.Embed(
            title="Help",
            description="List of available commands.",
            color=discord.Color.blurple(),
        )
        for label, lines in groups.items():
            embed.add_field(name=label, value="\n".join(lines), inline=False)
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """Entry point required by load_extension to register the cog."""
    await bot.add_cog(General(bot))
