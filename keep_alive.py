"""
Keep Alive Server for 24/7 Bot Uptime
Creates a simple web server that UptimeRobot can ping to keep the bot running
"""

from aiohttp import web
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def health_check(request):
    """Health check endpoint for UptimeRobot"""
    return web.json_response({
        "status": "online",
        "message": "Discord bot is running",
        "timestamp": str(asyncio.get_event_loop().time())
    })

async def root_handler(request):
    """Root endpoint"""
    return web.Response(text="Discord Bot - Online 24/7")

async def create_app():
    """Create the web application"""
    app = web.Application()
    
    # Add routes
    app.router.add_get('/', root_handler)
    app.router.add_get('/health', health_check)
    app.router.add_get('/ping', health_check)  # Alternative endpoint
    
    return app

async def start_server():
    """Start the keep-alive web server"""
    app = await create_app()
    
    # Start server on port 5000 (Replit's default)
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, '0.0.0.0', 5000)
    await site.start()
    
    logger.info("Keep-alive server started on http://0.0.0.0:5000")
    logger.info("Health check available at: /health and /ping")
    
    return runner

if __name__ == "__main__":
    asyncio.run(start_server())