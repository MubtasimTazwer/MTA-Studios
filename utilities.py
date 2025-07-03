"""
Utilities Cog - Various utility commands like polls, reminders, weather, etc.
"""

import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import aiohttp
import json
import requests
from datetime import datetime, timedelta
# from utils.helpers import create_embed

def create_embed(title=None, description=None, color=discord.Color.blue()):
    embed = discord.Embed(
        title=title or "Information",
        description=description or "",
        color=color
    )
    return embed

from config import BotConfig


class MatchDetailsView(discord.ui.View):
    """Interactive view for displaying detailed match information."""
    
    def __init__(self, matches):
        super().__init__(timeout=300)  # 5 minutes timeout
        self.matches = matches
        
        # Add buttons for each match (up to 5)
        for i, match in enumerate(matches):
            home = match['teams']['home']['name']
            away = match['teams']['away']['name']
            score_home = match['goals']['home']
            score_away = match['goals']['away']
            
            button = discord.ui.Button(
                label=f"{home} {score_home}-{score_away} {away}",
                style=discord.ButtonStyle.primary,
                custom_id=f"match_{i}",
                emoji="⚽"
            )
            button.callback = self.create_match_callback(i)
            self.add_item(button)
    
    def create_match_callback(self, match_index):
        """Create a callback function for a specific match button."""
        async def match_callback(interaction: discord.Interaction):
            await self.show_match_details(interaction, match_index)
        return match_callback
    
    async def show_match_details(self, interaction: discord.Interaction, match_index: int):
        """Show detailed information for a specific match."""
        try:
            match = self.matches[match_index]
            
            # Extract detailed match data
            home_team = match['teams']['home']['name']
            away_team = match['teams']['away']['name']
            home_score = match['goals']['home']
            away_score = match['goals']['away']
            league = match['league']['name']
            country = match['league']['country']
            elapsed = match['fixture']['status']['elapsed']
            venue = match['fixture']['venue']['name']
            city = match['fixture']['venue']['city']
            referee = match['fixture']['referee']
            
            # Create detailed embed
            embed = create_embed(
                title=f"⚽ {home_team} vs {away_team}",
                description=f"**Live Score: {home_score} - {away_score}**",
                color=0x00ff00
            )
            
            # Match info
            embed.add_field(
                name="🏆 Competition",
                value=f"{league}\n🌍 {country}",
                inline=True
            )
            
            embed.add_field(
                name="🕐 Match Time",
                value=f"{elapsed}' (Live)",
                inline=True
            )
            
            embed.add_field(
                name="🏟️ Venue",
                value=f"{venue}\n📍 {city}",
                inline=True
            )
            
            # Team details
            embed.add_field(
                name=f"🏠 {home_team}",
                value=f"⚽ Goals: {home_score}\n🎯 Playing at home",
                inline=True
            )
            
            embed.add_field(
                name=f"✈️ {away_team}",
                value=f"⚽ Goals: {away_score}\n🎯 Playing away",
                inline=True
            )
            
            if referee:
                embed.add_field(
                    name="👨‍⚖️ Referee",
                    value=referee,
                    inline=True
                )
            
            # Additional match status info
            status = match['fixture']['status']['long']
            embed.add_field(
                name="📊 Match Status",
                value=status,
                inline=False
            )
            
            embed.set_footer(
                text="Data from API-Football • Click buttons below for more info",
                icon_url=interaction.user.display_avatar.url
            )
            
            # Create buttons for lineups and back
            back_view = MatchActionsView(self.matches, match_index)
            
            await interaction.response.edit_message(embed=embed, view=back_view)
            
        except Exception as e:
            await interaction.response.send_message(
                "❌ Error loading match details. Please try again.",
                ephemeral=True
            )


class BackToMatchesView(discord.ui.View):
    """View with back button to return to match list."""
    
    def __init__(self, matches):
        super().__init__(timeout=300)
        self.matches = matches
    
    @discord.ui.button(label="Back to Matches", style=discord.ButtonStyle.secondary, emoji="🔙")
    async def back_to_matches(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Return to the main matches list."""
        # Recreate the original embed
        embed = create_embed(
            title="📺 Live Football Scores",
            description="Current live matches from around the world",
            color=0x00ff00
        )
        
        matches_added = 0
        for match_data in self.matches:
            home = match_data['teams']['home']['name']
            away = match_data['teams']['away']['name']
            score_home = match_data['goals']['home']
            score_away = match_data['goals']['away']
            league = match_data['league']['name']
            elapsed = match_data['fixture']['status']['elapsed']

            match_text = f"**{home} {score_home} - {score_away} {away}**\n"
            match_text += f"*League: {league}*\n"
            match_text += f"🕐 {elapsed}'"
            
            embed.add_field(
                name=f"⚽ Match {matches_added + 1}",
                value=match_text,
                inline=True
            )
            matches_added += 1
        
        embed.add_field(
            name="📊 Want More Details?",
            value="Click the buttons below to see detailed match information!",
            inline=False
        )
        
        embed.set_footer(
            text=f"Requested by {interaction.user}",
            icon_url=interaction.user.display_avatar.url
        )
        
        # Recreate the original view
        original_view = MatchDetailsView(self.matches)
        
        await interaction.response.edit_message(embed=embed, view=original_view)


class MatchActionsView(discord.ui.View):
    """View with multiple action buttons for match details."""
    
    def __init__(self, matches, current_match_index):
        super().__init__(timeout=300)
        self.matches = matches
        self.current_match_index = current_match_index
    
    @discord.ui.button(label="Show Playing XI", style=discord.ButtonStyle.success, emoji="👥")
    async def show_lineups(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show the starting lineups for both teams."""
        await self.fetch_and_show_lineups(interaction)
    
    @discord.ui.button(label="Back to Matches", style=discord.ButtonStyle.secondary, emoji="🔙")
    async def back_to_matches(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Return to the main matches list."""
        # Recreate the original embed
        embed = create_embed(
            title="📺 Live Football Scores",
            description="Current live matches from around the world",
            color=0x00ff00
        )
        
        matches_added = 0
        for match_data in self.matches:
            home = match_data['teams']['home']['name']
            away = match_data['teams']['away']['name']
            score_home = match_data['goals']['home']
            score_away = match_data['goals']['away']
            league = match_data['league']['name']
            elapsed = match_data['fixture']['status']['elapsed']

            match_text = f"**{home} {score_home} - {score_away} {away}**\n"
            match_text += f"*League: {league}*\n"
            match_text += f"🕐 {elapsed}'"
            
            embed.add_field(
                name=f"⚽ Match {matches_added + 1}",
                value=match_text,
                inline=True
            )
            matches_added += 1
        
        embed.add_field(
            name="📊 Want More Details?",
            value="Click the buttons below to see detailed match information!",
            inline=False
        )
        
        embed.set_footer(
            text=f"Requested by {interaction.user}",
            icon_url=interaction.user.display_avatar.url
        )
        
        # Recreate the original view
        original_view = MatchDetailsView(self.matches)
        
        await interaction.response.edit_message(embed=embed, view=original_view)
    
    async def fetch_and_show_lineups(self, interaction: discord.Interaction):
        """Fetch and display team lineups for the current match."""
        try:
            await interaction.response.defer()
            
            match = self.matches[self.current_match_index]
            fixture_id = match['fixture']['id']
            
            # API endpoint for lineups
            lineup_url = f"https://v3.football.api-sports.io/fixtures/lineups"
            headers = {
                'X-RapidAPI-Key': '2a1eb675326c4e4ec655221a750b1cfb',
                'X-RapidAPI-Host': 'v3.football.api-sports.io'
            }
            params = {'fixture': fixture_id}
            
            response = requests.get(lineup_url, headers=headers, params=params)
            
            if response.status_code != 200:
                embed = create_embed(
                    title="❌ Lineup Information Unavailable",
                    description="Unable to fetch lineup data at this time.",
                    color=0xff0000
                )
                back_view = MatchActionsView(self.matches, self.current_match_index)
                await interaction.followup.edit_message(interaction.message.id, embed=embed, view=back_view)
                return
            
            lineup_data = response.json()
            lineups = lineup_data.get('response', [])
            
            if not lineups or len(lineups) < 2:
                embed = create_embed(
                    title="📋 Lineups Not Available",
                    description="Starting lineups haven't been announced yet or are not available for this match.",
                    color=0xffff00
                )
                back_view = MatchActionsView(self.matches, self.current_match_index)
                await interaction.followup.edit_message(interaction.message.id, embed=embed, view=back_view)
                return
            
            # Extract team information
            home_team_data = lineups[0]
            away_team_data = lineups[1]
            
            home_team = home_team_data['team']['name']
            away_team = away_team_data['team']['name']
            home_formation = home_team_data.get('formation', 'Unknown')
            away_formation = away_team_data.get('formation', 'Unknown')
            
            # Create lineup embed
            embed = create_embed(
                title=f"👥 Starting Lineups",
                description=f"**{home_team} vs {away_team}**",
                color=0x00ff00
            )
            
            # Home team lineup
            home_xi = home_team_data.get('startXI', [])
            if home_xi:
                home_players = []
                for player_data in home_xi[:11]:  # First 11 players
                    player = player_data['player']
                    name = player['name']
                    number = player.get('number', '?')
                    position = player.get('pos', 'Unknown')
                    home_players.append(f"{number}. {name} ({position})")
                
                home_lineup_text = "\n".join(home_players)
                embed.add_field(
                    name=f"🏠 {home_team} ({home_formation})",
                    value=home_lineup_text[:1024],  # Discord field limit
                    inline=True
                )
            
            # Away team lineup
            away_xi = away_team_data.get('startXI', [])
            if away_xi:
                away_players = []
                for player_data in away_xi[:11]:  # First 11 players
                    player = player_data['player']
                    name = player['name']
                    number = player.get('number', '?')
                    position = player.get('pos', 'Unknown')
                    away_players.append(f"{number}. {name} ({position})")
                
                away_lineup_text = "\n".join(away_players)
                embed.add_field(
                    name=f"✈️ {away_team} ({away_formation})",
                    value=away_lineup_text[:1024],  # Discord field limit
                    inline=True
                )
            
            # Add coaches if available
            home_coach = home_team_data.get('coach', {}).get('name')
            away_coach = away_team_data.get('coach', {}).get('name')
            
            if home_coach or away_coach:
                coach_info = ""
                if home_coach:
                    coach_info += f"🏠 Coach: {home_coach}\n"
                if away_coach:
                    coach_info += f"✈️ Coach: {away_coach}"
                
                embed.add_field(
                    name="👨‍💼 Coaches",
                    value=coach_info,
                    inline=False
                )
            
            embed.set_footer(
                text="Data from API-Football • Playing XI and formations",
                icon_url=interaction.user.display_avatar.url
            )
            
            # Create view with back button
            back_view = MatchActionsView(self.matches, self.current_match_index)
            
            await interaction.followup.edit_message(interaction.message.id, embed=embed, view=back_view)
            
        except Exception as e:
            embed = create_embed(
                title="❌ Error Loading Lineups",
                description="There was an issue fetching the lineup information.",
                color=0xff0000
            )
            back_view = MatchActionsView(self.matches, self.current_match_index)
            await interaction.followup.edit_message(interaction.message.id, embed=embed, view=back_view)


class UtilitiesCog(commands.Cog):
    """Cog containing utility commands."""
    
    def __init__(self, bot):
        self.bot = bot
        self.config = BotConfig()
        self.active_polls = {}
        self.reminders = {}
    
    @app_commands.command(name="poll", description="Create a poll with multiple options")
    @app_commands.describe(
        question="The poll question",
        options="Poll options separated by commas (max 10)"
    )
    async def poll(self, interaction: discord.Interaction, question: str, options: str):
        """Create a poll with reactions."""
        option_list = [opt.strip() for opt in options.split(',') if opt.strip()]
        
        if len(option_list) < 2:
            await interaction.response.send_message("❌ You need at least 2 options for a poll.", ephemeral=True)
            return
        
        if len(option_list) > self.config.MAX_POLL_OPTIONS:
            await interaction.response.send_message(f"❌ Maximum {self.config.MAX_POLL_OPTIONS} options allowed.", ephemeral=True)
            return
        
        # Emoji numbers for reactions
        number_emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
        
        embed = create_embed(
            title="📊 Poll",
            description=f"**{question}**",
            color=self.config.COLORS["info"]
        )
        
        # Add options with emoji numbers
        options_text = ""
        for i, option in enumerate(option_list):
            options_text += f"{number_emojis[i]} {option}\n"
        
        embed.add_field(name="Options", value=options_text, inline=False)
        embed.add_field(name="Instructions", value="React with the corresponding emoji to vote!", inline=False)
        
        embed.set_footer(
            text=f"Poll created by {interaction.user}",
            icon_url=interaction.user.display_avatar.url
        )
        
        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()
        
        # Add reactions
        for i in range(len(option_list)):
            await message.add_reaction(number_emojis[i])
        
        # Store poll info
        self.active_polls[message.id] = {
            'question': question,
            'options': option_list,
            'creator': interaction.user.id,
            'channel': interaction.channel.id
        }
    
    @app_commands.command(name="pollresults", description="Get results of a poll")
    @app_commands.describe(message_id="The ID of the poll message")
    async def pollresults(self, interaction: discord.Interaction, message_id: str):
        """Get poll results."""
        try:
            msg_id = int(message_id)
        except ValueError:
            await interaction.response.send_message("❌ Invalid message ID.", ephemeral=True)
            return
        
        if msg_id not in self.active_polls:
            await interaction.response.send_message("❌ Poll not found or not created by this bot.", ephemeral=True)
            return
        
        try:
            message = await interaction.channel.fetch_message(msg_id)
        except discord.NotFound:
            await interaction.response.send_message("❌ Poll message not found.", ephemeral=True)
            return
        
        poll_info = self.active_polls[msg_id]
        number_emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
        
        embed = create_embed(
            title="📊 Poll Results",
            description=f"**{poll_info['question']}**",
            color=self.config.COLORS["success"]
        )
        
        total_votes = 0
        results = []
        
        for i, option in enumerate(poll_info['options']):
            reaction = discord.utils.get(message.reactions, emoji=number_emojis[i])
            votes = (reaction.count - 1) if reaction else 0  # Subtract bot's reaction
            total_votes += votes
            results.append((option, votes))
        
        # Sort by vote count
        results.sort(key=lambda x: x[1], reverse=True)
        
        if total_votes == 0:
            embed.add_field(name="Results", value="No votes yet!", inline=False)
        else:
            results_text = ""
            for i, (option, votes) in enumerate(results):
                percentage = (votes / total_votes) * 100 if total_votes > 0 else 0
                bar_length = int(percentage / 10)
                bar = "█" * bar_length + "░" * (10 - bar_length)
                results_text += f"**{option}**\n{bar} {votes} votes ({percentage:.1f}%)\n\n"
            
            embed.add_field(name="Results", value=results_text, inline=False)
        
        embed.add_field(name="Total Votes", value=str(total_votes), inline=True)
        embed.set_footer(text=f"Poll created by {self.bot.get_user(poll_info['creator'])}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="remind", description="Set a reminder")
    @app_commands.describe(
        time="Time in minutes",
        message="Reminder message"
    )
    async def remind(self, interaction: discord.Interaction, time: int, message: str = "No message provided"):
        """Set a reminder."""
        if time < 1 or time > (self.config.MAX_REMINDER_TIME // 60):
            await interaction.response.send_message(f"❌ Time must be between 1 minute and {self.config.MAX_REMINDER_TIME // 60} minutes.", ephemeral=True)
            return
        
        reminder_time = datetime.utcnow() + timedelta(minutes=time)
        
        embed = create_embed(
            title="⏰ Reminder Set",
            description=f"I'll remind you in **{time} minutes**",
            color=self.config.COLORS["success"]
        )
        embed.add_field(name="Message", value=message, inline=False)
        embed.add_field(name="Reminder Time", value=f"<t:{int(reminder_time.timestamp())}:F>", inline=False)
        
        await interaction.response.send_message(embed=embed)
        
        # Store reminder
        reminder_id = f"{interaction.user.id}_{int(datetime.utcnow().timestamp())}"
        self.reminders[reminder_id] = {
            'user_id': interaction.user.id,
            'channel_id': interaction.channel.id,
            'message': message,
            'time': reminder_time
        }
        
        # Wait and send reminder
        await asyncio.sleep(time * 60)
        
        if reminder_id in self.reminders:  # Check if reminder wasn't cancelled
            reminder_embed = create_embed(
                title="⏰ Reminder",
                description=f"You asked me to remind you:",
                color=self.config.COLORS["warning"]
            )
            reminder_embed.add_field(name="Message", value=message, inline=False)
            
            try:
                user = self.bot.get_user(interaction.user.id)
                channel = self.bot.get_channel(interaction.channel.id)
                if channel:
                    await channel.send(f"{user.mention}", embed=reminder_embed)
            except:
                pass  # Channel might be deleted or bot removed
            
            del self.reminders[reminder_id]
    
    @app_commands.command(name="weather", description="Get weather search links for a city")
    @app_commands.describe(city="The city to get weather links for")
    async def weather(self, interaction: discord.Interaction, city: str):
        """Get weather search links for a city."""
        embed = create_embed(
            title=f"🌤️ Weather for {city.title()}",
            description=f"Here are some reliable weather sources for **{city.title()}**:",
            color=self.config.COLORS["info"]
        )
        
        # Create search URLs for popular weather services
        city_encoded = city.replace(" ", "+")
        
        weather_links = [
            f"[Weather.com](https://weather.com/search/enhancedlocalsearch?query={city_encoded})",
            f"[AccuWeather](https://www.accuweather.com/en/search-locations?query={city_encoded})",
            f"[Weather Underground](https://www.wunderground.com/weather/{city_encoded})",
            f"[OpenWeatherMap](https://openweathermap.org/find?q={city_encoded})",
            f"[Google Weather](https://www.google.com/search?q=weather+{city_encoded})"
        ]
        
        embed.add_field(
            name="🔗 Weather Sources",
            value="\n".join(weather_links),
            inline=False
        )
        
        embed.add_field(
            name="💡 Tip",
            value="Click any link above to get current weather conditions, forecasts, and detailed weather information for your location.",
            inline=False
        )
        
        embed.set_footer(
            text=f"Requested by {interaction.user}",
            icon_url=interaction.user.display_avatar.url
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="timestamp", description="Generate Discord timestamps")
    @app_commands.describe(
        time="Time in format: YYYY-MM-DD HH:MM (24h format)",
        style="Timestamp style"
    )
    @app_commands.choices(style=[
        app_commands.Choice(name="Short Time (16:20)", value="t"),
        app_commands.Choice(name="Long Time (4:20:30 PM)", value="T"),
        app_commands.Choice(name="Short Date (20/04/2021)", value="d"),
        app_commands.Choice(name="Long Date (20 April 2021)", value="D"),
        app_commands.Choice(name="Short Date/Time (20 April 2021 16:20)", value="f"),
        app_commands.Choice(name="Long Date/Time (Tuesday, 20 April 2021 16:20)", value="F"),
        app_commands.Choice(name="Relative Time (2 months ago)", value="R")
    ])
    async def timestamp(self, interaction: discord.Interaction, time: str, style: str = "f"):
        """Generate Discord timestamp."""
        try:
            # Parse the input time
            dt = datetime.strptime(time, "%Y-%m-%d %H:%M")
            timestamp = int(dt.timestamp())
            
            embed = create_embed(
                title="🕐 Discord Timestamp",
                color=self.config.COLORS["info"]
            )
            
            embed.add_field(
                name="Input",
                value=f"**{time}**",
                inline=True
            )
            
            embed.add_field(
                name="Timestamp Code",
                value=f"`<t:{timestamp}:{style}>`",
                inline=True
            )
            
            embed.add_field(
                name="Preview",
                value=f"<t:{timestamp}:{style}>",
                inline=False
            )
            
            embed.add_field(
                name="All Formats",
                value=f"**Short Time:** <t:{timestamp}:t> `<t:{timestamp}:t>`\n"
                      f"**Long Time:** <t:{timestamp}:T> `<t:{timestamp}:T>`\n"
                      f"**Short Date:** <t:{timestamp}:d> `<t:{timestamp}:d>`\n"
                      f"**Long Date:** <t:{timestamp}:D> `<t:{timestamp}:D>`\n"
                      f"**Short Date/Time:** <t:{timestamp}:f> `<t:{timestamp}:f>`\n"
                      f"**Long Date/Time:** <t:{timestamp}:F> `<t:{timestamp}:F>`\n"
                      f"**Relative:** <t:{timestamp}:R> `<t:{timestamp}:R>`",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
            
        except ValueError:
            await interaction.response.send_message(
                "❌ Invalid time format. Please use `YYYY-MM-DD HH:MM` format.\n"
                "Example: `2024-12-25 14:30`", 
                ephemeral=True
            )
    
    @app_commands.command(name="football", description="Get live football scores")
    @app_commands.describe(match="Search for a specific team or match (e.g. 'Arsenal', 'Real Madrid vs Barcelona')")
    async def football_scores(self, interaction: discord.Interaction, match: str = None):
        """Get live football scores using API-Football."""
        await interaction.response.defer()
        
        try:
            # API-Football config
            API_KEY = '2a1eb675326c4e4ec655221a750b1cfb'
            API_URL = 'https://v3.football.api-sports.io/fixtures?live=all'
            
            headers = {
                'x-apisports-key': API_KEY
            }
            
            response = requests.get(API_URL, headers=headers)
            
            if response.status_code != 200:
                embed = create_embed(
                    title="❌ Could not fetch live scores",
                    description="Unable to connect to the football API.",
                    color=self.config.COLORS["error"]
                )
                await interaction.followup.send(embed=embed)
                return

            data = response.json()
            all_matches = data.get('response', [])

            # Filter matches if specific match search is provided
            if match:
                filtered_matches = []
                search_terms = match.lower().split()
                
                for game in all_matches:
                    home_team = game['teams']['home']['name'].lower()
                    away_team = game['teams']['away']['name'].lower()
                    
                    # Check if any search term matches either team
                    match_found = False
                    for term in search_terms:
                        if term in home_team or term in away_team:
                            match_found = True
                            break
                    
                    if match_found:
                        filtered_matches.append(game)
                
                matches = filtered_matches
                if not matches:
                    embed = create_embed(
                        title=f"⚽ No matches found for '{match}'",
                        description="No live matches found for the specified team or match.",
                        color=self.config.COLORS["warning"]
                    )
                    embed.add_field(
                        name="💡 Try These Examples",
                        value="• `/football match: Arsenal`\n"
                              "• `/football match: Real Madrid`\n"
                              "• `/football match: Barcelona`\n"
                              "• `/football` (for all live matches)",
                        inline=False
                    )
                    await interaction.followup.send(embed=embed)
                    return
            else:
                matches = all_matches

            if not matches:
                embed = create_embed(
                    title="⚽ No live matches at the moment",
                    description="There are currently no live football matches.",
                    color=self.config.COLORS["warning"]
                )
                await interaction.followup.send(embed=embed)
                return

            # Create embed for live scores
            if match:
                embed = create_embed(
                    title=f"📺 Live Scores: {match}",
                    description=f"Matches found for '{match}'",
                    color=0x00ff00
                )
            else:
                embed = create_embed(
                    title="📺 Live Football Scores",
                    description="Current live matches from around the world",
                    color=0x00ff00
                )

            # Create view with buttons for match details
            view = MatchDetailsView(matches[:5])
            
            matches_added = 0
            for match_data in matches[:5]:  # Limit to first 5 matches
                home = match_data['teams']['home']['name']
                away = match_data['teams']['away']['name']
                score_home = match_data['goals']['home']
                score_away = match_data['goals']['away']
                league = match_data['league']['name']
                elapsed = match_data['fixture']['status']['elapsed']

                match_text = f"**{home} {score_home} - {score_away} {away}**\n"
                match_text += f"*League: {league}*\n"
                match_text += f"🕐 {elapsed}'"
                
                embed.add_field(
                    name=f"⚽ Match {matches_added + 1}",
                    value=match_text,
                    inline=True
                )
                matches_added += 1
            
            if matches_added > 0:
                embed.add_field(
                    name="📊 Want More Details?",
                    value="Click the buttons below to see detailed match information!",
                    inline=False
                )

            embed.set_footer(
                text=f"Requested by {interaction.user}",
                icon_url=interaction.user.display_avatar.url
            )

            if matches_added > 0:
                await interaction.followup.send(embed=embed, view=view)
            else:
                await interaction.followup.send(embed=embed)
            
        except Exception as e:
            # Error handling
            embed = create_embed(
                title="❌ Error Getting Football Scores",
                description="There was an issue fetching live scores.",
                color=self.config.COLORS["error"]
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="help", description="Get help with bot commands")
    async def help_command(self, interaction: discord.Interaction):
        """Display help information."""
        embed = create_embed(
            title="🤖 Discord Utility Bot - Help",
            description="Here are all the available commands:",
            color=self.config.COLORS["info"]
        )
        
        # Moderation Commands
        embed.add_field(
            name="🛡️ Moderation Commands",
            value="• `/kick` - Kick a member\n"
                  "• `/ban` - Ban a member\n"
                  "• `/unban` - Unban a user\n"
                  "• `/timeout` - Timeout a member\n"
                  "• `/clear` - Clear messages",
            inline=True
        )
        
        # Server Info Commands
        embed.add_field(
            name="📊 Server Information",
            value="• `/serverinfo` - Server details\n"
                  "• `/membercount` - Member statistics\n"
                  "• `/channels` - List all channels\n"
                  "• `/roles` - List all roles",
            inline=True
        )
        
        # User Info Commands
        embed.add_field(
            name="👤 User Information",
            value="• `/userinfo` - User profile\n"
                  "• `/avatar` - User's avatar\n"
                  "• `/joinposition` - Join position",
            inline=True
        )
        
        # Utility Commands
        embed.add_field(
            name="🔧 Utility Commands",
            value="• `/poll` - Create a poll\n"
                  "• `/pollresults` - Get poll results\n"
                  "• `/remind` - Set a reminder\n"
                  "• `/weather` - Get weather info\n"
                  "• `/football` - Live football scores\n"
                  "• `/timestamp` - Generate timestamps",
            inline=True
        )
        
        # Role Commands
        embed.add_field(
            name="🎭 Role Management",
            value="• `/addrole` - Add role to user\n"
                  "• `/removerole` - Remove role from user\n"
                  "• `/createrole` - Create a new role",
            inline=True
        )
        
        embed.add_field(
            name="ℹ️ Information",
            value="• Bot uses slash commands (`/`)\n"
                  "• Some commands require permissions\n"
                  "• Commands have cooldowns to prevent spam",
            inline=False
        )
        
        embed.set_footer(
            text=f"Requested by {interaction.user} • Bot developed by Mubtasim Tazwer",
            icon_url=interaction.user.display_avatar.url
        )
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(UtilitiesCog(bot))
