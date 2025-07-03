"""
User Information Cog - Provides user profile and statistics
"""

import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from utils.helpers import create_embed
from config import BotConfig

class UserInfoCog(commands.Cog):
    """Cog containing user information commands."""
    
    def __init__(self, bot):
        self.bot = bot
        self.config = BotConfig()
    
    @app_commands.command(name="userinfo", description="Get detailed information about a user")
    @app_commands.describe(user="The user to get information about (defaults to yourself)")
    async def userinfo(self, interaction: discord.Interaction, user: discord.Member = None):
        """Display comprehensive user information."""
        if user is None:
            user = interaction.user
        
        embed = create_embed(
            title=f"👤 {user.display_name}",
            color=user.color if user.color != discord.Color.default() else self.config.COLORS["info"]
        )
        
        embed.set_thumbnail(url=user.display_avatar.url)
        
        # Basic user information
        embed.add_field(
            name="📝 Basic Info",
            value=f"**Username:** {user.name}\n"
                  f"**Discriminator:** #{user.discriminator}\n"
                  f"**ID:** `{user.id}`\n"
                  f"**Bot:** {'Yes' if user.bot else 'No'}",
            inline=True
        )
        
        # Account creation and join dates
        account_age = datetime.utcnow() - user.created_at
        server_join_age = datetime.utcnow() - user.joined_at if user.joined_at else None
        
        join_info = f"**Account Created:** <t:{int(user.created_at.timestamp())}:F>\n"
        join_info += f"**Account Age:** {account_age.days} days\n"
        
        if user.joined_at:
            join_info += f"**Joined Server:** <t:{int(user.joined_at.timestamp())}:F>\n"
            join_info += f"**Member For:** {server_join_age.days} days"
        else:
            join_info += "**Joined Server:** Unknown"
        
        embed.add_field(
            name="📅 Dates",
            value=join_info,
            inline=True
        )
        
        # Status and activity
        status_emoji = {
            discord.Status.online: "🟢 Online",
            discord.Status.idle: "🟡 Idle",
            discord.Status.dnd: "🔴 Do Not Disturb",
            discord.Status.offline: "⚫ Offline"
        }
        
        status_info = f"**Status:** {status_emoji.get(user.status, '❓ Unknown')}\n"
        
        # Get user activity
        if user.activities:
            activity = user.activities[0]
            if activity.type == discord.ActivityType.playing:
                status_info += f"**Playing:** {activity.name}\n"
            elif activity.type == discord.ActivityType.listening:
                if isinstance(activity, discord.Spotify):
                    status_info += f"**Listening to:** {activity.title} by {activity.artist}\n"
                else:
                    status_info += f"**Listening to:** {activity.name}\n"
            elif activity.type == discord.ActivityType.watching:
                status_info += f"**Watching:** {activity.name}\n"
            elif activity.type == discord.ActivityType.streaming:
                status_info += f"**Streaming:** {activity.name}\n"
            elif activity.type == discord.ActivityType.custom:
                if activity.name:
                    status_info += f"**Custom Status:** {activity.name}\n"
        
        # Device info
        if hasattr(user, 'desktop_status') and user.desktop_status != discord.Status.offline:
            status_info += "**Device:** 🖥️ Desktop\n"
        elif hasattr(user, 'mobile_status') and user.mobile_status != discord.Status.offline:
            status_info += "**Device:** 📱 Mobile\n"
        elif hasattr(user, 'web_status') and user.web_status != discord.Status.offline:
            status_info += "**Device:** 🌐 Web\n"
        
        embed.add_field(
            name="🔴 Status & Activity",
            value=status_info,
            inline=False
        )
        
        # Roles (if this is a guild member)
        if isinstance(user, discord.Member) and user.roles[1:]:  # Exclude @everyone
            roles = [role.mention for role in sorted(user.roles[1:], key=lambda r: r.position, reverse=True)]
            roles_text = ", ".join(roles[:10])  # Show first 10 roles
            if len(user.roles) > 11:  # 10 + @everyone
                roles_text += f" ... and {len(user.roles) - 11} more"
            
            embed.add_field(
                name=f"🎭 Roles ({len(user.roles) - 1})",
                value=roles_text,
                inline=False
            )
        
        # Server-specific information
        if isinstance(user, discord.Member):
            server_info = ""
            
            if user.nick:
                server_info += f"**Nickname:** {user.nick}\n"
            
            # Permissions
            key_perms = []
            if user.guild_permissions.administrator:
                key_perms.append("Administrator")
            elif user.guild_permissions.manage_guild:
                key_perms.append("Manage Server")
            elif user.guild_permissions.manage_roles:
                key_perms.append("Manage Roles")
            elif user.guild_permissions.manage_channels:
                key_perms.append("Manage Channels")
            elif user.guild_permissions.kick_members:
                key_perms.append("Kick Members")
            elif user.guild_permissions.ban_members:
                key_perms.append("Ban Members")
            
            if key_perms:
                server_info += f"**Key Permissions:** {', '.join(key_perms[:3])}\n"
            
            # Top role
            if user.top_role.name != "@everyone":
                server_info += f"**Top Role:** {user.top_role.mention}\n"
            
            # Boost info
            if user.premium_since:
                server_info += f"**Boosting Since:** <t:{int(user.premium_since.timestamp())}:F>\n"
            
            if server_info:
                embed.add_field(
                    name="🏠 Server Info",
                    value=server_info,
                    inline=True
                )
        
        # User badges/flags
        if user.public_flags:
            badges = []
            flag_mapping = {
                'staff': '👨‍💼 Discord Staff',
                'partner': '🤝 Discord Partner',
                'hypesquad': '🎉 HypeSquad Events',
                'bug_hunter': '🐛 Bug Hunter',
                'hypesquad_bravery': '🔥 HypeSquad Bravery',
                'hypesquad_brilliance': '💎 HypeSquad Brilliance',
                'hypesquad_balance': '⚖️ HypeSquad Balance',
                'early_supporter': '🌟 Early Supporter',
                'verified_bot_developer': '🔧 Verified Bot Developer',
                'discord_certified_moderator': '🛡️ Discord Certified Moderator',
                'active_developer': '🔨 Active Developer'
            }
            
            for flag_name, flag_value in user.public_flags:
                if flag_value and flag_name in flag_mapping:
                    badges.append(flag_mapping[flag_name])
            
            if badges:
                embed.add_field(
                    name="🏅 Badges",
                    value="\n".join(badges),
                    inline=True
                )
        
        # User avatar info
        if user.avatar:
            embed.add_field(
                name="🖼️ Avatar",
                value=f"[Download Avatar]({user.display_avatar.url})",
                inline=True
            )
        
        embed.set_footer(
            text=f"Requested by {interaction.user}",
            icon_url=interaction.user.display_avatar.url
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="avatar", description="Get a user's avatar")
    @app_commands.describe(user="The user to get the avatar of (defaults to yourself)")
    async def avatar(self, interaction: discord.Interaction, user: discord.Member = None):
        """Display a user's avatar."""
        if user is None:
            user = interaction.user
        
        embed = create_embed(
            title=f"🖼️ {user.display_name}'s Avatar",
            color=user.color if user.color != discord.Color.default() else self.config.COLORS["info"]
        )
        
        embed.set_image(url=user.display_avatar.url)
        
        # Avatar formats
        avatar_formats = []
        avatar_url = str(user.display_avatar.url)
        
        if user.display_avatar.is_animated():
            avatar_formats.append(f"[GIF]({avatar_url.replace('.webp', '.gif')})")
        
        avatar_formats.extend([
            f"[PNG]({avatar_url.replace('.webp', '.png')})",
            f"[JPG]({avatar_url.replace('.webp', '.jpg')})",
            f"[WEBP]({avatar_url})"
        ])
        
        embed.add_field(
            name="📥 Download Links",
            value=" • ".join(avatar_formats),
            inline=False
        )
        
        embed.set_footer(
            text=f"Requested by {interaction.user}",
            icon_url=interaction.user.display_avatar.url
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="joinposition", description="Check when you joined compared to others")
    @app_commands.describe(user="The user to check (defaults to yourself)")
    async def joinposition(self, interaction: discord.Interaction, user: discord.Member = None):
        """Show a user's join position in the server."""
        if user is None:
            user = interaction.user
        
        if not user.joined_at:
            await interaction.response.send_message("❌ Cannot determine join date for this user.", ephemeral=True)
            return
        
        # Sort members by join date
        sorted_members = sorted(
            [m for m in interaction.guild.members if m.joined_at],
            key=lambda m: m.joined_at
        )
        
        try:
            position = sorted_members.index(user) + 1
        except ValueError:
            await interaction.response.send_message("❌ Could not determine join position.", ephemeral=True)
            return
        
        embed = create_embed(
            title=f"📊 {user.display_name}'s Join Position",
            color=user.color if user.color != discord.Color.default() else self.config.COLORS["info"]
        )
        
        embed.set_thumbnail(url=user.display_avatar.url)
        
        embed.add_field(
            name="🎯 Position",
            value=f"**{position:,}** out of **{len(sorted_members):,}** members",
            inline=True
        )
        
        embed.add_field(
            name="📅 Join Date",
            value=f"<t:{int(user.joined_at.timestamp())}:F>",
            inline=True
        )
        
        # Show members who joined around the same time
        start_idx = max(0, position - 3)
        end_idx = min(len(sorted_members), position + 2)
        nearby_members = sorted_members[start_idx:end_idx]
        
        nearby_list = []
        for i, member in enumerate(nearby_members, start=start_idx + 1):
            prefix = "**➤**" if member == user else "  "
            nearby_list.append(f"{prefix} {i}. {member.display_name}")
        
        embed.add_field(
            name="👥 Nearby Members",
            value="\n".join(nearby_list),
            inline=False
        )
        
        embed.set_footer(
            text=f"Requested by {interaction.user}",
            icon_url=interaction.user.display_avatar.url
        )
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(UserInfoCog(bot))
