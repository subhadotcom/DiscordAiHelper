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

# In Replit, we're using gunicorn for Flask, 
# so we need to modify our approach to run the bot as a separate process
import multiprocessing
import time

def run_flask():
    """Run the Flask web interface"""
    app.run(host="0.0.0.0", port=5000, debug=True)

def run_bot():
    """Run the Discord bot"""
    try:
        discord_token = Config.get_discord_token()
        if not discord_token:
            logger.error("Discord token not found in environment variables")
            return
        
        # Log that we're attempting to connect
        logger.info(f"Attempting to connect to Discord with token: {discord_token[:5]}...")
        
        # Start the bot with the token (async)
        bot.run(discord_token)
    except Exception as e:
        logger.error(f"Error starting the bot: {e}")
        print(f"Discord Bot Error: {e}")

def start_bot_process():
    """Start the bot in a separate process"""
    # When running with gunicorn, we'll start the bot as a separate process
    bot_process = multiprocessing.Process(target=run_bot)
    bot_process.daemon = True
    bot_process.start()
    logger.info(f"Started Discord bot process with PID: {bot_process.pid}")
    return bot_process

# If we're running this file directly
if __name__ == "__main__":
    try:
        # Start the Discord bot in a separate process
        bot_process = start_bot_process()
        
        # Run the Flask app in the main thread (for development)
        run_flask()
    except KeyboardInterrupt:
        logger.info("Application shutdown by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
else:
    # When imported by gunicorn, start the bot process
    # This ensures the bot runs when the app is started with gunicorn
    try:
        logger.info("Starting Discord bot process from gunicorn import")
        bot_process = start_bot_process()
    except Exception as e:
        logger.error(f"Failed to start Discord bot from gunicorn: {e}")
        print(f"Discord Bot Start Error: {e}")
