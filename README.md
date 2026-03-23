# Memact AutoMod

Memact AutoMod is a `nextcord` moderation bot for a private Discord server.

## Features

- moderation slash commands for bans, kicks, timeouts, warnings, purge, locks, slowmode, nicknames, and role tools
- SQLite-backed case history, warning points, temp-ban scheduling, and server config
- automod for spam, duplicate messages, invite links, blocked words, caps, and mention flooding
- rules management and rules embed posting
- generic embed creation and reusable embed templates
- member report and appeal flows

## Setup

1. Create a Discord bot in the Discord developer portal.
2. Enable the `SERVER MEMBERS INTENT` and `MESSAGE CONTENT INTENT`.
3. Copy `.env.example` to `.env` and fill in `MEMACT_TOKEN`.
4. Install dependencies with `pip install -r requirements.txt`.
5. Run the bot with `python main.py`.
