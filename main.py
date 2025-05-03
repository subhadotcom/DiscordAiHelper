"""
Entry point for the Discord bot with OpenAI integration.
This file imports the Flask app and runs the Discord bot.
"""
import asyncio
import logging
import threading
import os
import sys

from app import app
from bot import bot
from utils.config import Config
from utils.logger import setup_logger

# Set up logging
setup_logger()
logger = logging.getLogger("discord_bot")

def run_flask():
    """Run the Flask web interface"""
    app.run(host="0.0.0.0", port=5000, debug=True)

def run_bot():
    """Run the Discord bot"""
    try:
        discord_token = Config.get_discord_token()
        if not discord_token:
            logger.error("Discord token not found in environment variables")
            sys.exit(1)
        
        # Start the bot with the token
        bot.run(discord_token)
    except Exception as e:
        logger.error(f"Error starting the bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        # Start the Flask server in a separate thread
        flask_thread = threading.Thread(target=run_flask)
        flask_thread.daemon = True
        flask_thread.start()
        
        # Run the Discord bot in the main thread
        run_bot()
    except KeyboardInterrupt:
        logger.info("Application shutdown by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
