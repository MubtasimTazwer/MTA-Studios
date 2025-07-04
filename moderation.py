"""
Moderation Cog - Handles all moderation-related commands
"""

import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from datetime import datetime, timedelta
def has_moderation_permissions(user: discord.Member, guild: discord.Guild) -> bool:
    """Check if the user has kick, ban, or manage_roles permissions."""
    perms = user.guild_permissions
    return perms.kick_members or perms.ban_members or perms.manage_roles

def create_embed(title=None, description=None, color=discord.Color.red()):
    embed = discord.Embed(
        title=title or "Notice",
        description=description or "",
        color=color
    )
    return embed
from config import BotConfig

class ModerationCog(commands.Cog):
    """Cog containing moderation commands."""
    
    def __init__(self, bot):
        self.bot = bot
        self.config = BotConfig()
    
    @app_commands.command(name="kick", description="Kick a member from the server")
    @app_commands.describe(
        member="The member to kick",
        reason="Reason for the kick"
    )
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        """Kick a member from the server."""
        if not has_moderation_permissions(interaction.user, interaction.guild):
            await interaction.response.send_message("â You don't have permission to kick members.", ephemeral=True)
            return
        
        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message("â You cannot kick someone with a higher or equal role.", ephemeral=True)
            return
        
        if member.id == interaction.user.id:
            await interaction.response.send_message("â You cannot kick yourself.", ephemeral=True)
            return
        
        try:
            # Send DM to the member before kicking
            try:
                dm_embed = create_embed(
                    title="You have been kicked",
                    description=f"You were kicked from **{interaction.guild.name}**",
                    color=discord.Color.orange()
                )
                dm_embed.add_field(name="Reason", value=reason, inline=False)
                dm_embed.add_field(name="Kicked by", value=interaction.user.mention, inline=True)
                await member.send(embed=dm_embed)
            except:
                pass  # Member might have DMs disabled
            
            await member.kick(reason=f"{reason} - Kicked by {interaction.user}")
            
            embed = create_embed(
                title="Member Kicked",
                description=f"**{member}** has been kicked from the server",
                color=self.config.COLORS["success"]
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Kicked by", value=interaction.user.mention, inline=True)
            
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            await interaction.response.send_message("â I don't have permission to kick that member.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"â An error occurred: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="ban", description="Ban a member from the server")
    @app_commands.describe(
        member="The member to ban",
        reason="Reason for the ban",
        delete_messages="Days of messages to delete (0-7)"
    )
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided", delete_messages: int = 0):
        """Ban a member from the server."""
        if not has_moderation_permissions(interaction.user, interaction.guild):
            await interaction.response.send_message("â You don't have permission to ban members.", ephemeral=True)
            return
        
        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message("â You cannot ban someone with a higher or equal role.", ephemeral=True)
            return
        
        if member.id == interaction.user.id:
            await interaction.response.send_message("â You cannot ban yourself.", ephemeral=True)
            return
        
        if delete_messages < 0 or delete_messages > 7:
            await interaction.response.send_message("â Delete messages days must be between 0 and 7.", ephemeral=True)
            return
        
        try:
            # Send DM to the member before banning
            try:
                dm_embed = create_embed(
                    title="You have been banned",
                    description=f"You were banned from **{interaction.guild.name}**",
                    color=self.config.COLORS["error"]
                )
                dm_embed.add_field(name="Reason", value=reason, inline=False)
                dm_embed.add_field(name="Banned by", value=interaction.user.mention, inline=True)
                await member.send(embed=dm_embed)
            except:
                pass  # Member might have DMs disabled
            
            await member.ban(reason=f"{reason} - Banned by {interaction.user}", delete_message_days=delete_messages)
            
            embed = create_embed(
                title="Member Banned",
                description=f"**{member}** has been banned from the server",
                color=self.config.COLORS["error"]
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Banned by", value=interaction.user.mention, inline=True)
            embed.add_field(name="Messages deleted", value=f"{delete_messages} days", inline=True)
            
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            await interaction.response.send_message("â I don't have permission to ban that member.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"â An error occurred: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="unban", description="Unban a user from the server")
    @app_commands.describe(
        user_id="The ID of the user to unban",
        reason="Reason for the unban"
    )
    async def unban(self, interaction: discord.Interaction, user_id: str, reason: str = "No reason provided"):
        """Unban a user from the server."""
        if not has_moderation_permissions(interaction.user, interaction.guild):
            await interaction.response.send_message("â You don't have permission to unban members.", ephemeral=True)
            return
        
        try:
            user_id = int(user_id)
        except ValueError:
            await interaction.response.send_message("â Invalid user ID provided.", ephemeral=True)
            return
        
        try:
            user = await self.bot.fetch_user(user_id)
            await interaction.guild.unban(user, reason=f"{reason} - Unbanned by {interaction.user}")
            
            embed = create_embed(
                title="Member Unbanned",
                description=f"**{user}** has been unbanned from the server",
                color=self.config.COLORS["success"]
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Unbanned by", value=interaction.user.mention, inline=True)
            
            await interaction.response.send_message(embed=embed)
            
        except discord.NotFound:
            await interaction.response.send_message("â User not found or not banned.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("â I don't have permission to unban users.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"â An error occurred: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="clear", description="Clear a specified number of messages")
    @app_commands.describe(
        amount="Number of messages to delete (1-100)",
        user="Only delete messages from this user"
    )
    async def clear(self, interaction: discord.Interaction, amount: int, user: discord.Member = None):
        """Clear messages from the channel."""
        if not has_moderation_permissions(interaction.user, interaction.guild):
            await interaction.response.send_message("â You don't have permission to manage messages.", ephemeral=True)
            return
        
        if amount < 1 or amount > self.config.MAX_PURGE_AMOUNT:
            await interaction.response.send_message(f"â Amount must be between 1 and {self.config.MAX_PURGE_AMOUNT}.", ephemeral=True)
            return
        
        try:
            def check(message):
                if user:
                    return message.author == user
                return True
            
            # Defer the response since this might take a while
            await interaction.response.defer()
            
            deleted = await interaction.channel.purge(limit=amount, check=check)
            
            embed = create_embed(
                title="Messages Cleared",
                description=f"Successfully deleted {len(deleted)} messages",
                color=self.config.COLORS["success"]
            )
            
            if user:
                embed.add_field(name="Target User", value=user.mention, inline=True)
            
            embed.add_field(name="Cleared by", value=interaction.user.mention, inline=True)
            
            # Send a temporary message that will delete itself
            message = await interaction.followup.send(embed=embed)
            await asyncio.sleep(5)
            await message.delete()
            
        except discord.Forbidden:
            await interaction.followup.send("â I don't have permission to delete messages.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"â An error occurred: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="timeout", description="Timeout a member")
    @app_commands.describe(
        member="The member to timeout",
        duration="Duration in minutes",
        reason="Reason for the timeout"
    )
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, duration: int, reason: str = "No reason provided"):
        """Timeout a member."""
        if not has_moderation_permissions(interaction.user, interaction.guild):
            await interaction.response.send_message("â You don't have permission to timeout members.", ephemeral=True)
            return
        
        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message("â You cannot timeout someone with a higher or equal role.", ephemeral=True)
            return
        
        if member.id == interaction.user.id:
            await interaction.response.send_message("â You cannot timeout yourself.", ephemeral=True)
            return
        
        if duration < 1 or duration > 40320:  # Discord's max timeout is 28 days
            await interaction.response.send_message("â Duration must be between 1 minute and 28 days (40320 minutes).", ephemeral=True)
            return
        
        try:
            timeout_until = datetime.utcnow() + timedelta(minutes=duration)
            await member.timeout(timeout_until, reason=f"{reason} - Timed out by {interaction.user}")
            
            embed = create_embed(
    title="Member Timed Out",
    description=f"**{member}** has been timed out",
    color=discord.Color.orange()
)
            embed.add_field(name="Duration", value=f"{duration} minutes", inline=True)
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Timed out by", value=interaction.user.mention, inline=True)
            
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            await interaction.response.send_message("â I don't have permission to timeout that member.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"â An error occurred: {str(e)}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ModerationCog(bot)
