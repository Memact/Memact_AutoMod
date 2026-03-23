from __future__ import annotations

from typing import Iterable

import nextcord

from utils.ui import send_interaction


def _has_role(member: nextcord.Member, role_ids: Iterable[int]) -> bool:
    allowed = set(role_ids)
    return any(role.id in allowed for role in member.roles)


def is_moderator_member(member: nextcord.Member, config: dict) -> bool:
    permissions = member.guild_permissions
    return (
        permissions.administrator
        or permissions.manage_guild
        or permissions.kick_members
        or permissions.ban_members
        or permissions.manage_messages
        or _has_role(member, config["admin_role_ids"])
        or _has_role(member, config["mod_role_ids"])
    )


def is_admin_member(member: nextcord.Member, config: dict) -> bool:
    permissions = member.guild_permissions
    return permissions.administrator or _has_role(member, config["admin_role_ids"])


async def require_guild(interaction: nextcord.Interaction) -> nextcord.Guild | None:
    if interaction.guild is not None:
        if not interaction.client.is_allowed_guild_id(interaction.guild.id):
            await send_interaction(
                interaction,
                content=f"Memact AutoMod only works in server `{interaction.client.settings.dev_guild_id}`.",
                ephemeral=True,
            )
            return None
        return interaction.guild
    await send_interaction(interaction, content="This command only works inside a server.", ephemeral=True)
    return None


async def require_moderator(interaction: nextcord.Interaction) -> nextcord.Member | None:
    guild = await require_guild(interaction)
    if guild is None:
        return None
    member = interaction.user if isinstance(interaction.user, nextcord.Member) else guild.get_member(interaction.user.id)
    if member is None:
        await send_interaction(interaction, content="I couldn't resolve your member profile in this guild.", ephemeral=True)
        return None
    config = interaction.client.db.get_guild_config(guild.id)
    if is_moderator_member(member, config):
        return member
    await send_interaction(interaction, content="You need moderator permissions to use this command.", ephemeral=True)
    return None


async def require_admin(interaction: nextcord.Interaction) -> nextcord.Member | None:
    guild = await require_guild(interaction)
    if guild is None:
        return None
    member = interaction.user if isinstance(interaction.user, nextcord.Member) else guild.get_member(interaction.user.id)
    if member is None:
        await send_interaction(interaction, content="I couldn't resolve your member profile in this guild.", ephemeral=True)
        return None
    config = interaction.client.db.get_guild_config(guild.id)
    if is_admin_member(member, config):
        return member
    await send_interaction(interaction, content="You need admin permissions to use this command.", ephemeral=True)
    return None
