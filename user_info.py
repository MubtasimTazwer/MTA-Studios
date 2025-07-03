import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

class UserInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="userinfo", description="Shows detailed information about a user")
    @app_commands.describe(user="The user to get information about")
    async def userinfo(self, interaction: discord.Interaction, user: discord.User = None):
        user = user or interaction.user
        member = interaction.guild.get_member(user.id) if interaction.guild else None

        embed = discord.Embed(title=f"👤 User Info — {user.name}", color=discord.Color.green(), timestamp=datetime.utcnow())
        embed.set_thumbnail(url=user.avatar.url if user.avatar else None)

        embed.add_field(name="🆔 ID", value=user.id, inline=True)
        embed.add_field(name="🔢 Discriminator", value=f"#{user.discriminator}", inline=True)
        embed.add_field(name="🤖 Bot", value="Yes" if user.bot else "No", inline=True)

        embed.add_field(name="📅 Created Account", value=user.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)

        if member:
            embed.add_field(name="📆 Joined Server", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
            embed.add_field(name="📛 Top Role", value=member.top_role.mention, inline=True)
            embed.add_field(name="📜 Roles", value=", ".join([role.mention for role in member.roles if role.name != "@everyone"]) or "None", inline=False)

            status = str(member.status).capitalize()
            embed.add_field(name="🟢 Status", value=status, inline=True)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(UserInfo(bot))
