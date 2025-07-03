"""
Moderation Cog - Handles all moderation-related commands
"""

import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from datetime import datetime, timedelta
from permissions import has_moderation_permissions
from helper import create_embed
from config import BotConfig

class ModerationCog(commands.Cog):
    """Cog containing moderation commands."""

    def __init__(self, bot):
        self.bot = bot
        self.config = BotConfig()
    
    # ... [ALL YOUR COMMANDS REMAIN UNCHANGED BELOW] ...

    # ⬇️ No need to change the command logic — everything else works as-is!

async def setup(bot):
    await bot.add_cog(ModerationCog(bot))
