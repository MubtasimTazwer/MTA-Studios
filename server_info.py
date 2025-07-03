"""
Server Information Cog - Provides server statistics and information
"""

import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from helper import create_embed  # ✅ Updated import
from config import BotConfig

class ServerInfoCog(commands.Cog):
    """Cog containing server information commands."""
    
    def __init__(self, bot):
        self.bot = bot
        self.config = BotConfig()
    
    @app_commands.command(name="serverinfo", description="Get detailed information about the server")
    async def serverinfo(self, interaction: discord.Interaction):
        """Display comprehensive server information."""
        guild = interaction.guild
        
        # Calculate member statistics
        total_members = guild.member_count
        online_members = sum(1 for member in guild.members if member.status != discord.Status.offline)
        bot_count = sum(1 for member in guild.members if member.bot)
        human_count = total_members - bot_count
        
        # Get server features
        features = []
        if guild.features:
            feature_mapping = {
                'COMMUNITY': 'Community Server',
                'PARTNERED': 'Discord Partner',
                'VERIFIED': 'Verified',
                'VANITY_URL': 'Vanity URL',
                'BANNER': 'Server Banner',
                'ANIMATED_ICON': 'Animated Icon',
                'NEWS': 'News Channels',
                'DISCOVERABLE': 'Server Discovery'
            }
            features = [feature_mapping.get(feature, feature.replace('_', ' ').title()) for feature in guild.features[:5]]
        
        embed = create_embed(
            title=f"📊 {guild.name} Server Information",
            color=self.config.COLORS["info"]
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        # Basic information
        embed.add_field(
            name="📝 Basic Info",
            value=f"**Owner:** {guild.owner.mention if guild.owner else 'Unknown'}\n"
                  f"**Created:** <t:{int(guild.created_at.timestamp())}:F>\n"
                  f"**Server ID:** `{guild.id}`\n"
                  f"**Verification Level:** {guild.verification_level.name.title()}",
            inline=True
        )
        
        # Member statistics
        embed.add_field(
            name="👥 Members",
            value=f"**Total:** {total_members:,}\n"
                  f"**Online:** {online_members:,}\n"
                  f"**Humans:** {human_count:,}\n"
                  f"**Bots:** {bot_count:,}",
            inline=True
        )
        
        # Channel information
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        
        embed.add_field(
            name="📁 Channels",
            value=f"**Text:** {text_channels}\n"
                  f"**Voice:** {voice_channels}\n"
                  f"**Categories:** {categories}\n"
                  f"**Total:** {text_channels + voice_channels}",
            inline=True
        )
        
        # Roles information
        embed.add_field(
            name="🎭 Roles",
            value=f"**Total:** {len(guild.roles)}\n"
                  f"**Highest:** {guild.roles[-1].name}\n"
                  f"**Default:** @everyone",
            inline=True
        )
        
        # Boost information
        embed.add_field(
            name="💎 Nitro Boosts",
            value=f"**Level:** {guild.premium_tier}\n"
                  f"**Boosts:** {guild.premium_subscription_count or 0}\n"
                  f"**Boosters:** {len(guild.premium_subscribers)}",
            inline=True
        )
        
        # Security settings
        embed.add_field(
            name="🔒 Security",
            value=f"**2FA Requirement:** {'Yes' if guild.mfa_level else 'No'}\n"
                  f"**Content Filter:** {guild.explicit_content_filter.name.replace('_', ' ').title()}\n"
                  f"**Default Notifications:** {guild.default_notifications.name.title()}",
            inline=True
        )
        
        # Server features
        if features:
            embed.add_field(
                name="✨ Features",
                value="\n".join([f"• {feature}" for feature in features]),
                inline=False
            )
        
        # Server banner
        if guild.banner:
            embed.set_image(url=guild.banner.url)
        
        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="membercount", description="Get the current member count")
    async def membercount(self, interaction: discord.Interaction):
        """Display current member count with breakdown."""
        guild = interaction.guild
        
        total_members = guild.member_count
        online_members = sum(1 for member in guild.members if member.status != discord.Status.offline)
        bot_count = sum(1 for member in guild.members if member.bot)
        human_count = total_members - bot_count
        
        # Count by status
        status_counts = {
            'online': 0,
            'idle': 0,
            'dnd': 0,
            'offline': 0
        }
        
        for member in guild.members:
            if not member.bot:
                status_counts[str(member.status)] += 1
        
        embed = create_embed(
            title=f"👥 {guild.name} Member Count",
            description=f"**Total Members:** {total_members:,}",
            color=self.config.COLORS["info"]
        )
        
        embed.add_field(
            name="📊 Breakdown",
            value=f"**Humans:** {human_count:,}\n"
                  f"**Bots:** {bot_count:,}\n"
                  f"**Online:** {online_members:,}",
            inline=True
        )
        
        embed.add_field(
            name="🔴 Status Distribution",
            value=f"🟢 Online: {status_counts['online']}\n"
                  f"🟡 Idle: {status_counts['idle']}\n"
                  f"🔴 DND: {status_counts['dnd']}\n"
                  f"⚫ Offline: {status_counts['offline']}",
            inline=True
        )
        
        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="channels", description="List all channels in the server")
    async def channels(self, interaction: discord.Interaction):
        """Display all channels organized by category."""
        guild = interaction.guild
        
        embed = create_embed(
            title=f"📁 {guild.name} Channels",
            color=self.config.COLORS["info"]
        )
        
        # Get channels by category
        categories_data = {}
        
        # Channels without category
        uncategorized_text = [ch for ch in guild.text_channels if not ch.category]
        uncategorized_voice = [ch for ch in guild.voice_channels if not ch.category]
        
        if uncategorized_text or uncategorized_voice:
            categories_data["No Category"] = {
                'text': uncategorized_text,
                'voice': uncategorized_voice
            }
        
        # Channels with categories
        for category in guild.categories:
            categories_data[category.name] = {
                'text': category.text_channels,
                'voice': category.voice_channels
            }
        
        # Build embed fields
        for category_name, channels in categories_data.items():
            text_channels = channels['text']
            voice_channels = channels['voice']
            
            channel_list = []
            
            if text_channels:
                channel_list.extend([f"💬 {ch.name}" for ch in text_channels[:5]])
                if len(text_channels) > 5:
                    channel_list.append(f"... and {len(text_channels) - 5} more text channels")
            
            if voice_channels:
                channel_list.extend([f"🔊 {ch.name}" for ch in voice_channels[:3]])
                if len(voice_channels) > 3:
                    channel_list.append(f"... and {len(voice_channels) - 3} more voice channels")
            
            if channel_list:
                embed.add_field(
                    name=f"📂 {category_name}",
                    value="\n".join(channel_list) or "No channels",
                    inline=False
                )
        
        # Summary
        total_text = len(guild.text_channels)
        total_voice = len(guild.voice_channels)
        total_categories = len(guild.categories)
        
        embed.add_field(
            name="📊 Summary",
            value=f"**Text Channels:** {total_text}\n"
                  f"**Voice Channels:** {total_voice}\n"
                  f"**Categories:** {total_categories}",
            inline=True
        )
        
        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="roles", description="List all roles in the server")
    async def roles(self, interaction: discord.Interaction):
        """Display all roles in the server."""
        guild = interaction.guild
        
        # Sort roles by position (highest first)
        roles = sorted(guild.roles[1:], key=lambda r: r.position, reverse=True)  # Exclude @everyone
        
        embed = create_embed(
            title=f"🎭 {guild}
