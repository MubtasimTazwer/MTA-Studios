"""
Helper functions for the Discord bot
"""

import discord
from datetime import datetime
from config import BotConfig

config = BotConfig()

def create_embed(title: str = None, description: str = None, color: int = None) -> discord.Embed:
    """
    Create a Discord embed with consistent styling.
    
    Args:
        title: The embed title
        description: The embed description
        color: The embed color (defaults to bot's default color)
    
    Returns:
        discord.Embed: Configured embed object
    """
    if color is None:
        color = config.COLORS["default"]
    
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.utcnow()
    )
    
    return embed

def format_duration(seconds: int) -> str:
    """
    Format seconds into a human-readable duration.
    
    Args:
        seconds: Number of seconds
    
    Returns:
        str: Formatted duration string
    """
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if seconds or not parts:
        parts.append(f"{seconds}s")
    
    return " ".join(parts)

def format_permissions(permissions: discord.Permissions) -> list:
    """
    Format permissions into a readable list.
    
    Args:
        permissions: Discord permissions object
    
    Returns:
        list: List of permission names
    """
    permission_list = []
    
    # Important permissions mapping
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
    """
    Truncate text to fit within Discord's field limits.
    
    Args:
        text: The text to truncate
        max_length: Maximum length (default: 1024 for embed fields)
    
    Returns:
        str: Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - 3] + "..."

def get_member_status_emoji(status: discord.Status) -> str:
    """
    Get emoji representation of member status.
    
    Args:
        status: Discord status object
    
    Returns:
        str: Status emoji
    """
    status_emojis = {
        discord.Status.online: "🟢",
        discord.Status.idle: "🟡",
        discord.Status.dnd: "🔴",
        discord.Status.offline: "⚫"
    }
    
    return status_emojis.get(status, "❓")

def humanize_timedelta(td) -> str:
    """
    Convert timedelta to human-readable format.
    
    Args:
        td: timedelta object
    
    Returns:
        str: Human-readable time difference
    """
    days = td.days
    hours, remainder = divmod(td.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    
    parts = []
    if days:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    
    if not parts:
        return "Just now"
    elif len(parts) == 1:
        return parts[0]
    elif len(parts) == 2:
        return f"{parts[0]} and {parts[1]}"
    else:
        return f"{parts[0]}, {parts[1]} and {parts[2]}"

def clean_code_block(content: str) -> str:
    """
    Remove code block formatting from text.
    
    Args:
        content: Text that might contain code blocks
    
    Returns:
        str: Cleaned text
    """
    # Remove ```language and ``` markers
    if content.startswith('```') and content.endswith('```'):
        lines = content.split('\n')
        if len(lines) > 2:
            return '\n'.join(lines[1:-1])
        else:
            return content[3:-3]
    
    # Remove single backticks
    if content.startswith('`') and content.endswith('`'):
        return content[1:-1]
    
    return content

def is_valid_hex_color(color: str) -> bool:
    """
    Check if a string is a valid hex color.
    
    Args:
        color: Color string to validate
    
    Returns:
        bool: True if valid hex color
    """
    color = color.lstrip('#')
    if len(color) != 6:
        return False
    
    try:
        int(color, 16)
        return True
    except ValueError:
        return False
