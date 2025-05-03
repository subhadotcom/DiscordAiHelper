"""
Configuration management for the Discord bot.
"""
import os
import logging
from typing import Optional

logger = logging.getLogger("discord_bot")

class Config:
    """Configuration utility class for the Discord bot."""
    
    # Default values
    _DEFAULT_PREFIX = "!"
    _DEFAULT_BOT_NAME = "AI Assistant"
    _DEFAULT_CLIENT_ID = None
    
    @staticmethod
    def get_discord_token() -> Optional[str]:
        """
        Get the Discord bot token from environment variables.
        
        Returns:
            str: The Discord bot token or None if not found
        """
        token = os.environ.get("DISCORD_TOKEN")
        if not token:
            logger.warning("DISCORD_TOKEN not found in environment variables")
        return token
    
    @staticmethod
    def get_openai_api_key() -> Optional[str]:
        """
        Get the OpenAI API key from environment variables.
        
        Returns:
            str: The OpenAI API key or None if not found
        """
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY not found in environment variables")
        return api_key
    
    @staticmethod
    def get_command_prefix() -> str:
        """
        Get the command prefix for the bot.
        
        Returns:
            str: The command prefix (defaults to '!')
        """
        return os.environ.get("BOT_PREFIX", Config._DEFAULT_PREFIX)
    
    @staticmethod
    def get_bot_name() -> str:
        """
        Get the bot's name for personalization.
        
        Returns:
            str: The bot's name (defaults to 'AI Assistant')
        """
        return os.environ.get("BOT_NAME", Config._DEFAULT_BOT_NAME)
    
    @staticmethod
    def get_database_url() -> Optional[str]:
        """
        Get the database URL from environment variables.
        
        Returns:
            str: The database URL or None if not found
        """
        return os.environ.get("DATABASE_URL")
    
    @staticmethod
    def get_log_level() -> str:
        """
        Get the logging level from environment variables.
        
        Returns:
            str: The logging level (defaults to 'INFO')
        """
        return os.environ.get("LOG_LEVEL", "INFO").upper()
    
    @staticmethod
    def is_production() -> bool:
        """
        Check if the environment is production.
        
        Returns:
            bool: True if in production mode, False otherwise
        """
        return os.environ.get("ENVIRONMENT", "development").lower() == "production"
        
    @staticmethod
    def get_client_id() -> Optional[str]:
        """
        Get the Discord client ID from environment variables.
        
        Returns:
            str: The Discord client ID or None if not found
        """
        client_id = os.environ.get("DISCORD_CLIENT_ID")
        if not client_id:
            logger.warning("DISCORD_CLIENT_ID not found in environment variables")
        return client_id
