from __future__ import annotations

import nextcord
from nextcord.ext import commands

from bot import MemactAutoModBot
from config import BLUESKY_RELAY_CHANNEL_ID, COMMAND_GUILD_IDS
from utils.checks import require_admin
from utils.ui import build_embed, send_interaction


class ConfigurationCog(commands.Cog):
    def __init__(self, bot: MemactAutoModBot) -> None:
        self.bot = bot

    @nextcord.slash_command(
        description="Configure Memact AutoMod",
        guild_ids=COMMAND_GUILD_IDS,
        default_member_permissions=nextcord.Permissions(manage_guild=True),
    )
    async def config(self, interaction: nextcord.Interaction) -> None:
        pass

    @config.subcommand(description="Show the current server configuration")
    async def view(self, interaction: nextcord.Interaction) -> None:
        admin = await require_admin(interaction)
        if admin is None:
            return
        config = self.bot.db.get_guild_config(interaction.guild.id)
        bluesky_feed = self.bot.db.get_bluesky_feed(interaction.guild.id)

        def format_role_list(role_ids: list[int]) -> str:
            mentions = []
            for role_id in role_ids:
                role = interaction.guild.get_role(role_id)
                mentions.append(role.mention if role is not None else f"`{role_id}`")
            return ", ".join(mentions) if mentions else "None"

        def format_channel(channel_id: int | None) -> str:
            if not channel_id:
                return "Not set"
            channel = interaction.guild.get_channel(channel_id)
            return channel.mention if channel is not None else f"`{channel_id}`"

        def format_bluesky_feed() -> str:
            if bluesky_feed is None:
                return "Not configured"
            status = "enabled" if bluesky_feed["enabled"] else "disabled"
            channel = format_channel(BLUESKY_RELAY_CHANNEL_ID)
            return f"`@{bluesky_feed['handle']}` -> {channel} ({status})"

        embed = build_embed(
            "Memact AutoMod Configuration",
            "Current server settings.",
            fields=[
                ("Mod Roles", format_role_list(config["mod_role_ids"]), False),
                ("Admin Roles", format_role_list(config["admin_role_ids"]), False),
                ("Log Channel", format_channel(config["log_channel_id"]), True),
                ("Rules Channel", format_channel(config["rules_channel_id"]), True),
                ("Report Channel", format_channel(config["report_channel_id"]), True),
                ("Appeal Channel", format_channel(config["appeal_channel_id"]), True),
                ("Bluesky Relay", format_bluesky_feed(), False),
                (
                    "Security",
                    f"Anti-nuke {'on' if config['antinuke_enabled'] else 'off'} / "
                    f"Audit logs {'on' if config['audit_server_logs_enabled'] else 'off'}",
                    False,
                ),
                ("Raid Mode", "On" if config["raid_mode"] else "Off", True),
                ("Min Account Age", f"{config['min_account_age_hours']} hours", True),
                ("Warn Thresholds", f"Timeout {config['warn_timeout_threshold']} / Kick {config['warn_kick_threshold']} / Ban {config['warn_ban_threshold']}", False),
            ],
        )
        await send_interaction(interaction, embed=embed)

    @config.subcommand(description="Set the moderation log channel")
    async def log_channel(self, interaction: nextcord.Interaction, channel: nextcord.TextChannel) -> None:
        admin = await require_admin(interaction)
        if admin is None:
            return
        self.bot.db.set_config_value(interaction.guild.id, "log_channel_id", channel.id)
        await send_interaction(interaction, embed=build_embed("Log Channel Updated", f"Set the log channel to {channel.mention}."))

    @config.subcommand(description="Set the rules channel")
    async def rules_channel(self, interaction: nextcord.Interaction, channel: nextcord.TextChannel) -> None:
        admin = await require_admin(interaction)
        if admin is None:
            return
        self.bot.db.set_config_value(interaction.guild.id, "rules_channel_id", channel.id)
        await send_interaction(interaction, embed=build_embed("Rules Channel Updated", f"Set the rules channel to {channel.mention}."))

    @config.subcommand(description="Set the report channel")
    async def report_channel(self, interaction: nextcord.Interaction, channel: nextcord.TextChannel) -> None:
        admin = await require_admin(interaction)
        if admin is None:
            return
        self.bot.db.set_config_value(interaction.guild.id, "report_channel_id", channel.id)
        await send_interaction(interaction, embed=build_embed("Report Channel Updated", f"Set the report channel to {channel.mention}."))

    @config.subcommand(description="Set the appeal channel")
    async def appeal_channel(self, interaction: nextcord.Interaction, channel: nextcord.TextChannel) -> None:
        admin = await require_admin(interaction)
        if admin is None:
            return
        self.bot.db.set_config_value(interaction.guild.id, "appeal_channel_id", channel.id)
        await send_interaction(interaction, embed=build_embed("Appeal Channel Updated", f"Set the appeal channel to {channel.mention}."))

    @config.subcommand(description="Register a moderator role")
    async def add_mod_role(self, interaction: nextcord.Interaction, role: nextcord.Role) -> None:
        admin = await require_admin(interaction)
        if admin is None:
            return
        self.bot.db.add_role_id(interaction.guild.id, "mod_role_ids", role.id)
        await send_interaction(interaction, embed=build_embed("Moderator Role Added", f"{role.mention} can now use mod commands."))

    @config.subcommand(description="Remove a moderator role")
    async def remove_mod_role(self, interaction: nextcord.Interaction, role: nextcord.Role) -> None:
        admin = await require_admin(interaction)
        if admin is None:
            return
        self.bot.db.remove_role_id(interaction.guild.id, "mod_role_ids", role.id)
        await send_interaction(interaction, embed=build_embed("Moderator Role Removed", f"{role.mention} no longer has Memact AutoMod access."))

    @config.subcommand(description="Register an admin role")
    async def add_admin_role(self, interaction: nextcord.Interaction, role: nextcord.Role) -> None:
        admin = await require_admin(interaction)
        if admin is None:
            return
        self.bot.db.add_role_id(interaction.guild.id, "admin_role_ids", role.id)
        await send_interaction(interaction, embed=build_embed("Admin Role Added", f"{role.mention} can now manage bot config."))

    @config.subcommand(description="Remove an admin role")
    async def remove_admin_role(self, interaction: nextcord.Interaction, role: nextcord.Role) -> None:
        admin = await require_admin(interaction)
        if admin is None:
            return
        self.bot.db.remove_role_id(interaction.guild.id, "admin_role_ids", role.id)
        await send_interaction(interaction, embed=build_embed("Admin Role Removed", f"{role.mention} no longer has Memact AutoMod admin access."))

    @config.subcommand(description="Toggle raid mode")
    async def raidmode(self, interaction: nextcord.Interaction, enabled: bool) -> None:
        admin = await require_admin(interaction)
        if admin is None:
            return
        self.bot.db.set_config_value(interaction.guild.id, "raid_mode", int(enabled))
        await send_interaction(interaction, embed=build_embed("Raid Mode Updated", f"Raid mode is now {'enabled' if enabled else 'disabled'}."))

    @config.subcommand(description="Require a minimum account age before users can stay")
    async def min_account_age(self, interaction: nextcord.Interaction, hours: int = nextcord.SlashOption(min_value=0, max_value=8760)) -> None:
        admin = await require_admin(interaction)
        if admin is None:
            return
        self.bot.db.set_config_value(interaction.guild.id, "min_account_age_hours", hours)
        await send_interaction(interaction, embed=build_embed("Minimum Account Age Updated", f"Minimum account age is now `{hours}` hours."))

    @config.subcommand(description="Set warning escalation thresholds")
    async def thresholds(
        self,
        interaction: nextcord.Interaction,
        timeout_points: int = nextcord.SlashOption(min_value=1, max_value=100),
        kick_points: int = nextcord.SlashOption(min_value=1, max_value=100),
        ban_points: int = nextcord.SlashOption(min_value=1, max_value=100),
        timeout_minutes: int = nextcord.SlashOption(required=False, default=1440, min_value=1, max_value=40320),
    ) -> None:
        admin = await require_admin(interaction)
        if admin is None:
            return
        if not (timeout_points <= kick_points <= ban_points):
            await send_interaction(interaction, content="Thresholds must be ordered like timeout <= kick <= ban.", ephemeral=True)
            return
        self.bot.db.set_config_value(interaction.guild.id, "warn_timeout_threshold", timeout_points)
        self.bot.db.set_config_value(interaction.guild.id, "warn_kick_threshold", kick_points)
        self.bot.db.set_config_value(interaction.guild.id, "warn_ban_threshold", ban_points)
        self.bot.db.set_config_value(interaction.guild.id, "warn_timeout_minutes", timeout_minutes)
        await send_interaction(
            interaction,
            embed=build_embed(
                "Thresholds Updated",
                f"Timeout at `{timeout_points}` points, kick at `{kick_points}`, ban at `{ban_points}`, timeout duration `{timeout_minutes}` minutes.",
            ),
        )


def setup(bot: MemactAutoModBot) -> None:
    bot.add_cog(ConfigurationCog(bot))
