"""
Role Management Cog - Handles role-related commands
"""

import discord
from discord.ext import commands
from discord import app_commands
from utils.permissions import has_role_management_permissions
from utils.helpers import create_embed
from config import BotConfig

class RolesCog(commands.Cog):
    """Cog containing role management commands."""
    
    def __init__(self, bot):
        self.bot = bot
        self.config = BotConfig()
    
    @app_commands.command(name="addrole", description="Add a role to a user")
    @app_commands.describe(
        user="The user to add the role to",
        role="The role to add"
    )
    async def add_role(self, interaction: discord.Interaction, user: discord.Member, role: discord.Role):
        """Add a role to a user."""
        if not has_role_management_permissions(interaction.user, interaction.guild):
            await interaction.response.send_message("❌ You don't have permission to manage roles.", ephemeral=True)
            return
        
        # Check if the role is higher than the user's top role
        if role >= interaction.user.top_role and interaction.user != interaction.guild.owner:
            await interaction.response.send_message("❌ You cannot assign a role higher than or equal to your highest role.", ephemeral=True)
            return
        
        # Check if the role is higher than the bot's top role
        if role >= interaction.guild.me.top_role:
            await interaction.response.send_message("❌ I cannot assign a role higher than or equal to my highest role.", ephemeral=True)
            return
        
        # Check if user already has the role
        if role in user.roles:
            await interaction.response.send_message(f"❌ {user.mention} already has the {role.mention} role.", ephemeral=True)
            return
        
        # Check for @everyone role
        if role.name == "@everyone":
            await interaction.response.send_message("❌ Cannot assign the @everyone role.", ephemeral=True)
            return
        
        try:
            await user.add_roles(role, reason=f"Role added by {interaction.user}")
            
            embed = create_embed(
                title="✅ Role Added",
                description=f"Successfully added {role.mention} to {user.mention}",
                color=self.config.COLORS["success"]
            )
            embed.add_field(name="Added by", value=interaction.user.mention, inline=True)
            embed.add_field(name="Role", value=role.mention, inline=True)
            
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to add that role.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ An error occurred: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="removerole", description="Remove a role from a user")
    @app_commands.describe(
        user="The user to remove the role from",
        role="The role to remove"
    )
    async def remove_role(self, interaction: discord.Interaction, user: discord.Member, role: discord.Role):
        """Remove a role from a user."""
        if not has_role_management_permissions(interaction.user, interaction.guild):
            await interaction.response.send_message("❌ You don't have permission to manage roles.", ephemeral=True)
            return
        
        # Check if the role is higher than the user's top role
        if role >= interaction.user.top_role and interaction.user != interaction.guild.owner:
            await interaction.response.send_message("❌ You cannot remove a role higher than or equal to your highest role.", ephemeral=True)
            return
        
        # Check if the role is higher than the bot's top role
        if role >= interaction.guild.me.top_role:
            await interaction.response.send_message("❌ I cannot remove a role higher than or equal to my highest role.", ephemeral=True)
            return
        
        # Check if user has the role
        if role not in user.roles:
            await interaction.response.send_message(f"❌ {user.mention} doesn't have the {role.mention} role.", ephemeral=True)
            return
        
        # Check for @everyone role
        if role.name == "@everyone":
            await interaction.response.send_message("❌ Cannot remove the @everyone role.", ephemeral=True)
            return
        
        try:
            await user.remove_roles(role, reason=f"Role removed by {interaction.user}")
            
            embed = create_embed(
                title="✅ Role Removed",
                description=f"Successfully removed {role.mention} from {user.mention}",
                color=self.config.COLORS["success"]
            )
            embed.add_field(name="Removed by", value=interaction.user.mention, inline=True)
            embed.add_field(name="Role", value=role.mention, inline=True)
            
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to remove that role.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ An error occurred: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="createrole", description="Create a new role")
    @app_commands.describe(
        name="The name of the role",
        color="The color of the role (hex format, e.g., #ff0000)",
        mentionable="Whether the role should be mentionable",
        hoisted="Whether the role should be displayed separately"
    )
    async def create_role(self, interaction: discord.Interaction, name: str, color: str = None, mentionable: bool = False, hoisted: bool = False):
        """Create a new role."""
        if not has_role_management_permissions(interaction.user, interaction.guild):
            await interaction.response.send_message("❌ You don't have permission to manage roles.", ephemeral=True)
            return
        
        # Validate role name
        if len(name) > 100:
            await interaction.response.send_message("❌ Role name cannot exceed 100 characters.", ephemeral=True)
            return
        
        # Check if role with same name exists
        if discord.utils.get(interaction.guild.roles, name=name):
            await interaction.response.send_message(f"❌ A role with the name '{name}' already exists.", ephemeral=True)
            return
        
        # Parse color
        role_color = discord.Color.default()
        if color:
            try:
                # Remove # if present
                color = color.lstrip('#')
                role_color = discord.Color(int(color, 16))
            except ValueError:
                await interaction.response.send_message("❌ Invalid color format. Use hex format like #ff0000 or ff0000.", ephemeral=True)
                return
        
        try:
            role = await interaction.guild.create_role(
                name=name,
                color=role_color,
                mentionable=mentionable,
                hoist=hoisted,
                reason=f"Role created by {interaction.user}"
            )
            
            embed = create_embed(
                title="✅ Role Created",
                description=f"Successfully created role {role.mention}",
                color=role_color if role_color != discord.Color.default() else self.config.COLORS["success"]
            )
            
            embed.add_field(name="Name", value=name, inline=True)
            embed.add_field(name="Color", value=f"#{role_color.value:06x}" if role_color != discord.Color.default() else "Default", inline=True)
            embed.add_field(name="Mentionable", value="Yes" if mentionable else "No", inline=True)
            embed.add_field(name="Hoisted", value="Yes" if hoisted else "No", inline=True)
            embed.add_field(name="Created by", value=interaction.user.mention, inline=True)
            embed.add_field(name="Role ID", value=f"`{role.id}`", inline=True)
            
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to create roles.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ An error occurred: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="roleinfo", description="Get information about a role")
    @app_commands.describe(role="The role to get information about")
    async def role_info(self, interaction: discord.Interaction, role: discord.Role):
        """Display information about a role."""
        embed = create_embed(
            title=f"🎭 Role Information: {role.name}",
            color=role.color if role.color != discord.Color.default() else self.config.COLORS["info"]
        )
        
        # Basic information
        embed.add_field(
            name="📝 Basic Info",
            value=f"**Name:** {role.name}\n"
                  f"**ID:** `{role.id}`\n"
                  f"**Position:** {role.position}\n"
                  f"**Created:** <t:{int(role.created_at.timestamp())}:F>",
            inline=True
        )
        
        # Settings
        embed.add_field(
            name="⚙️ Settings",
            value=f"**Color:** #{role.color.value:06x}\n"
                  f"**Mentionable:** {'Yes' if role.mentionable else 'No'}\n"
                  f"**Hoisted:** {'Yes' if role.hoist else 'No'}\n"
                  f"**Managed:** {'Yes' if role.managed else 'No'}",
            inline=True
        )
        
        # Member count
        member_count = len(role.members)
        embed.add_field(
            name="👥 Members",
            value=f"**{member_count}** members have this role",
            inline=True
        )
        
        # Key permissions
        key_perms = []
        if role.permissions.administrator:
            key_perms.append("Administrator")
        elif role.permissions.manage_guild:
            key_perms.append("Manage Server")
        elif role.permissions.manage_roles:
            key_perms.append("Manage Roles")
        elif role.permissions.manage_channels:
            key_perms.append("Manage Channels")
        elif role.permissions.kick_members:
            key_perms.append("Kick Members")
        elif role.permissions.ban_members:
            key_perms.append("Ban Members")
        elif role.permissions.manage_messages:
            key_perms.append("Manage Messages")
        
        if key_perms:
            embed.add_field(
                name="🔑 Key Permissions",
                value="\n".join([f"• {perm}" for perm in key_perms[:5]]),
                inline=False
            )
        
        # Show some members if any
        if role.members and member_count <= 20:
            member_list = [member.display_name for member in role.members[:10]]
            if len(role.members) > 10:
                member_list.append(f"... and {len(role.members) - 10} more")
            
            embed.add_field(
                name="👤 Members with this role",
                value="\n".join(member_list),
                inline=False
            )
        elif member_count > 20:
            embed.add_field(
                name="👤 Members with this role",
                value=f"Too many members to list ({member_count} total)",
                inline=False
            )
        
        embed.set_footer(
            text=f"Requested by {interaction.user}",
            icon_url=interaction.user.display_avatar.url
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="whohas", description="See who has a specific role")
    @app_commands.describe(role="The role to check")
    async def who_has(self, interaction: discord.Interaction, role: discord.Role):
        """Show members who have a specific role."""
        members = role.members
        
        if not members:
            embed = create_embed(
                title=f"👥 Members with {role.name}",
                description="No members have this role.",
                color=self.config.COLORS["info"]
            )
            await interaction.response.send_message(embed=embed)
            return
        
        embed = create_embed(
            title=f"👥 Members with {role.name}",
            description="\n".join([member.mention for member in members[:25]]),
            color=role.color if role.color != discord.Color.default() else self.config.COLORS["info"]
        )
        
        if len(members) > 25:
            embed.set_footer(text=f"And {len(members) - 25} more...")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(RolesCog(bot))
