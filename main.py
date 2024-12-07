import datetime
import os
import sqlite3
import discord
import asyncio
import nhl
import nhlresponses
import economyresponses
import modresponses
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
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents)

class NHL(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.live_channels = {}

    @app_commands.command(name='info', description='Get command information.')
    async def info_command(self, interaction: discord.Interaction):
        try:
            response = nhlresponses.get_info()
            await interaction.response.send_message(content=interaction.user.mention, embed=response, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(embed=await return_error('INFO', [None], e), ephemeral=True)

    @app_commands.command(name='playerstats', description='Get statistics for a player. Records span back to 1917')
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

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}

    @app_commands.command(name='register', description='Sign up for this servers economy.')
    async def register_command(self, interaction: discord.Interaction):
        try:
            response = economyresponses.register(interaction.user.id, interaction.user.name, interaction.guild.id, interaction.user.display_avatar.url)
            await interaction.response.send_message(content=interaction.user.mention, embed=response, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(embed=await return_error('REGISTER', [interaction.user.id, interaction.user.name, interaction.guild.id], e), ephemeral=True)

    @app_commands.command(name='bonus', description='Get your daily $1,000 bonus.')
    async def bonus_command(self, interaction: discord.Interaction):
        try:
            if await self.check_cooldown(interaction, interaction.user.id, interaction.guild.id, 'bonus'):
                return
            response = economyresponses.bonus(interaction.user.id, interaction.guild.id, interaction.user.display_avatar.url)
            await interaction.response.send_message(content=interaction.user.mention, embed=response)
        except Exception as e:
            await interaction.response.send_message(embed=await return_error('BONUS', [interaction.user.id, interaction.guild.id], e))
    
    @app_commands.command(name='beg', description='Earn between $50 to $100')
    async def beg_command(self, interaction: discord.Interaction):
        try:
            if await self.check_cooldown(interaction, interaction.user.id, interaction.guild.id, 'beg'):
                return
            response = economyresponses.beg(interaction.user.id, interaction.guild.id, interaction.user.display_avatar.url)
            await interaction.response.send_message(content=interaction.user.mention, embed=response)
        except Exception as e:
            await interaction.response.send_message(embed=await return_error('BEG', [interaction.user.id, interaction.guild.id], e))
    
    @app_commands.command(name='balance', description='Check your current balance.')
    async def balance_command(self, interaction: discord.Interaction):
        try:
            response = economyresponses.balance(interaction.user.id, interaction.guild.id, interaction.user.display_avatar.url)
            await interaction.response.send_message(content=interaction.user.mention, embed=response)
        except Exception as e:
            await interaction.response.send_message(embed=await return_error('BALANCE', [interaction.user.id , interaction.guild.id], e))

    @app_commands.command(name='placebet', description='Bet on which team will win their game today. Bets won\'t be accepted 10 minutes before puckdrop.')
    @app_commands.describe(team='Bet on which team will win. Use the three letter abbreviation.')
    @app_commands.describe(wager='Place your wager. Minimum $10')
    async def bet_command(self, interaction: discord.Interaction, team: str, wager: float):
        try:
            response = economyresponses.placebet(interaction.user.id, interaction.guild.id, team.upper(), wager, interaction.user.name, interaction.user.display_avatar.url)
            await interaction.response.send_message(content=interaction.user.mention, embed=response)
        except Exception as e:
            await interaction.response.send_message(embed=await return_error('PLACEBET', [interaction.user.id, interaction.guild.id, team.upper(), wager], e))

    @app_commands.command(name='mybets', description='Check your current bets.')
    async def mybets_command(self, interaction: discord.Interaction):
        try:
            response = economyresponses.mybets(interaction.user.id, interaction.guild.id, interaction.user.display_avatar.url)
            await interaction.response.send_message(content=interaction.user.mention, embed=response)
        except Exception as e:
            await interaction.response.send_message(embed=await return_error('MYBETS', [interaction.user.id, interaction.guild.id], e))

    @app_commands.command(name='removebet', description='Remove a bet. Use \'mybets\' to get your bet ID.')
    @app_commands.describe(team='Enter which team you want to remove the bet for.')
    async def removebet_command(self, interaction: discord.Interaction, team: str):
        try:
            response = economyresponses.removebet(interaction.user.id, interaction.guild.id, team, interaction.user.display_avatar.url)
            await interaction.response.send_message(content=interaction.user.mention, embed=response)
        except Exception as e:
            await interaction.response.send_message(embed=await return_error('REMOVEBET', [interaction.user.id, interaction.guild.id, team], e))
    
    @app_commands.command(name='bethistory', description='See the last 10 bets you placed.')
    async def bethistory_command(self, interaction: discord.Interaction):
        try:
            response = economyresponses.bethistory(interaction.user.id, interaction.guild.id, interaction.user.name, interaction.user.display_avatar.url)
            await interaction.response.send_message(content=interaction.user.mention, embed=response)
        except Exception as e:
            await interaction.response.send_message(embed=await return_error('BETHISTORY', [interaction.user.id, interaction.guild.id], e))

    @app_commands.command(name='leaderboard', description='See which server members have the most money.')
    async def leaderboard_command(self, interaction: discord.Interaction):
        try:
            response = economyresponses.leaderboard(interaction.guild.id)
            await interaction.response.send_message(embed=response)
        except Exception as e:
            await interaction.response.send_message(embed=await return_error('LEADERBOARD', [interaction.guild.id], e))
    
    @app_commands.command(name='slots', description='Gamble all your money away. :D')
    @app_commands.describe(wager='Enter your wager, Minimum $10 Bet.')
    async def slots(self, interaction:discord.Interaction, wager: float):
        try:
            if await self.check_cooldown(interaction, interaction.user.id, interaction.guild.id, 'slots'):
                return
            response = economyresponses.slots(interaction.user.id, interaction.guild.id, wager, interaction.user.name, interaction.user.display_avatar.url)
            await interaction.response.send_message(embed=response)
        except Exception as e:
            await interaction.response.send_message(embed=await return_error('SLOTS', [wager, interaction.guild.id], e))

    @app_commands.command(name='coinflip', description='Gamble some of your money away. :)')
    @app_commands.describe(side='Heads or Tails')
    async def coinflip(self, interaction:discord.Interaction, side: str):
        try:
            if await self.check_cooldown(interaction, interaction.user.id, interaction.guild.id, 'coinflip'):
                return
            response = economyresponses.coinflip(interaction.user.id, interaction.guild.id, side, interaction.user.name, interaction.user.display_avatar.url)
            await interaction.response.send_message(embed=response)
        except Exception as e:
            await interaction.response.send_message(embed=await return_error('COINFLIP', [side, interaction.guild.id], e))
        
    @app_commands.command(name='roulette', description='Gamble every dime you own. :D')
    @app_commands.describe(color='Red or Black.')
    @app_commands.describe(color_wager='1 to 1 Payout.')
    @app_commands.describe(number='Pick a number 1-36.')
    @app_commands.describe(number_wager='11 to 1 Payout.')
    async def roulette(self, interaction:discord.Interaction, color: Optional[str], color_wager: Optional[float], number: Optional[int], number_wager: Optional[float]):
        try:
            if await self.check_cooldown(interaction, interaction.user.id, interaction.guild.id, 'roulette'):
                return
            response = economyresponses.roulette(interaction.user.id, interaction.guild.id, color, color_wager, number, number_wager, interaction.user.name, interaction.user.display_avatar.url)
            await interaction.response.send_message(embed=response)
        except Exception as e:
            await interaction.response.send_message(embed=await return_error('ROULETTE', [color, color_wager, number, number_wager, interaction.guild.id], e))
    
    @app_commands.command(name='jackpot', description='Put money into the jackpot machine for a chance to win it.')
    @app_commands.describe(amount='Min $1, Max $100')
    async def jackpot(self, interaction:discord.Interaction, amount: int):
        try:
            if await self.check_cooldown(interaction, interaction.user.id, interaction.guild.id, 'jackpot'):
                return
            response = economyresponses.jackpot(interaction.guild.id, interaction.user.id, amount, interaction.user.name, interaction.user.display_avatar.url)
            await interaction.response.send_message(embed=response)
        except Exception as e:
            await interaction.response.send_message(embed=await return_error('JACKPOT', [interaction.guild.id, amount], e))
            
    @app_commands.command(name='checkjackpot', description='See information on this servers jackpot.')
    async def checkjackpot(self, interaction:discord.Interaction):
        try:
            response = economyresponses.checkjackpot(interaction.guild.name, interaction.guild.id)
            await interaction.response.send_message(embed=response)
        except Exception as e:
            await interaction.response.send_message(embed=await return_error('CHECKJACKPOT', [interaction.guild.id], e))
    
    async def check_cooldown(self, interaction:discord.Interaction, user_id: int, guild_id: int, command: str):
        current_time = time.time()
        key = (user_id, guild_id, command)
        if key in self.cooldowns and current_time < self.cooldowns[key]:
            remaining_time = round(self.cooldowns[key] - current_time, 1)
            if remaining_time > 60:
                remaining_time = round(remaining_time / 60, 1)
                unit = 'minutes'
            else:
                unit = 'seconds'
            embed = discord.Embed(title='You\'re on cooldown.', description=f'Please wait {remaining_time} {unit}', color=discord.Color(0xFFFFFF))
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return True
        if command == 'bonus':
            self.cooldowns[key] = current_time + 86400
        elif command == 'jackpot':
            self.cooldowns[key] = current_time + 1800
        elif command == 'beg':
            self.cooldowns[key] = current_time + 120
        else:
            self.cooldowns[key] = current_time + 5
        return False
    
class Moderator(commands.Cog):
    @app_commands.command(name='startgame')
    @app_commands.describe(team='Enter the team you want live updates for. This will send updates in whatever channel your typing this command.')
    @app_commands.checks.has_permissions(administrator=True)
    async def startgame_command(self, interaction: discord.Interaction, team: str):
        try:
            response = nhlresponses.startgame(team, interaction.channel.id, interaction.guild.id)
            await interaction.response.send_message(embed=response)
        except Exception as e:
            await interaction.response.send_message(embed=await return_error('STARTGAME', [team], e))
    
    @app_commands.command(name='wipeuser', description='Remove a user from the economy.')
    @app_commands.describe(username='Enter the discord username to wipe.')
    @app_commands.checks.has_permissions(administrator=True)
    async def wipeuser_command(self, interaction: discord.Interaction, username: str):
        try:
            response = modresponses.wipeuser(interaction.guild.id, username)
            await interaction.response.send_message(embed=response, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(embed=await return_error('WIPEUSER', [interaction.guild.id, username], e), ephemeral=True)
    
    @app_commands.command(name='addmoney', description='Give a user money.')
    @app_commands.describe(username='Enter the discord username to give money.')
    @app_commands.describe(amount='Enter the amount to give.')
    @app_commands.checks.has_permissions(administrator=True)
    async def addmoney_command(self, interaction: discord.Interaction, username: str, amount: int):
        try:
            response = modresponses.addmoney(interaction.guild.id, username, amount)
            await interaction.response.send_message(embed=response, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(embed=await return_error('ADDMONEY', [interaction.guild.id, username, amount], e), ephemeral=True)
    
    @app_commands.command(name='takemoney', description='Take away a users money.')
    @app_commands.describe(username='Enter the discord username to take money.')
    @app_commands.describe(amount='Enter the amount to take.')
    @app_commands.checks.has_permissions(administrator=True)
    async def takemoney_command(self, interaction: discord.Interaction, username: str, amount: int):
        try:
            response = modresponses.takemoney(interaction.guild.id, username, amount)
            await interaction.response.send_message(embed=response, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(embed=await return_error('TAKEMONEY', [interaction.guild.id, username, amount], e), ephemeral=True)
    
    @app_commands.command(name='reseteconomy', description='WARNING: THIS WILL WIPE ALL DATA FOR YOUR USERS. NO TAKEBACKSIES!')
    @app_commands.checks.has_permissions(administrator=True)
    async def reseteconomy_command(self, interaction: discord.Interaction):
        try:
            response = modresponses.reseteconomy(interaction.guild.id) 
            await interaction.response.send_message(embed=response, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(embed=await return_error('RESETECONOMY', [interaction.guild.id], e), ephemeral=True)
            
    @app_commands.command(name='addroles', description='Create team roles for this server')
    @app_commands.describe()
    async def addroles_command(self, interaction: discord.Interaction):
        try:
            response = modresponses.addrolls(interaction.guild.id)
            await interaction.response.send_message(embed=response, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(embed=await return_error('ADDROLES', [interaction.guild.id], e), ephemeral=True)
    
    @addroles_command.error
    @startgame_command.error
    @wipeuser_command.error
    @addmoney_command.error
    @takemoney_command.error
    @reseteconomy_command.error
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

class Scheduled(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.update_games())
        self.bot.loop.create_task(self.update_tables())

    async def update_tables(self):
        while True:
            now = datetime.datetime.now()
            season = int(str(now.year) + str(now.year+1))
            await schedules.fetch_players(season)
            await schedules.fetch_standings()
            await asyncio.sleep(86400)

    async def update_games(self):
        while True:
            await schedules.update_games(self.bot)
            await asyncio.sleep(5)

async def return_error(command: str, parameters: list[str], e: str) -> discord.Embed:
    nhl.log_data (f'Error occured using command {command} with parameters: {parameters}, ERR: {e}')
    embed = discord.Embed(title = 'Error', color = discord.Color.red())
    embed.add_field(name='', value='Problem with your request. Check you parameters and retry the command', inline=False)
    embed.set_footer(text='If your parameters are correct theres likely no results for your request. If this is a code issue, the error has been logged.')
    return embed

async def setup(bot):
    if 'NHL' not in bot.cogs:
        await bot.add_cog(NHL(bot))
    if 'Economy' not in bot.cogs:
        await bot.add_cog(Economy(bot))
    if 'Moderator' not in bot.cogs:
        await bot.add_cog(Moderator(bot))
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

@bot.event
async def on_guild_remove(guild):
    nhl.log_data(f'I was just removed from {guild.name}. ID:{guild.id}')

def main() -> None:
    bot.run(TOKEN)

if __name__ == '__main__':
    main()