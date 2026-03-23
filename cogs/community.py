from __future__ import annotations

import nextcord
from nextcord.ext import commands

from bot import MemactAutoModBot
from config import COMMAND_GUILD_IDS
from utils.ui import build_embed, send_interaction


class CommunityCog(commands.Cog):
    def __init__(self, bot: MemactAutoModBot) -> None:
        self.bot = bot

    @nextcord.slash_command(description="Report a member to the moderators", guild_ids=COMMAND_GUILD_IDS)
    async def report(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member,
        reason: str,
        evidence_url: str = nextcord.SlashOption(required=False, default=""),
    ) -> None:
        if interaction.guild is None:
            await send_interaction(interaction, content="This command only works inside a server.", ephemeral=True)
            return
        config = self.bot.db.get_guild_config(interaction.guild.id)
        channel_id = config["report_channel_id"]
        if not channel_id:
            await send_interaction(interaction, content="Reports are not configured yet. Ask an admin to set `/config report_channel`.", ephemeral=True)
            return
        channel = interaction.guild.get_channel(channel_id)
        if not isinstance(channel, nextcord.TextChannel):
            await send_interaction(interaction, content="The configured report channel could not be found.", ephemeral=True)
            return
        report_id = self.bot.db.add_report(
            interaction.guild.id,
            "report",
            interaction.user.id,
            member.id,
            reason,
            evidence_url=evidence_url or None,
        )
        embed = build_embed(
            "New Member Report",
            reason,
            fields=[
                ("Report ID", str(report_id), True),
                ("Reporter", interaction.user.mention, True),
                ("Target", member.mention, True),
                ("Evidence", evidence_url or "None", False),
            ],
            footer="Memact AutoMod report queue",
        )
        await channel.send(embed=embed)
        await send_interaction(interaction, embed=build_embed("Report Submitted", f"Your report for {member.mention} has been sent to the moderators."))

    @nextcord.slash_command(description="Appeal a moderation case", guild_ids=COMMAND_GUILD_IDS)
    async def appeal(
        self,
        interaction: nextcord.Interaction,
        case_id: int,
        reason: str,
    ) -> None:
        if interaction.guild is None:
            await send_interaction(interaction, content="This command only works inside a server.", ephemeral=True)
            return
        config = self.bot.db.get_guild_config(interaction.guild.id)
        channel_id = config["appeal_channel_id"]
        if not channel_id:
            await send_interaction(interaction, content="Appeals are not configured yet. Ask an admin to set `/config appeal_channel`.", ephemeral=True)
            return
        case = self.bot.db.get_case(interaction.guild.id, case_id)
        if case is None:
            await send_interaction(interaction, content="That case ID was not found.", ephemeral=True)
            return
        channel = interaction.guild.get_channel(channel_id)
        if not isinstance(channel, nextcord.TextChannel):
            await send_interaction(interaction, content="The configured appeal channel could not be found.", ephemeral=True)
            return
        appeal_id = self.bot.db.add_report(
            interaction.guild.id,
            "appeal",
            interaction.user.id,
            case["user_id"],
            reason,
            case_id=case_id,
        )
        embed = build_embed(
            "New Case Appeal",
            reason,
            fields=[
                ("Appeal ID", str(appeal_id), True),
                ("Appealing User", interaction.user.mention, True),
                ("Case ID", str(case_id), True),
                ("Original Action", case["action"], True),
                ("Original Reason", case["reason"], False),
            ],
            footer="Memact AutoMod appeal queue",
        )
        await channel.send(embed=embed)
        await send_interaction(interaction, embed=build_embed("Appeal Submitted", f"Your appeal for case #{case_id} has been sent to the moderators."))


def setup(bot: MemactAutoModBot) -> None:
    bot.add_cog(CommunityCog(bot))
