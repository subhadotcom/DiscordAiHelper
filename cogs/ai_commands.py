"""
AI-related commands for the Discord bot using Google AI Studio.
"""
import discord
from discord.ext import commands
import logging
import asyncio
import re
from datetime import datetime

from utils.google_ai_helper import generate_ai_response, generate_image
from utils.config import Config
from models import Conversation, Server
from app import db

logger = logging.getLogger("discord_bot")

class AICommands(commands.Cog):
    """Cog containing AI-related commands."""
    
    def __init__(self, bot):
        self.bot = bot
        self.typing_tasks = {}
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """
        Listen for messages that mention the bot and respond with AI.
        """
        # Don't respond to bot messages
        if message.author.bot:
            return
        
        # Check if the message mentions the bot or starts with @bot
        is_mention = self.bot.user in message.mentions
        is_reply = message.reference and message.reference.resolved and message.reference.resolved.author.id == self.bot.user.id
        
        if is_mention or is_reply:
            # Extract the actual message content without the mention
            content = re.sub(f'<@!?{self.bot.user.id}>', '', message.content).strip()
            
            if content:  # Only process if there's actual content
                await self._process_ai_response(message, content)
    
    @commands.command(name="ai")
    async def ai_command(self, ctx, *, message=None):
        """
        Get a response from the AI.
        
        Usage: !ai <your message>
        """
        if not message:
            await ctx.send("Please provide a message for me to respond to!")
            return
        
        await self._process_ai_response(ctx.message, message)
    
    @commands.command(name="image")
    @commands.cooldown(rate=1, per=30, type=commands.BucketType.user)
    async def generate_image_command(self, ctx, *, prompt=None):
        """
        Generate an image using AI.
        
        Usage: !image <prompt>
        """
        if not prompt:
            await ctx.send("Please provide a prompt for the image generation!")
            return
        
        try:
            # Send a typing indicator
            async with ctx.typing():
                await ctx.send("Generating image... This may take a moment.")
                
                # Generate the image
                result = generate_image(prompt)
                
                if result and "url" in result:
                    # Create an embed for the image
                    embed = discord.Embed(
                        title="AI Generated Image",
                        description=f"Prompt: {prompt}",
                        color=discord.Color.purple()
                    )
                    embed.set_image(url=result["url"])
                    embed.set_footer(text=f"Requested by {ctx.author.name}")
                    
                    await ctx.send(embed=embed)
                elif result and "error" in result:
                    # Display the error message
                    embed = discord.Embed(
                        title="Image Generation",
                        description=result["error"],
                        color=discord.Color.gold()
                    )
                    embed.set_footer(text="Using Google AI Studio")
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("Failed to generate the image. Please try again with a different prompt.")
        
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            await ctx.send(f"An error occurred while generating the image: {str(e)}")
            # Reset the cooldown if there was an error
            self.generate_image_command.reset_cooldown(ctx)
    
    async def _process_ai_response(self, message, content):
        """
        Process an AI response to a message.
        
        Args:
            message: The Discord message
            content: The content to process
        """
        # Start typing indicator
        typing_task = asyncio.create_task(self._continue_typing(message.channel))
        self.typing_tasks[message.channel.id] = typing_task
        
        try:
            # Generate AI response
            response = await asyncio.to_thread(generate_ai_response, content, message.author.name)
            
            # Save conversation to database
            try:
                server = await self._get_or_create_server(message.guild)
                
                conversation = Conversation(
                    server_id=server.id,
                    channel_id=str(message.channel.id),
                    user_id=str(message.author.id),
                    username=message.author.name,
                    message=content,
                    response=response,
                    timestamp=datetime.utcnow()
                )
                
                db.session.add(conversation)
                db.session.commit()
            except Exception as db_error:
                logger.error(f"Database error: {db_error}")
            
            # Cancel typing
            if message.channel.id in self.typing_tasks:
                self.typing_tasks[message.channel.id].cancel()
                del self.typing_tasks[message.channel.id]
            
            # Split response if it's too long
            if len(response) > 2000:
                chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
                for chunk in chunks:
                    await message.channel.send(chunk)
            else:
                await message.channel.send(response)
        
        except Exception as e:
            logger.error(f"Error processing AI response: {e}")
            
            # Cancel typing
            if message.channel.id in self.typing_tasks:
                self.typing_tasks[message.channel.id].cancel()
                del self.typing_tasks[message.channel.id]
            
            await message.channel.send(f"Sorry, I encountered an error: {str(e)}")
    
    async def _continue_typing(self, channel):
        """
        Continues to show typing indicator while processing.
        
        Args:
            channel: The Discord channel
        """
        try:
            async with channel.typing():
                while True:
                    await asyncio.sleep(10)
        except asyncio.CancelledError:
            # Task was cancelled, which is expected
            pass
        except Exception as e:
            logger.error(f"Error in typing indicator: {e}")
    
    async def _get_or_create_server(self, guild):
        """
        Get or create a server record in the database.
        
        Args:
            guild: The Discord guild (server)
            
        Returns:
            Server: The server record
        """
        if not guild:
            # This might be a DM, so we'll create a special server for DMs
            server = Server.query.filter_by(discord_server_id="DM").first()
            if not server:
                server = Server(
                    discord_server_id="DM",
                    name="Direct Messages",
                    user_id=1,  # Assuming admin user ID is 1
                    prefix=Config.get_command_prefix(),
                    ai_enabled=True
                )
                db.session.add(server)
                db.session.commit()
            return server
        
        # Look up the server in the database
        server = Server.query.filter_by(discord_server_id=str(guild.id)).first()
        
        # If the server doesn't exist, create it
        if not server:
            server = Server(
                discord_server_id=str(guild.id),
                name=guild.name,
                user_id=1,  # Assuming admin user ID is 1
                prefix=Config.get_command_prefix(),
                ai_enabled=True
            )
            db.session.add(server)
            db.session.commit()
        
        return server

async def setup(bot):
    """Add the cog to the bot."""
    await bot.add_cog(AICommands(bot))
