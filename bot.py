"""
Discord Bot Core Implementation
"""

import discord
from discord.ext import commands
import logging
import asyncio
from config import BotConfig

logger = logging.getLogger(__name__)

class DiscordBot(commands.Bot):
    """Main Discord Bot class with all core functionality."""
    
    def __init__(self):
        # Set up bot intents
        intents = discord.Intents.default()
        # Enable message content if needed for non-slash commands (optional)
        intents.message_content = True

        super().__init__(
            command_prefix=BotConfig.PREFIX,
            intents=intents,
            help_command=None,  # Custom help command
            case_insensitive=True,
            strip_after_prefix=True
        )
        
        self.config = BotConfig()
        
    async def setup_hook(self):
        """Called when the bot is starting up."""
        logger.info("Setting up bot...")

        # ✅ Load cogs from the same directory
        cogs_to_load = [
            'moderation',
            'server_info',
            'user_info',
            'utilities',
            'roles'
        ]
        
        for cog in cogs_to_load:
            try:
                await self.load_extension(cog)
                logger.info(f"Loaded cog: {cog}")
            except Exception as e:
                logger.error(f"Failed to load cog {cog}: {e}")
        
        # 🔄 Sync slash commands
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} slash commands")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
    
    async def on_ready(self):
        """Called when the bot has successfully connected to Discord."""
        logger.info(f"Bot is ready! Logged in as {self.user}")
        logger.info(f"Bot ID: {self.user.id}")
        logger.info(f"Connected to {len(self.guilds)} guilds")
        
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(self.guilds)} servers | /help"
        )
        await self.change_presence(activity=activity, status=discord.Status.online)
    
    async def on_guild_join(self, guild):
        """Called when the bot joins a new guild."""
        logger.info(f"Joined guild: {guild.name} (ID: {guild.id})")
        await self.update_status()
    
    async def on_guild_remove(self, guild):
        """Called when the bot is removed from a guild."""
        logger.info(f"Left guild: {guild.name} (ID: {guild.id})")
        await self.update_status()

    async def update_status(self):
        """Update bot presence based on server count."""
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(self.guilds)} servers | /help"
        )
        await self.change_presence(activity=activity, status=discord.Status.online)
    
    async def on_command_error(self, ctx, error):
        """Global error handler for prefix commands."""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore unknown commands
        
        logger.error(f"Command error in {ctx.command}: {error}")
        
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏰ Command is on cooldown. Try again in {error.retry_after:.1f} seconds.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: `{error.param.name}`")
        else:
            await ctx.send("❌ An error occurred while executing this command.")
    
    async def on_app_command_error(self, interaction: discord.Interaction, error):
        """Global error handler for slash commands."""
        logger.error(f"Slash command error: {error}")
        
        send_func = (
            interaction.followup.send if interaction.response.is_done()
            else interaction.response.send_message
        )

        if isinstance(error, discord.app_commands.MissingPermissions):
            await send_func("❌ You don't have permission to use this command.", ephemeral=True)
        elif isinstance(error, discord.app_commands.CommandOnCooldown):
            await send_func(f"⏰ Cooldown active. Try again in {error.retry_after:.1f} seconds.", ephemeral=True)
        else:
            await send_func("❌ An error occurred while executing this command.", ephemeral=True)
