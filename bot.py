"""
Main Discord bot module using discord.py.
"""
import os
import asyncio
import logging
import discord
from discord.ext import commands

from utils.config import Config
from utils.logger import setup_logger

# Set up logging
setup_logger()
logger = logging.getLogger("discord_bot")

# Set up the Discord bot with intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Create the bot instance with a command prefix from config
bot = commands.Bot(command_prefix=Config.get_command_prefix(), intents=intents)

@bot.event
async def on_ready():
    """Event triggered when the bot is ready and connected to Discord."""
    logger.info(f"Bot connected as {bot.user.name} (ID: {bot.user.id})")
    logger.info(f"Connected to {len(bot.guilds)} servers")
    
    # Set the bot's activity
    activity = discord.Activity(type=discord.ActivityType.listening, name=f"{Config.get_command_prefix()}help")
    await bot.change_presence(activity=activity)
    
    # Load cogs
    await load_cogs()
    
    logger.info("Bot is fully ready!")

@bot.event
async def on_guild_join(guild):
    """Event triggered when the bot joins a new Discord server."""
    logger.info(f"Bot joined a new server: {guild.name} (ID: {guild.id})")
    
    # Try to send a welcome message to the system channel if available
    if guild.system_channel:
        embed = discord.Embed(
            title="Thanks for adding me!",
            description=f"Hello! I'm an AI-powered bot to help with your conversations. Use `{Config.get_command_prefix()}help` to see my commands.",
            color=discord.Color.blue()
        )
        embed.add_field(name="AI Conversations", value="I can have AI-powered conversations and respond to your questions.", inline=False)
        embed.add_field(name="Commands", value=f"Use `{Config.get_command_prefix()}ai <message>` to get an AI response.", inline=False)
        
        try:
            await guild.system_channel.send(embed=embed)
            logger.info(f"Sent welcome message to {guild.name}")
        except Exception as e:
            logger.error(f"Failed to send welcome message to {guild.name}: {e}")

@bot.event
async def on_guild_remove(guild):
    """Event triggered when the bot is removed from a Discord server."""
    logger.info(f"Bot removed from server: {guild.name} (ID: {guild.id})")

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors."""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"Command not found. Use `{Config.get_command_prefix()}help` to see available commands.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing required argument: {error.param.name}")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"Invalid argument provided: {str(error)}")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(f"You don't have the required permissions to use this command.")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send(f"I don't have the required permissions to execute this command.")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"This command is on cooldown. Try again in {error.retry_after:.2f} seconds.")
    else:
        logger.error(f"Command error: {str(error)}")
        await ctx.send(f"An error occurred: {str(error)}")

async def load_cogs():
    """Load command cogs."""
    try:
        # Load general commands cog
        await bot.load_extension("cogs.general_commands")
        logger.info("Loaded general commands cog")
        
        # Load AI commands cog
        await bot.load_extension("cogs.ai_commands")
        logger.info("Loaded AI commands cog")
    except Exception as e:
        logger.error(f"Error loading cogs: {e}")

# Add basic commands directly here
@bot.command(name="ping")
async def ping(ctx):
    """Simple command to check if the bot is responsive."""
    latency = round(bot.latency * 1000)
    await ctx.send(f"Pong! Latency: {latency}ms")

if __name__ == "__main__":
    # If running this file directly, start the bot
    discord_token = Config.get_discord_token()
    if not discord_token:
        logger.error("Discord token not found in environment variables")
        exit(1)
    
    bot.run(discord_token)
