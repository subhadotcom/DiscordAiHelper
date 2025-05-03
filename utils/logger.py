"""
Logging configuration for the Discord bot.
"""
import logging
import os
from logging.handlers import RotatingFileHandler
import sys

from utils.config import Config

def setup_logger():
    """
    Configure the logger for the application.
    
    Creates a logger that writes to both console and file.
    """
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Get log level from config
    log_level_str = Config.get_log_level()
    log_level = getattr(logging, log_level_str, logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            RotatingFileHandler(
                "logs/discord_bot.log", 
                maxBytes=10485760,  # 10MB
                backupCount=5
            )
        ]
    )
    
    # Set specific levels for external libraries
    logging.getLogger("discord").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    logger = logging.getLogger("discord_bot")
    logger.info(f"Logger initialized with level: {log_level_str}")
    
    return logger
