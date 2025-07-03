"""
Helper functions for the Discord bot.

This module provides shared utility functions used across different cogs
for things like creating embeds, formatting time, and cleaning text.
"""

import discord
from datetime import datetime
from config import BotConfig

config = BotConfig()

def create_embed(title: str = None, description: str = None, color: int = None) -> discord.Embed:
    """Create a Discord embed with consistent styling."""
    if color is None:
        color = config.COLORS["default"]
    return discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.utcnow()
    )

def format_duration(seconds: int) -> str:
    """Convert seconds into a human-readable duration string."""
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    parts = []
    if days: parts.append(f"{days}d")
    if hours: parts.append(f"{hours}h")
    if minutes: parts.append(f"{minutes}m")
    if seconds or not parts: parts.append(f"{seconds}s")
    return " ".join(parts)

def format_permissions(permissions: discord.Permissions) -> list:
    """Convert a Discord Permissions object to a readable list of permission names."""
    permission_list = []

    perm_mapping = {
        'administrator': 'Administrator',
        'manage_guild': 'Manage Server',
        'manage_roles': 'Manage Roles',
        'manage_channels': 'Manage Channels',
        'kick_members': 'Kick Members',
        'ban_members': 'Ban Members',
        'manage_messages': 'Manage Messages',
        'manage_webhooks': 'Manage Webhooks',
        'manage_nicknames': 'Manage Nicknames',
        'mute_members': 'Mute Members',
        'deafen_members': 'Deafen Members',
        'move_members': 'Move Members',
        'use_voice_activation': 'Use Voice Activity',
        'priority_speaker': 'Priority Speaker',
        'stream': 'Video',
        'view_audit_log': 'View Audit Log',
        'view_guild_insights': 'View Server Insights',
        'change_nickname': 'Change Nickname',
        'create_instant_invite': 'Create Invite',
        'send_messages': 'Send Messages',
        'send_tts_messages': 'Send TTS Messages',
        'embed_links': 'Embed Links',
        'attach_files': 'Attach Files',
        'read_message_history': 'Read Message History',
        'mention_everyone': 'Mention Everyone',
        'use_external_emojis': 'Use External Emojis',
        'add_reactions': 'Add Reactions',
        'connect': 'Connect to Voice',
        'speak': 'Speak in Voice'
    }

    for perm, value in permissions:
        if value and perm in perm_mapping:
            permission_list.append(perm_mapping[perm])
    return permission_list

def truncate_text(text: str, max_length: int = 1024) -> str:
    """Truncate text to fit within Discord embed field character limits."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

def get_member_status_emoji(status: discord.Status) -> str:
    """Get emoji representation of a member's online status."""
    status_emojis = {
        discord.Status.online: "🟢",
        discord.Status.idle: "🟡",
        discord.Status.dnd: "🔴",
        discord.Status.offline: "⚫"
    }
    return status_emojis.get(status, "❓")

def humanize_timedelta(td) -> str:
    """Convert a timedelta object to a human-readable string."""
    days = td.days
    hours, remainder = divmod(td.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    parts = []
    if days: parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours: parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes: parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")

    if not parts:
        return "Just now"
    elif len(parts) == 1:
        return parts[0]
    elif len(parts) == 2:
        return f"{parts[0]} and {parts[1]}"
    else:
        return f"{parts[0]}, {parts[1]} and {parts[2]}"

def clean_code_block(content: str) -> str:
    """Remove Discord code block formatting from a string."""
    if content.startswith('```') and content.endswith('```'):
        lines = content.split('\n')
        return '\n'.join(lines[1:-1]) if len(lines) > 2 else content[3:-3]
    if content.startswith('`') and content.endswith('`'):
        return content[1:-1]
    return content

def is_valid_hex_color(color: str) -> bool:
    """Check if a string is a valid 6-digit hex color (with or without #)."""
    color = color.lstrip('#')
    if len(color) != 6:
        return False
    try:
        int(color, 16)
        return True
    except ValueError:
        return False
