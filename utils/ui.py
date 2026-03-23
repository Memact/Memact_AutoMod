from __future__ import annotations

from typing import Iterable

import nextcord

from config import EMBED_COLOR


def build_embed(
    title: str,
    description: str = "",
    *,
    color: int = EMBED_COLOR,
    footer: str | None = None,
    fields: Iterable[tuple[str, str, bool]] | None = None,
) -> nextcord.Embed:
    embed = nextcord.Embed(title=title, description=description, color=color)
    if footer:
        embed.set_footer(text=footer)
    if fields:
        for name, value, inline in fields:
            embed.add_field(name=name, value=value or "-", inline=inline)
    return embed


async def send_interaction(
    interaction: nextcord.Interaction,
    *,
    content: str | None = None,
    embed: nextcord.Embed | None = None,
    ephemeral: bool = True,
    view: nextcord.ui.View | None = None,
) -> None:
    kwargs = {"ephemeral": ephemeral}
    if content is not None:
        kwargs["content"] = content
    if embed is not None:
        kwargs["embed"] = embed
    if view is not None:
        kwargs["view"] = view
    if interaction.response.is_done():
        await interaction.followup.send(**kwargs)
    else:
        await interaction.response.send_message(**kwargs)


async def safe_dm(user: nextcord.abc.User, *, content: str | None = None, embed: nextcord.Embed | None = None) -> bool:
    try:
        await user.send(content=content, embed=embed)
    except (nextcord.Forbidden, nextcord.HTTPException):
        return False
    return True
