import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

class ServerInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="serverinfo", description="Shows detailed information about the server")
    async def serverinfo(self, interaction: discord.Interaction):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("This command must be used in a server.")
            return

        icon = guild.icon.url if guild.icon else None
        banner = guild.banner.url if guild.banner else None
        splash = guild.splash.url if guild.splash else None
        system_channel = guild.system_channel.mention if guild.system_channel else "Not set"
        afk_channel = guild.afk_channel.mention if guild.afk_channel else "Not set"

        embed = discord.Embed(
            title=f"🌐 {guild.name} — Server Info",
            color=discord.Color.blurple(),
            timestamp=datetime.utcnow()
        )

        embed.set_thumbnail(url=icon)
        if banner:
            embed.set_image(url=banner)

        embed.add_field(name="🆔 Server ID", value=str(guild.id), inline=True)
        embed.add_field(name="👑 Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
        embed.add_field(name="🌎 Region", value=str(guild.preferred_locale).capitalize(), inline=True)

        embed.add_field(name="📅 Created On", value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
        embed.add_field(name="👥 Members", value=f"{guild.member_count}", inline=True)
        embed.add_field(name="🧑‍🤝‍🧑 Humans / 🤖 Bots", value=f"{len([m for m in guild.members if not m.bot])} / {len([m for m in guild.members if m.bot])}", inline=True)

        embed.add_field(name="💬 Text Channels", value=f"{len(guild.text_channels)}", inline=True)
        embed.add_field(name="🔊 Voice Channels", value=f"{len(guild.voice_channels)}", inline=True)
        embed.add_field(name="📁 Categories", value=f"{len(guild.categories)}", inline=True)

        embed.add_field(name="📛 Roles", value=f"{len(guild.roles)}", inline=True)
        embed.add_field(name="😃 Emojis", value=f"{len(guild.emojis)}", inline=True)
        embed.add_field(name="🚀 Boosts", value=f"Level {guild.premium_tier} with {guild.premium_subscription_count} boosts", inline=False)

        embed.add_field(name="✅ Verification Level", value=str(guild.verification_level).capitalize(), inline=True)
        embed.add_field(name="💤 AFK Timeout", value=f"{guild.afk_timeout // 60} minutes", inline=True)
        embed.add_field(name="💬 System Channel", value=system_channel, inline=True)

        if splash:
            embed.set_footer(text="Server has a splash image")
        else:
            embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ServerInfo(bot))
