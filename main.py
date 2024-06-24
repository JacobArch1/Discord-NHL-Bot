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
bot = commands.Bot(command_prefix="!", intents=intents)

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='help')
    async def help_command(self, interaction: discord.Interaction):
        response = get_response('help', None)
        await interaction.response.send_message(embed=response, ephemeral=True)

    @app_commands.command(name='glossary')
    async def glossary_command(self, interaction: discord.Interaction):
        response = get_response('glossary', None)
        await interaction.response.send_message(embed=response, ephemeral=True)

    @app_commands.command(name='playerstats')
    @app_commands.describe(player="Enter first and last name, capitalize each.")
    async def playerstats_command(self, interaction: discord.Interaction, player: str):
        response = get_response('playerstats', player)
        await interaction.response.send_message(embed=response)

    @app_commands.command(name='standings')
    @app_commands.describe(season="Get standings by year. Format: YYYY-YYYY")
    async def standings_command(self, interaction: discord.Interaction, season: Optional[str] = None):
        if season:
            response = get_response('standings', season)
        else:
            response = get_response('currentstandings', None)
        await interaction.response.send_message(embed=response)

    @app_commands.command(name='leaders')
    @app_commands.describe(position="Skater or goalie")
    @app_commands.describe(category="Use /glossary for list of categories")
    async def leaders_command(self, interaction: discord.Interaction, position: str, category: str):
        params = f'{position} {category}'
        response = get_response('leaders', params)
        await interaction.response.send_message(embed=response)
    
    @app_commands.command(name="teamroster")
    @app_commands.describe(team="Enter the team you want the roster for")
    @app_commands.describe(season="Get team roster by year. Format: YYYY-YYYY")
    async def teamroster_command(self, interaction: discord.Interaction, team: str, season: Optional[str] = 'current'):
        params = f'{team} {season}'
        response = get_response('teamroster', params)
        await interaction.response.send_message(embed=response)

    @app_commands.command(name="playoffbracket")
    async def playoffbracket_command(self, interaction: discord.Interaction):
        response = get_response('playoffbracket', None)
        await interaction.response.send_message(embed=response)

    @app_commands.command(name="teamschedule")
    @app_commands.describe(team="Enter the team you want the schedule for")
    async def schedule_command(self, interaction: discord.Interaction, team: str):
        response = get_response('schedule', team)
        await interaction.response.send_message(embed=response)

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="register")
    async def register_command(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        user_mention = interaction.user.mention
        response = get_response('register', user_id)
        await interaction.response.send_message(content=user_mention, embed=response, ephemeral=True)

    @app_commands.command(name="bonus")
    async def bonus_command(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        user_mention = interaction.user.mention
        response = get_response('bonus', user_id)
        await interaction.response.send_message(content= user_mention, embed=response)
     
    @app_commands.command(name="balance")
    async def balance_command(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        user_mention = interaction.user.mention
        response = get_response('balance', user_id)
        await interaction.response.send_message(content= user_mention, embed=response)

    @app_commands.command(name='placebet')
    @app_commands.describe(moneyline='Bet on which team will win. Use the three letter abbreviation')
    @app_commands.describe(moneyline_wager='Place your wager for your money line bet. Max $500, Min $1')
    @app_commands.describe(puckline='Bet on what the score difference will be. Must be a float of .5')
    @app_commands.describe(puckline_wager='Place your wager for your puck line bet. Max $500, Min $1')
    @app_commands.describe(over_under='Bet on the total score of the game. Must be a float of .5')
    @app_commands.describe(over_under_wager='Place your wager for your over/under bet. Max $500, Min $1')
    async def bet_command(self, interaction: discord.Interaction, moneyline: str, moneyline_wager: float, puckline: Optional[float], puckline_wager: Optional[float], over_under: Optional[float], over_under_wager: Optional[float]):
        user_id = interaction.user.id
        user_mention = interaction.user.mention
        params = f'{user_id}-{moneyline}-{moneyline_wager}-{puckline}-{puckline_wager}-{over_under}-{over_under_wager}'
        response = get_response('placebet', params)
        await interaction.response.send_message(content=user_mention, embed=response)

    @app_commands.command(name='mybets')
    async def mybets_command(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        user_mention = interaction.user.mention
        response = get_response('mybets', user_id)
        await interaction.response.send_message(content=user_mention, embed=response)

    @app_commands.command(name='removebet')
    @app_commands.describe(bet_id='Enter the bet ID to remove')
    async def removebet_command(self, interaction: discord.Interaction, bet_id: int):
        user_id = interaction.user.id
        user_mention = interaction.user.mention
        params = f'{user_id}-{bet_id}'
        response = get_response('removebet', params)
        await interaction.response.send_message(content=user_mention, embed=response)

    @app_commands.command(name='leaderboard')
    async def leaderboard_command(self, interaction: discord.Interaction):
        response = get_response('leaderboard', None)
        await interaction.response.send_message(embed=response)

class Scheduled(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def reset():
        while True:
            now = datetime.datetime.now()
            then = now.replace(hour=0, minute=0, second=0, microsecond=0)
            wait_time = (then - now).total_seconds()
            await asyncio.sleep(wait_time)
            schedules.get_weeks_games()
            schedules.reset_bonus()

async def setup(bot):
    if 'Commands' not in bot.cogs:
        await bot.add_cog(Commands(bot))
        print("Commands Cog Synced")
    if 'Economy' not in bot.cogs:
        await bot.add_cog(Economy(bot))
        print("Economy Cog Synced")
    if 'Scheduled' not in bot.cogs:
        await bot.add_cog(Scheduled(bot))
        print("Scheduled Cog Synced")
    await bot.tree.sync()

def initialize_economy():
    conn = sqlite3.connect('economy.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS Global_Economy (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            balance REAL NOT NULL DEFAULT 0.0,
            bonus INTEGER NOT NULL DEFAULT 0,
            num_bets INTEGER NOT NULL DEFAULT 0,
            num_wins INTEGER NOT NULL DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS Betting_Pool (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            game_type INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            moneyline TEXT NOT NULL,
            puckline REAL,
            over_under REAL,
            moneyline_bet REAL,
            puckline_bet REAL,
            over_under_bet REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES Global_Economy(user_id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS Bet_History (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            game_type INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            moneyline TEXT NOT NULL,
            puckline REAL,
            over_under REAL,
            moneyline_bet REAL,
            puckline_bet REAL,
            over_under_bet REAL,
            total_bet REAL NOT NULL,
            payout REAL,
            moneyline_win BOOLEAN,
            puckline_win BOOLEAN,
            over_under_win BOOLEAN,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES Global_Economy(user_id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS Current_Games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            away_team TEXT NOT NULL,
            home_team TEXT NOT NULL,
            game_type INTEGER NOT NULL,
            start_date DATE NOT NULL,
            start_time TIME NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()
    print("Database Synced")

@bot.event
async def on_ready() -> None:
    initialize_economy()
    await setup(bot)
    print(f'{bot.user} is now running')

def main() -> None:
    bot.run(TOKEN)

if __name__ == '__main__':
    main()
