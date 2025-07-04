import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import yt_dlp

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="play", description="Play a song by name or URL.")
    @app_commands.describe(query="Song name or YouTube URL")
    async def play(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer()

        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.followup.send("❌ You must be in a voice channel to use this command.")
            return

        voice_channel = interaction.user.voice.channel

        # Connect or move to user's voice channel
        if interaction.guild.voice_client:
            vc = interaction.guild.voice_client
            if vc.channel != voice_channel:
                await vc.move_to(voice_channel)
        else:
            vc = await voice_channel.connect()

        # yt_dlp options with search
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'noplaylist': True,
            'default_search': 'ytsearch1',
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(query, download=False)
                if 'entries' in info:
                    info = info['entries'][0]  # Get first search result

                audio_url = info['url']
                title = info.get('title', 'Unknown Title')

            vc.stop()
            vc.play(discord.FFmpegPCMAudio(audio_url), after=lambda e: print(f"[Music] Finished: {e}"))
            await interaction.followup.send(f"🎶 Now playing: **{title}**")

        except Exception as e:
            await interaction.followup.send(f"❌ Failed to play: {e}")

    @app_commands.command(name="stop", description="Stop the music and leave the channel.")
    async def stop(self, interaction: discord.Interaction):
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()
            await interaction.response.send_message("⏹️ Stopped and left the voice channel.")
        else:
            await interaction.response.send_message("❌ I'm not in a voice channel.")

async def setup(bot):
    await bot.add_cog(Music(bot))
