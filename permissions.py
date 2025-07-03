"""
Permission checking utilities
"""

import discord
from config import BotConfig

config = BotConfig()

def has_moderation_permissions(user: discord.Member, guild: discord.Guild) -> bool:
    """
    Check if a user has moderation permissions.
    
    Args:
        user: The member to check
        guild: The guild context
    
    Returns:
        bool: True if user has moderation permissions
    """
    if user == guild.owner:
        return True
    
    if user.guild_permissions.administrator:
        return True
    
    # Check for specific moderation permissions
    moderation_perms = [
        user.guild_permissions.kick_members,
        user.guild_permissions.ban_members,
        user.guild_permissions.manage_messages,
        user.guild_permissions.manage_roles,
        user.guild_permissions.manage_channels
    ]
    
    return any(moderation_perms)

def has_role_management_permissions(user: discord.Member, guild: discord.Guild) -> bool:
    """
    Check if a user has role management permissions.
    
    Args:
        user: The member to check
        guild: The guild context
    
    Returns:
        bool: True if user has role management permissions
    """
    if user == guild.owner:
        return True
    
    if user.guild_permissions.administrator:
        return True
    
    return user.guild_permissions.manage_roles

def can_moderate_member(moderator: discord.Member, target: discord.Member) -> bool:
    """
    Check if a moderator can moderate a target member.
    
    Args:
        moderator: The member attempting to moderate
        target: The target member
    
    Returns:
        bool: True if moderation is allowed
    """
    # Guild owner can moderate anyone except themselves
    if moderator == moderator.guild.owner:
        return moderator != target
    
    # Can't moderate yourself
    if moderator == target:
        return False
    
    # Can't moderate someone with higher or equal role
    if target.top_role >= moderator.top_role:
        return False
    
    # Can't moderate the guild owner
    if target == target.guild.owner:
        return False
    
    return True

def can_manage_role(user: discord.Member, role: discord.Role) -> bool:
    """
    Check if a user can manage a specific role.
    
    Args:
        user: The member to check
        role: The role to manage
    
    Returns:
        bool: True if user can manage the role
    """
    # Guild owner can manage any role except @everyone
    if user == user.guild.owner and role.name != "@everyone":
        return True
    
    # Administrator can manage roles below their highest role
    if user.guild_permissions.administrator and role < user.top_role:
        return True
    
    # Users with manage_roles can manage roles below their highest role
    if user.guild_permissions.manage_roles and role < user.top_role:
        return True
    
    return False

def bot_can_manage_role(bot_member: discord.Member, role: discord.Role) -> bool:
    """
    Check if the bot can manage a specific role.
    
    Args:
        bot_member: The bot's member object
        role: The role to manage
    
    Returns:
        bool: True if bot can manage the role
    """
    # Bot needs manage_roles permission
    if not bot_member.guild_permissions.manage_roles:
        return False
    
    # Bot can't manage roles higher than or equal to its highest role
    if role >= bot_member.top_role:
        return False
    
    # Bot can't manage @everyone
    if role.name == "@everyone":
        return False
    
    # Bot can't manage managed roles (integration roles)
    if role.managed:
        return False
    
    return True

def check_hierarchy(user: discord.Member, target: discord.Member) -> tuple[bool, str]:
    """
    Check role hierarchy between two members.
    
    Args:
        user: The user performing the action
        target: The target member
    
    Returns:
        tuple: (bool: allowed, str: reason)
    """
    if user == user.guild.owner:
        if target == user:
            return False, "You cannot perform this action on yourself."
        return True, "Guild owner can moderate any member."
    
    if target == target.guild.owner:
        return False, "You cannot moderate the server owner."
    
    if user == target:
        return False, "You cannot perform this action on yourself."
    
    if target.top_role >= user.top_role:
        return False, "You cannot moderate someone with a higher or equal role."
    
    return True, "Action allowed."

def has_permission_in_channel(member: discord.Member, channel: discord.abc.GuildChannel, permission: str) -> bool:
    """
    Check if a member has a specific permission in a channel.
    
    Args:
        member: The member to check
        channel: The channel to check permissions in
        permission: The permission name to check
    
    Returns:
        bool: True if member has the permission
    """
    permissions = channel.permissions_for(member)
    return getattr(permissions, permission, False)

def get_missing_permissions(member: discord.Member, required_permissions: list) -> list:
    """
    Get a list of missing permissions for a member.
    
    Args:
        member: The member to check
        required_permissions: List of required permission names
    
    Returns:
        list: List of missing permission names
    """
    missing = []
    
    for permission in required_permissions:
        if not getattr(member.guild_permissions, permission, False):
            missing.append(permission)
    
    return missing

def format_missing_permissions(missing_permissions: list) -> str:
    """
    Format missing permissions into a readable string.
    
    Args:
        missing_permissions: List of missing permission names
    
    Returns:
        str: Formatted string of missing permissions
    """
    if not missing_permissions:
        return "No missing permissions"
    
    # Permission name mapping
    perm_names = {
        'kick_members': 'Kick Members',
        'ban_members': 'Ban Members',
        'manage_messages': 'Manage Messages',
        'manage_roles': 'Manage Roles',
        'manage_channels': 'Manage Channels',
        'administrator': 'Administrator',
        'manage_guild': 'Manage Server'
    }
    
    formatted = [perm_names.get(perm, perm.replace('_', ' ').title()) for perm in missing_permissions]
    
    if len(formatted) == 1:
        return formatted[0]
    elif len(formatted) == 2:
        return f"{formatted[0]} and {formatted[1]}"
    else:
        return f"{', '.join(formatted[:-1])}, and {formatted[-1]}"
