#!/usr/bin/env python3
"""
Discord Utility Bot - Main Entry Point
A comprehensive Discord bot with moderation, server management, and utility features.
Includes 24/7 uptime support with web server for UptimeRobot monitoring.
"""

import asyncio
import logging
import os
import sys
from bot import DiscordBot
from keep_alive import start_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Main function to start the Discord bot with keep-alive server."""
    try:
        # Get bot token from environment variables
        token = os.getenv("DISCORD_BOT_TOKEN")
        if not token:
            logger.error("DISCORD_BOT_TOKEN environment variable not found!")
            logger.error("Please set your Discord bot token in the environment variables.")
            return
        
        # Start the keep-alive web server for 24/7 uptime
        logger.info("Starting keep-alive server for 24/7 uptime...")
        await start_server()
        
        # Create and start the Discord bot
        bot = DiscordBot()
        
        logger.info("Starting Discord Utility Bot...")
        await bot.start(token)
        
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested by user")
    except Exception as e:
        logger.error(f"Fatal error occurred: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        sys.exit(1)
