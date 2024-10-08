import datetime
import os
import sqlite3
import discord
import asyncio
import schedules
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from typing import Final, Optional
from parseresponses import get_response

load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='playerstats')
    @app_commands.describe(player='Enter first and last name, capitalize each.')
    async def playerstats_command(self, interaction: discord.Interaction, player: str):
        response = get_response('playerstats', player)
        await interaction.response.send_message(embed=response)

    @app_commands.command(name='standings')
    @app_commands.describe(season='Get standings by year. Format: YYYY-YYYY')
    async def standings_command(self, interaction: discord.Interaction, season: Optional[str] = None):
        if season:
            response = get_response('standings', season)
        else:
            response = get_response('currentstandings', None)
        await interaction.response.send_message(embed=response)

    @app_commands.command(name='leaders')
    @app_commands.describe(position='Skater or goalie')
    @app_commands.describe(category='Use /glossary for list of categories')
    async def leaders_command(self, interaction: discord.Interaction, position: str, category: str):
        params = [position, category]
        response = get_response('leaders', params)
        await interaction.response.send_message(embed=response)
    
    @app_commands.command(name='teamroster')
    @app_commands.describe(team='Enter the team you want the roster for')
    @app_commands.describe(season='Get team roster by year. Format: YYYY-YYYY')
    async def teamroster_command(self, interaction: discord.Interaction, team: str, season: Optional[str] = 'current'):
        params = [team, season]
        response = get_response('teamroster', params)
        await interaction.response.send_message(embed=response)

    @app_commands.command(name='playoffbracket')
    async def playoffbracket_command(self, interaction: discord.Interaction):
        response = get_response('playoffbracket', None)
        await interaction.response.send_message(embed=response)

    @app_commands.command(name='schedule')
    @app_commands.describe(team='Enter the team you want the schedule for')
    async def schedule_command(self, interaction: discord.Interaction, team: Optional[str] = None):
        if team:
            response = get_response('teamschedule', team)
        else:
            response = get_response('schedule', None)
        await interaction.response.send_message(embed=response)

    @app_commands.command(name='score')
    @app_commands.describe(team='Enter the team you want to see the live scoreboard for')
    async def score_command(self, interaction: discord.Interaction, team: str):
        response = get_response('score', team)
        await interaction.response.send_message(embed=response)

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='register')
    @app_commands.describe(username='Enter the name you want people to see on the leaderboard. Min 3 Characters, Max 25 Characters')
    async def register_command(self, interaction: discord.Interaction, username: str):
        params = [interaction.user.id, username]
        response = get_response('register', params)
        await interaction.response.send_message(content=interaction.user.mention, embed=response, ephemeral=True)

    @app_commands.command(name='bonus')
    async def bonus_command(self, interaction: discord.Interaction):
        response = get_response('bonus', interaction.user.id)
        await interaction.response.send_message(content=interaction.user.mention, embed=response)
    
    @app_commands.command(name='balance')
    async def balance_command(self, interaction: discord.Interaction):
        response = get_response('balance', interaction.user.id)
        await interaction.response.send_message(content=interaction.user.mention, embed=response)

    @app_commands.command(name='placebet')
    @app_commands.describe(team='Bet on which team will win. Use the three letter abbreviation')
    @app_commands.describe(wager='Place your wager. Max $500, Min $1')
    async def bet_command(self, interaction: discord.Interaction, team: str, wager: float):
        params = [interaction.user.id, team, wager]
        response = get_response('placebet', params)
        await interaction.response.send_message(content=interaction.user.mention, embed=response)

    @app_commands.command(name='mybets')
    async def mybets_command(self, interaction: discord.Interaction):
        response = get_response('mybets', interaction.user.id)
        await interaction.response.send_message(content=interaction.user.mention, embed=response)

    @app_commands.command(name='removebet')
    @app_commands.describe(bet_id='Enter the bet ID to remove')
    async def removebet_command(self, interaction: discord.Interaction, bet_id: int):
        params = [interaction.user.id, bet_id]
        response = get_response('removebet', params)
        await interaction.response.send_message(content=interaction.user.mention, embed=response)

    @app_commands.command(name='leaderboard')
    async def leaderboard_command(self, interaction: discord.Interaction):
        response = get_response('leaderboard', None)
        await interaction.response.send_message(embed=response)

class Casino(commands.Cog):
    def __init__(self):
        self.bot = bot

    @app_commands.command(name='slots')
    @app_commands.describe(wager='Enter your wager')
    async def slots(self, interaction:discord.Interaction, wager: int):
        user_id = interaction.user.id
        params = f'{user_id}-{wager}'
        response = get_response('slots', params)
        await interaction.response.send_message(embed=response)


class Scheduled(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.reset_bonuses())
        self.bot.loop.create_task(self.check_game_over())

    async def reset_bonuses(self):
        while True:
            now = datetime.datetime.now()
            then = now.replace(hour=23, minute=59, second=59, microsecond=59)
            wait_time = (then - now).total_seconds()
            await asyncio.sleep(wait_time)
            schedules.get_todays_games()
            schedules.reset_bonus()

    async def check_game_over(self):
        while True:
            now = datetime.datetime.now()
            start_time = now.replace(hour=19, minute=0, second=0, microsecond=0)
            if now.hour < 2:
                start_time = (now - datetime.timedelta(days=1)).replace(hour=19, minute=0, second=0, microsecond=0)

            end_time = start_time + datetime.timedelta(hours=7)

            if start_time <= now < end_time:
                schedules.check_game_ended()
                
            await asyncio.sleep(1 * 60)

async def setup(bot):
    if 'Commands' not in bot.cogs:
        await bot.add_cog(Commands(bot))
    if 'Economy' not in bot.cogs:
        await bot.add_cog(Economy(bot))
    if 'Scheduled' not in bot.cogs:
        await bot.add_cog(Scheduled(bot))
    print('Cogs Synced')
    await bot.tree.sync()

def initialize_economy():
    conn = sqlite3.connect('economy.db')
    c = conn.cursor()
    
    with open('tables.sql', 'r') as f:
        script = f.read()
    c.executescript(script)

    conn.commit()
    conn.close()
    print('Database Synced')

@bot.event
async def on_ready() -> None:
    initialize_economy()
    await setup(bot)
    print(f'{bot.user} is now running')

def main() -> None:
    bot.run(TOKEN)

if __name__ == '__main__':
    main()
