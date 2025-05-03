"""
General commands for the Discord bot.
"""
import discord
from discord.ext import commands
import logging
import platform
import psutil
import asyncio
from datetime import datetime

from utils.config import Config

logger = logging.getLogger("discord_bot")

class GeneralCommands(commands.Cog):
    """Cog containing general bot commands."""
    
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.utcnow()
    
    @commands.command(name="commands")
    async def help_command(self, ctx, command=None):
        """
        Display help information for commands.
        
        Usage: !commands [command]
        """
        prefix = Config.get_command_prefix()
        
        if command:
            # Get help for a specific command
            cmd = self.bot.get_command(command)
            if cmd:
                embed = discord.Embed(
                    title=f"Help: {prefix}{cmd.name}",
                    description=cmd.help or "No description available.",
                    color=discord.Color.blue()
                )
                
                if cmd.aliases:
                    embed.add_field(name="Aliases", value=", ".join(cmd.aliases), inline=False)
                
                usage = f"{prefix}{cmd.name}"
                if cmd.signature:
                    usage += f" {cmd.signature}"
                embed.add_field(name="Usage", value=f"`{usage}`", inline=False)
                
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"Command '{command}' not found.")
        else:
            # Show general help
            embed = discord.Embed(
                title="Bot Help",
                description=f"Here are the available commands. Use `{prefix}commands [command]` for more info on a command.",
                color=discord.Color.blue()
            )
            
            # Group commands by cog
            cog_commands = {}
            for cmd in self.bot.commands:
                if cmd.hidden:
                    continue
                
                cog_name = cmd.cog.qualified_name if cmd.cog else "No Category"
                if cog_name not in cog_commands:
                    cog_commands[cog_name] = []
                
                cog_commands[cog_name].append(cmd)
            
            # Add fields for each cog
            for cog_name, cmds in cog_commands.items():
                command_list = ", ".join(f"`{prefix}{cmd.name}`" for cmd in cmds)
                embed.add_field(name=cog_name, value=command_list, inline=False)
            
            embed.set_footer(text=f"Bot Version: 1.0.0 | Use {prefix}commands [command] for more details")
            
            await ctx.send(embed=embed)
    
    @commands.command(name="info")
    async def info_command(self, ctx):
        """
        Show information about the bot.
        
        Usage: !info
        """
        # Calculate uptime
        uptime = datetime.utcnow() - self.start_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"
        
        # Get system info
        process = psutil.Process()
        memory_usage = process.memory_info().rss / 1024 / 1024  # Convert to MB
        
        embed = discord.Embed(
            title=f"{self.bot.user.name} Info",
            description="An AI-powered Discord bot using OpenAI",
            color=discord.Color.green()
        )
        
        embed.add_field(name="Bot Version", value="1.0.0", inline=True)
        embed.add_field(name="Discord.py Version", value=discord.__version__, inline=True)
        embed.add_field(name="Python Version", value=platform.python_version(), inline=True)
        
        embed.add_field(name="Uptime", value=uptime_str, inline=True)
        embed.add_field(name="Memory Usage", value=f"{memory_usage:.2f} MB", inline=True)
        embed.add_field(name="Servers", value=str(len(self.bot.guilds)), inline=True)
        
        embed.add_field(name="Developer", value="Bot Developer", inline=True)
        embed.add_field(name="Commands", value=str(len(self.bot.commands)), inline=True)
        embed.add_field(name="Prefix", value=Config.get_command_prefix(), inline=True)
        
        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        embed.set_footer(text="Thanks for using the bot!")
        
        await ctx.send(embed=embed)
    
    @commands.command(name="invite")
    async def invite_command(self, ctx):
        """
        Get an invite link for the bot.
        
        Usage: !invite
        """
        permissions = discord.Permissions(
            send_messages=True,
            embed_links=True,
            attach_files=True,
            read_messages=True,
            read_message_history=True,
            add_reactions=True
        )
        
        # Use the configured client ID if available, otherwise fallback to the bot user ID
        client_id = Config.get_client_id() or str(self.bot.user.id)
        invite_url = discord.utils.oauth_url(
            client_id=client_id,
            permissions=permissions
        )
        
        embed = discord.Embed(
            title="Invite Link",
            description="Click the link below to add me to your server!",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Bot Invite", value=f"[Click Here]({invite_url})", inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="uptime")
    async def uptime_command(self, ctx):
        """
        Show the bot's uptime.
        
        Usage: !uptime
        """
        uptime = datetime.utcnow() - self.start_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        await ctx.send(f"🕒 Uptime: **{days}** days, **{hours}** hours, **{minutes}** minutes, **{seconds}** seconds")
    
    @commands.command(name="servers")
    @commands.is_owner()
    async def servers_command(self, ctx):
        """
        List all servers the bot is in (owner only).
        
        Usage: !servers
        """
        server_list = [f"**{guild.name}** (ID: {guild.id}, Members: {guild.member_count})" for guild in self.bot.guilds]
        
        # Split into chunks if there are many servers
        chunks = [server_list[i:i+10] for i in range(0, len(server_list), 10)]
        
        for i, chunk in enumerate(chunks):
            embed = discord.Embed(
                title=f"Server List ({i+1}/{len(chunks)})",
                description="\n".join(chunk),
                color=discord.Color.blue()
            )
            embed.set_footer(text=f"Total Servers: {len(self.bot.guilds)}")
            
            await ctx.send(embed=embed)

async def setup(bot):
    """Add the cog to the bot."""
    await bot.add_cog(GeneralCommands(bot))
