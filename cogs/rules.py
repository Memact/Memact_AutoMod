from __future__ import annotations

from typing import Optional

import nextcord
from nextcord.ext import commands

from bot import MemactAutoModBot
from config import COMMAND_GUILD_IDS
from utils.checks import require_admin
from utils.ui import build_embed, send_interaction


class RulesCog(commands.Cog):
    def __init__(self, bot: MemactAutoModBot) -> None:
        self.bot = bot

    def _build_rules_embed(self, guild: nextcord.Guild) -> nextcord.Embed:
        rules = self.bot.db.list_rules(guild.id)
        lines = []
        for index, rule in enumerate([item for item in rules if item["enabled"]], start=1):
            lines.append(f"**{index}. {rule['title']}**\n{rule['description']}\nPenalty weight: `{rule['points']}`")
        description = "\n\n".join(lines) if lines else "No rules configured yet."
        return build_embed(f"{guild.name} Server Rules", description, footer="Please read and follow these rules.")

    @nextcord.slash_command(description="Manage and post server rules", guild_ids=COMMAND_GUILD_IDS)
    async def rules(self, interaction: nextcord.Interaction) -> None:
        pass

    @rules.subcommand(description="Show the current rules list")
    async def list(self, interaction: nextcord.Interaction) -> None:
        admin = await require_admin(interaction)
        if admin is None:
            return
        await send_interaction(interaction, embed=self._build_rules_embed(interaction.guild))

    @rules.subcommand(description="Add a rule")
    async def add(
        self,
        interaction: nextcord.Interaction,
        title: str,
        description: str,
        points: int = nextcord.SlashOption(required=False, default=1, min_value=1, max_value=10),
    ) -> None:
        admin = await require_admin(interaction)
        if admin is None:
            return
        rule_id = self.bot.db.add_rule(interaction.guild.id, title, description, points)
        await send_interaction(interaction, embed=build_embed("Rule Added", f"Added rule #{rule_id}: **{title}**"))

    @rules.subcommand(description="Edit an existing rule")
    async def edit(
        self,
        interaction: nextcord.Interaction,
        rule_id: int,
        title: Optional[str] = nextcord.SlashOption(required=False),
        description: Optional[str] = nextcord.SlashOption(required=False),
        points: Optional[int] = nextcord.SlashOption(required=False, min_value=1, max_value=10),
        enabled: Optional[bool] = nextcord.SlashOption(required=False),
    ) -> None:
        admin = await require_admin(interaction)
        if admin is None:
            return
        updated = self.bot.db.update_rule(interaction.guild.id, rule_id, title=title, description=description, points=points, enabled=enabled)
        if not updated:
            await send_interaction(interaction, content="No rule was updated. Check the rule ID or provide at least one field.", ephemeral=True)
            return
        await send_interaction(interaction, embed=build_embed("Rule Updated", f"Updated rule #{rule_id}."))

    @rules.subcommand(description="Delete a rule")
    async def remove(
        self,
        interaction: nextcord.Interaction,
        rule_id: int,
    ) -> None:
        admin = await require_admin(interaction)
        if admin is None:
            return
        removed = self.bot.db.delete_rule(interaction.guild.id, rule_id)
        if not removed:
            await send_interaction(interaction, content="Rule not found.", ephemeral=True)
            return
        await send_interaction(interaction, embed=build_embed("Rule Removed", f"Deleted rule #{rule_id}."))

    @rules.subcommand(description="Reset rules to the built-in server rule defaults")
    async def reset(self, interaction: nextcord.Interaction) -> None:
        admin = await require_admin(interaction)
        if admin is None:
            return
        self.bot.db.reset_rules(interaction.guild.id)
        await send_interaction(interaction, embed=build_embed("Rules Reset", "Restored the default server rules."))

    @rules.subcommand(description="Post the rules embed")
    async def post(
        self,
        interaction: nextcord.Interaction,
        channel: Optional[nextcord.TextChannel] = nextcord.SlashOption(required=False),
    ) -> None:
        admin = await require_admin(interaction)
        if admin is None:
            return
        config = self.bot.db.get_guild_config(interaction.guild.id)
        target_channel = channel
        if target_channel is None and config["rules_channel_id"]:
            target_channel = interaction.guild.get_channel(config["rules_channel_id"])
        if target_channel is None:
            await send_interaction(interaction, content="Set a rules channel with `/config rules_channel` or pass a channel here.", ephemeral=True)
            return
        embed = self._build_rules_embed(interaction.guild)
        await target_channel.send(embed=embed)
        await send_interaction(interaction, embed=build_embed("Rules Posted", f"Posted the rules in {target_channel.mention}."))


def setup(bot: MemactAutoModBot) -> None:
    bot.add_cog(RulesCog(bot))
