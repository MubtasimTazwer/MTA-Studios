"""
Bot Configuration Settings
"""

import os

class BotConfig:
    """Configuration class for the Discord bot."""
    
    # Bot settings
    PREFIX = "!"
    
    # API Keys and tokens (from environment variables)
    # Note: Weather command now uses direct links instead of API
    
    # Bot permissions
    MODERATOR_PERMISSIONS = [
        "kick_members",
        "ban_members",
        "manage_messages",
        "manage_roles",
        "manage_channels"
    ]
    
    # Command cooldowns (in seconds)
    COOLDOWNS = {
        "general": 3,
        "moderation": 5,
        "utility": 2,
        "info": 1
    }
    
    # Embed colors
    COLORS = {
        "success": 0x00ff00,
        "error": 0xff0000,
        "warning": 0xffff00,
        "info": 0x0099ff,
        "default": 0x7289da
    }
    
    # Maximum values
    MAX_PURGE_AMOUNT = 100
    MAX_POLL_OPTIONS = 10
    MAX_REMINDER_TIME = 86400  # 24 hours in seconds
    

