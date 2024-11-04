import datetime
import os
import sqlite3
import discord
import asyncio
import nhlresponses
import economyresponses
import schedules
import time
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from typing import Final, Optional

load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.live_channels = {}

    @app_commands.command(name='info', description='Get command information.')
    async def info_command(self, interaction: discord.Interaction):
        try:
            response = nhlresponses.get_info()
            await interaction.response.send_message(content=interaction.user.mention, embed=response, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(embed=await return_error('INFO', [None], e))

    @app_commands.command(name='playerstats', description='Get statistics for a player. Player records span back to 1917')
    @app_commands.describe(first_name='Enter first name. Use proper capitalization and special characters where needed')
    @app_commands.describe(last_name='Enter last name. Use proper capitalization and special characters where needed')
    async def playerstats_command(self, interaction: discord.Interaction, first_name: str, last_name: str):
        try:
            response = nhlresponses.get_player_stats(first_name, last_name)
            await interaction.response.send_message(embed=response)
        except Exception as e:
            await interaction.response.send_message(embed=await return_error('PLAYERSTATS', [None], e))

    @app_commands.command(name='standings', description='Get the current standings for each division.')
    @app_commands.describe(season='Get standings by specific year. Format: YYYY-YYYY')
    async def standings_command(self, interaction: discord.Interaction, season: Optional[str] = None):
        try:
            if season:
                season = season.replace('-', '')
                response = nhlresponses.get_standings(season)
            else:
                response = nhlresponses.get_standings('')
            await interaction.response.send_message(embed=response)
        except Exception as e:
            await interaction.response.send_message(embed=await return_error('STANDINGS', [None], e))

    @app_commands.command(name='leaders', description='Get the leaders in a specific category.')
    @app_commands.describe(position='Skater or goalie.')
    @app_commands.describe(category='Use /info for list of categories.')
    async def leaders_command(self, interaction: discord.Interaction, position: str, category: str):
        try:
            response = nhlresponses.get_leaders(position, category)
            await interaction.response.send_message(embed=response)
        except Exception as e:
            await interaction.response.send_message(embed=await return_error('LEADERS', [position, category], e))
     
    @app_commands.command(name='teamroster', description='Get the roster for a team.')
    @app_commands.describe(team='Enter the three letter abbreviation.')
    @app_commands.describe(season='Get team roster by specific year. Format: YYYY-YYYY')
    async def teamroster_command(self, interaction: discord.Interaction, team: str, season: Optional[str] = 'current'):
        try:
            response = nhlresponses.get_team_roster(team, season.replace('-', ''))
            await interaction.response.send_message(embed=response)
        except Exception as e:
            await interaction.response.send_message(embed=await return_error('TEAMROSTER', [team, season.replace('-', '')], e))

    @app_commands.command(name='playoffbracket', description='Get the current playoff ')
    async def playoffbracket_command(self, interaction: discord.Interaction):
        try:
            response = nhlresponses.get_playoff_bracket()
            await interaction.response.send_message(embed=response)
        except Exception as e:
            await interaction.response.send_message(embed=await return_error('PLAYOFFBRACKET', [None], e))

    @app_commands.command(name='schedule', description='Get todays games for all teams.')
    @app_commands.describe(team='Enter the three letter abbreviation. Gets this weeks games for that team.')
    async def schedule_command(self, interaction: discord.Interaction, team: Optional[str] = None):
        try:
            if team:
                response = nhlresponses.get_team_schedule(team)
            else:
                response = nhlresponses.get_league_schedule()
            await interaction.response.send_message(embed=response)
        except Exception as e:
            await interaction.response.send_message(embed=await return_error('SCHEDULE', [team], e))

    @app_commands.command(name='score', description='Get the live score right now.')
    @app_commands.describe(team='Enter the three letter abbreviation.')
    async def score_command(self, interaction: discord.Interaction, team: str):
        try:
            response = nhlresponses.get_live_score(team)
            await interaction.response.send_message(embed=response)
        except Exception as e:
            await interaction.response.send_message(embed=await return_error('SCORE', [team], e))

    @app_commands.command(name='gamestory', description='Get scoring info and team stats for a specific game.')
    @app_commands.describe(team='Enter the three letter abbreviation.')
    @app_commands.describe(date='Enter the date for this game YYYY-MM-DD. Records span back about a week.')
    async def gamestory_command(self, interaction: discord.Interaction, team: str, date: str):
        try:
            response = nhlresponses.get_game_story(team, date)
            await interaction.response.send_message(embed=response)
        except Exception as e:
            await interaction.response.send_message(embed=await return_error('GAMESTORY', [team, date], e))

    @app_commands.command(name='liveupdates')
    @app_commands.describe(team='Enter the team you want live updates for. This will send updates in whatever channel your typing this command.')
    @app_commands.checks.has_permissions(administrator=True)
    async def liveupdates_command(self, interaction: discord.Interaction, team: str):
        try:
            response = nhlresponses.get_live_updates(team, interaction.channel.id)
            await interaction.response.send_message(embed=response)
        except Exception as e:
            await interaction.response.send_message(embed=await return_error('LIVEUPDATES', [team], e))
    
    @liveupdates_command.error
    async def return_error(self, interaction: discord.Interaction, error):
        embed = discord.Embed(
            title='Error', 
            color=discord.Color.red()
        )
        if isinstance(error, app_commands.MissingPermissions):
            embed.add_field(
                name='', 
                value='You do not have permission for this.'
            )
        else:
            embed.add_field(
                name='', 
                value='Check your parameters. If your parameters are fine there is likely a code issue.'
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}

    @app_commands.command(name='register', description='Sign up for this servers economy.')
    async def register_command(self, interaction: discord.Interaction):
        try:
            response = economyresponses.register(interaction.user.id, interaction.user.name, interaction.guild.id)
            await interaction.response.send_message(content=interaction.user.mention, embed=response, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(embed=await return_error('REGISTER', [interaction.user.id, interaction.user.name, interaction.guild.id], e))

    @app_commands.command(name='bonus', description='Get your daily $500 bonus.')
    async def bonus_command(self, interaction: discord.Interaction):
        try:
            if await self.check_cooldown(interaction, interaction.user.id, interaction.guild.id, True):
                return
            response = economyresponses.bonus(interaction.user.id, interaction.guild.id)
            await interaction.response.send_message(content=interaction.user.mention, embed=response)
        except Exception as e:
            await interaction.response.send_message(embed=await return_error('BONUS', [interaction.user.id, interaction.guild.id], e))
    
    @app_commands.command(name='balance', description='Check your current balance.')
    async def balance_command(self, interaction: discord.Interaction):
        try:
            response = economyresponses.balance(interaction.user.id, interaction.guild.id)
            await interaction.response.send_message(content=interaction.user.mention, embed=response)
        except Exception as e:
            await interaction.response.send_message(embed=await return_error('BALANCE', [interaction.user.id , interaction.guild.id], e))

    @app_commands.command(name='placebet', description='Bet on which team will win their game today. Bets won\'t be accepted 10 minutes before puckdrop.')
    @app_commands.describe(team='Bet on which team will win. Use the three letter abbreviation.')
    @app_commands.describe(wager='Place your wager. Minimum $1')
    async def bet_command(self, interaction: discord.Interaction, team: str, wager: float):
        try:
            response = economyresponses.placebet(interaction.user.id, interaction.guild.id, team.upper(), wager)
            await interaction.response.send_message(content=interaction.user.mention, embed=response)
        except Exception as e:
            await interaction.response.send_message(embed=await return_error('PLACEBET', [interaction.user.id, interaction.guild.id, team.upper(), wager], e))

    @app_commands.command(name='mybets', description='Check your current bets.')
    async def mybets_command(self, interaction: discord.Interaction):
        try:
            response = economyresponses.mybets(interaction.user.id, interaction.guild.id)
            await interaction.response.send_message(content=interaction.user.mention, embed=response)
        except Exception as e:
            await interaction.response.send_message(embed=await return_error('MYBETS', [interaction.user.id, interaction.guild.id], e))

    @app_commands.command(name='removebet', description='Remove a bet. Use \'mybets\' to get your bet ID.')
    @app_commands.describe(bet_id='Enter the bet ID to remove')
    async def removebet_command(self, interaction: discord.Interaction, bet_id: int):
        try:
            response = economyresponses.removebet(interaction.user.id, interaction.guild.id, bet_id)
            await interaction.response.send_message(content=interaction.user.mention, embed=response)
        except Exception as e:
            await interaction.response.send_message(embed=await return_error('REMOVEBET', [interaction.user.id, interaction.guild.id, bet_id], e))

    @app_commands.command(name='leaderboard', description='See which server members have the most money.')
    async def leaderboard_command(self, interaction: discord.Interaction):
        try:
            response = economyresponses.leaderboard(interaction.guild.id)
            await interaction.response.send_message(embed=response)
        except Exception as e:
            await interaction.response.send_message(embed=await return_error('LEADERBOARD', [interaction.guild.id], e))
    
    @app_commands.command(name='slots', description='Gamble all your money away. :D')
    @app_commands.describe(wager='Enter your wager, Minimum $100 Bet.')
    async def slots(self, interaction:discord.Interaction, wager: float):
        try:
            if await self.check_cooldown(interaction, interaction.user.id, interaction.guild.id, False):
                return
            response = economyresponses.slots(interaction.user.id, interaction.guild.id, wager)
            await interaction.response.send_message(embed=response)
        except Exception as e:
            await interaction.response.send_message(embed=await return_error('SLOTS', [wager, interaction.guild.id], e))

    @app_commands.command(name='coinflip', description='Gamble some of your money away. :)')
    @app_commands.describe(side='H or T')
    @app_commands.describe(wager='Enter your wager, Minimum $100 Bet.')
    async def coinflip(self, interaction:discord.Interaction, side: str, wager: float):
        try:
            if await self.check_cooldown(interaction, interaction.user.id, interaction.guild.id, False):
                return
            response = economyresponses.coinflip(interaction.user.id, interaction.guild.id, side, wager)
            await interaction.response.send_message(embed=response)
        except Exception as e:
            await interaction.response.send_message(embed=await return_error('COINFLIP', [side, wager, interaction.guild.id], e))
    
    async def check_cooldown(self, interaction:discord.Interaction, user_id: int, guild_id: int, bonus: bool):
        current_time = time.time()
        key = [user_id, guild_id]
        if key in self.cooldowns and current_time < self.cooldowns[key]:
            remaining_time = round(self.cooldowns[key] - current_time, 1)
            embed = discord.Embed(title='You\'re on cooldown.', description=f'Please wait {remaining_time} seconds', color=discord.Color.dark_gray())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return True
        if bonus:
            self.cooldowns[key] = current_time + 86400
        else:
            self.cooldowns[key] = current_time + 5
        return False

class Scheduled(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.check_game_over())
        self.bot.loop.create_task(self.update_tables())

    async def update_tables(self):
        while True:
            now = datetime.datetime.now()
            then = now.replace(year=(now.year+1), month=8, day=30, hour=11, minute=59, second=59, microsecond=59)
            wait_time = (then - now).total_seconds()
            await asyncio.sleep(wait_time)
            season = int(str(now.year) + str(now.year+1))
            schedules.fetch_players(season)
            schedules.fetch_standings()

    async def check_game_over(self):
        while True:
            schedules.check_game_ended()
            await asyncio.sleep(1 * 60)

async def return_error(command: str, parameters: list[str], e: str) -> discord.Embed:
    current_time = datetime.datetime.now()
    timestamp = current_time.strftime(f'%Y-%m-%d %H:%M:%S')
    log_entry = f'Error occured using command {command} with parameters: {parameters}, ERR: {e} | AT: {timestamp}\n'
    with open('./logs/log.txt', 'a') as file:
        file.write(log_entry)
    embed = discord.Embed(title = 'Error', color = discord.Color.red())
    embed.add_field(name='', value='Problem with your request. Check you parameters and retry the command', inline=False)
    embed.set_footer(text='If your parameters are correct theres likely no results for your request. If this is a code issue, the error has been logged.')
    return embed

async def setup(bot):
    if 'Commands' not in bot.cogs:
        await bot.add_cog(Commands(bot))
    if 'Economy' not in bot.cogs:
        await bot.add_cog(Economy(bot))
    if 'Scheduled' not in bot.cogs:
        await bot.add_cog(Scheduled(bot))
    print('Cogs Synced')
    await bot.tree.sync()

async def initialize_economy():
    conn = sqlite3.connect('./databases/main.db')
    c = conn.cursor()
    
    with open('./databases/tables.sql', 'r') as f:
        script = f.read()
    c.executescript(script)

    conn.commit()
    conn.close()
    print('Database Synced')

@bot.event
async def on_ready() -> None:
    await initialize_economy()
    await setup(bot)
    print(f'{bot.user} is now running')

def main() -> None:
    bot.run(TOKEN)

if __name__ == '__main__':
    main()