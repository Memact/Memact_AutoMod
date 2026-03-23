from __future__ import annotations

import nextcord
from nextcord.ext import commands

from bot import MemactAutoModBot
from config import COMMAND_GUILD_IDS
from utils.checks import require_admin
from utils.ui import build_embed, send_interaction


class ConfigurationCog(commands.Cog):
    def __init__(self, bot: MemactAutoModBot) -> None:
        self.bot = bot

    @nextcord.slash_command(description="Configure Memact AutoMod", guild_ids=COMMAND_GUILD_IDS)
    async def config(self, interaction: nextcord.Interaction) -> None:
        pass

    @config.subcommand(description="Show the current server configuration")
    async def view(self, interaction: nextcord.Interaction) -> None:
        admin = await require_admin(interaction)
        if admin is None:
            return
        config = self.bot.db.get_guild_config(interaction.guild.id)
        embed = build_embed(
            "Memact AutoMod Configuration",
            "Current server settings.",
            fields=[
                ("Mod Roles", ", ".join(f"`{role_id}`" for role_id in config["mod_role_ids"]) or "None", False),
                ("Admin Roles", ", ".join(f"`{role_id}`" for role_id in config["admin_role_ids"]) or "None", False),
                ("Log Channel", f"`{config['log_channel_id']}`" if config["log_channel_id"] else "Not set", True),
                ("Rules Channel", f"`{config['rules_channel_id']}`" if config["rules_channel_id"] else "Not set", True),
                ("Report Channel", f"`{config['report_channel_id']}`" if config["report_channel_id"] else "Not set", True),
                ("Appeal Channel", f"`{config['appeal_channel_id']}`" if config["appeal_channel_id"] else "Not set", True),
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
