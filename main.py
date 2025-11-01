import datetime
import os
import sqlite3
import discord
import nhl
import nhlresponses
import economyresponses
import modresponses
import schedules
from discord.ext import commands, tasks
from dotenv import load_dotenv
from typing import Final, Optional

load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix='$', intents=intents)

class HelpView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=None)
        self.user_id = user_id
    
    @discord.ui.button(label='NHL Commands', style=discord.ButtonStyle.primary)
    async def nhl_button_pressed(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message('You\'re not allowed to interact with this message.', ephemeral=True, delete_after=3)
            return
        
        embed = discord.Embed(
            title='NHL Commands',
            description='''`$playerstats first_name last_name` Get the career stats for a player
            `$standings season*` Get the standings for the current season or specified season
            `$leaders category` Get the player leaders for a specified stat
            `$roster team season*` Get the team roster for the current seasons or specified season
            `$prospects team` Get the current prospect roster for the specified team
            `$playoffs` Get the current playoff carousel
            `$schedule team*` Get todays games or specified a specified team weeks games
            `$score team` Get the live scoreboard for specified team
            `$gamestory team date` Get the gamestory for specified team (YYYY-DD-MM)''',
            color=discord.Color.lighter_gray()
        )
        await interaction.response.defer()
        await interaction.message.edit(embed=embed)
        
    @discord.ui.button(label='Economy Commands', style=discord.ButtonStyle.primary)
    async def economy_button_pressed(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message('You\'re not allowed to interact with this message.', ephemeral=True, delete_after=3)
            return
        
        embed = discord.Embed(
            title='Economy Commands',
            description='''`$register` Register for the economy
            `$bonus` Collect your daily bonus
            `$balance user*` Check your or a specified persons balance
            `$placebet team wager` Place a bet on a team
            `$mybets` See your ongoing bets
            `$removebet team` Remove the bet you placed on a team 
            `$bethistory` See the outcome of your last 10 bets
            `$leaderboard` See the servers 10 richest users''',
            color=discord.Color.lighter_gray()
        )
        await interaction.response.defer()
        await interaction.message.edit(embed=embed)
        
    @discord.ui.button(label='Admin Commands', style=discord.ButtonStyle.primary)
    async def adming_button_pressed(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message('You\'re not allowed to interact with this message.', ephemeral=True, delete_after=3)
            return
        
        embed = discord.Embed(
            title='Admin Commands',
            description='''`$startgame team -u*` Start a game in the channel running this command. Game events will be sent for goals, penalties, etc... -u will ping anyone who opts in for pings
            `$wipeuser user` Wipe a user from the economy. This removes all their data
            `$addmoney user amount` Give a user money
            `$takemoney user amount` Take away money from a user
            `$reseteconomy confirmation` IRREVERSABLE! Confirmation is the server ID to prevent accidental usage. Deletes all data for the server
            `$enableroles` Creates team roles for users
            `$disableroles` Deletes the team roles''',
            color=discord.Color.lighter_gray()
        )
        await interaction.response.defer()
        await interaction.message.edit(embed=embed)

@bot.tree.command(name='help', description='Get command information.')
async def info_command(interaction: discord.Interaction):
    try:
        response = await nhlresponses.get_help()
        await interaction.response.send_message( embed=response, view=HelpView(user_id=interaction.user.id), delete_after=600)
    except Exception as e:
        await interaction.response.send_message(embed=await return_error('HELP', [None], e))

class NHL(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    #--------------PLAYERSTATS--------------
    #first_name (REQUIRED): Ensure proper spelling and special characters where needed
    #last_name (REQUIRED): Ensure proper spelling and special characters where needed

    @commands.command(name='playerstats')
    async def playerstats_command(self, ctx, first_name: str, last_name: str, player_id: Optional[str]):
        try:
            response = await nhlresponses.get_player_stats(first_name, last_name, player_id)
            await ctx.send(embed=response)
        except Exception as e:
            await ctx.send(embed=await return_error('PLAYERSTATS', [None], e))
            
    @playerstats_command.error
    async def playerstats_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            embed=discord.Embed(
                title='playerstats Usage',
                description='$playerstats **first_name** **last_name**\nEnsure proper spelling and special characters\n\nExample: ```$playerstats Connor McDavid```',
                color=discord.Color.lighter_gray()
            )
            await ctx.send(embed=embed)

    #--------------STANDINGS--------------
    #season (OPTIONAL): Format YYYY-YYYY
    
    @commands.command(name='standings')
    async def standings_command(self, ctx, season: Optional[str] = None):
        try:
            if season:
                season = season.replace('-', '')
                response = await nhlresponses.get_standings(season)
            else:
                response = await nhlresponses.get_standings('')
            await ctx.send(embed=response)
        except Exception as e:
            await ctx.send(embed=await return_error('STANDINGS', [None], e))
            
    #--------------LEADERS--------------
    #position (REQUIRED): Either SKATER or GOALIE
    #category (REQUIRED): Category must be spelled properly. /info has list of known categories

    @commands.command(name='leaders')
    async def leaders_command(self, ctx, category: str):
        try:
            response = await nhlresponses.get_leaders(category)
            await ctx.send(embed=response)
        except Exception as e:
            await ctx.send(embed=await return_error('LEADERS', [category], e))
    
    @leaders_command.error
    async def leaders_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            embed=discord.Embed(
                title='leaders Usage',
                description='$leaders **category**\n\nCategories:\nGoalies(wins, shutouts, savePctg)\nSkaters(goals, assists, points, plusMinus)"\n\nExample: ```$leaders goals```',
                color=discord.Color.lighter_gray()
            )
            await ctx.send(embed=embed)
    
    #--------------ROSTER--------------
    #team (REQUIRED): Three letter abbrev for your team
    #season (OPTIONAL): Format YYYY-YYYY
    
    @commands.command(name='roster')
    async def roster_command(self, ctx, team: str, season: Optional[str] = 'current'):
        try:
            response = await nhlresponses.get_roster(team, season.replace('-', ''))
            await ctx.send(embed=response)
        except Exception as e:
            await ctx.send(embed=await return_error('ROSTER', [team, season.replace('-', '')], e))
    
    @roster_command.error
    async def roster_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            embed=discord.Embed(
                title='roster Usage',
                description='$roster **team** **season** [OPT]\nUse three letter abbrev for your team and YYYY-YYYY format for season\n\nExample: ```$roster TBL 2018-2019```',
                color=discord.Color.lighter_gray()
            )
            await ctx.send(embed=embed)
            
    #--------------PROSPECTS--------------
    #team (REQUIRED): Three letter abbrev for your team
    
    @commands.command(name='prospects')
    async def prospects_command(self, ctx, team: str):
        try:
            response = await nhlresponses.get_prospects(team)
            await ctx.send(embed=response)
        except Exception as e:
            await ctx.send(embed=await return_error('PROSPECTS', [team], e))
    
    @roster_command.error
    async def prospects_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            embed=discord.Embed(
                title='prospects Usage',
                description='$prospects **team**\nUse three letter abbrev for your team\n\nExample: ```$prospects VGK```',
                color=discord.Color.lighter_gray()
            )
            await ctx.send(embed=embed)

    #--------------PLAYOFFS--------------
    
    @commands.command(name='playoffs')
    async def playoffs_command(self, ctx):
        try:
            response = await nhlresponses.get_playoffs()
            await ctx.send(embed=response)
        except Exception as e:
            await ctx.send(embed=await return_error('PLAYOFFS', [None], e))

    #--------------SCHEDULE--------------
    #team (OPTIONAL): Three letter abbrev for your team
    
    @commands.command(name='schedule')
    async def schedule_command(self, ctx, team: Optional[str] = None):
        try:
            if team:
                response = await nhlresponses.get_team_schedule(team)
            else:
                response = await nhlresponses.get_league_schedule()
            await ctx.send(embed=response)
        except Exception as e:
            await ctx.send(embed=await return_error('SCHEDULE', [team], e))
    
    @schedule_command.error
    async def schedule_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            embed=discord.Embed(
                title='schedule Usage',
                description='$schedule **team** [OPT]\nLists todays game for the league or weeks game for specified team\n\nExample: ```$schedule CHI```',
                color=discord.Color.lighter_gray()
            )
            await ctx.send(embed=embed)
            
    #--------------SCORE--------------
    #team (REQUIRED): Three letter abbrev for your team

    @commands.command(name='score')
    async def score_command(self, ctx, team: str):
        try:
            response = await nhlresponses.get_live_score(team)
            await ctx.send(embed=response)
        except Exception as e:
            await ctx.send(embed=await return_error('SCORE', [team], e))
            
    @score_command.error
    async def score_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            embed=discord.Embed(
                title='score Usage',
                description='$score **team**\nGet live scoreboard for your team\n\nExample: ```$score MIN```',
                color=discord.Color.lighter_gray()
            )
            await ctx.send(embed=embed)

    #--------------GAMESTORY--------------
    #team (REQUIRED): Three letter abbrev for your team
    #date (OPTIONAL): Format YYYY-MM-DD
    
    @commands.command(name='gamestory')
    async def gamestory_command(self, ctx, team: str, date: Optional[str]):
        try:
            response = await nhlresponses.get_game_story(team, date)
            await ctx.send(embed=response)
        except Exception as e:
            await ctx.send(embed=await return_error('GAMESTORY', [team, date], e))
    
    @gamestory_command.error
    async def gamestory_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            embed=discord.Embed(
                title='gamestory Usage',
                description='$gamestory **team** **date** [OPT]\nUse three letter abbrev for your team and YYYY-MM-DD format for the date\n\nExample: ```$gamestory MTL 2024-12-03```',
                color=discord.Color.lighter_gray()
            )
            await ctx.send(embed=embed)

class Cooldown(commands.CooldownMapping):
    def __init__(self, rate, per):
        cooldown = commands.Cooldown(rate, per)
        super().__init__(cooldown, commands.BucketType.user)

    def _bucket_key(self, ctx):
        return (ctx.guild.id, ctx.author.id)

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}
        self.bonus_cooldown = Cooldown(1, 86400)
        
    #--------------REGISTER--------------

    @commands.command(name='register')
    async def register_command(self, ctx):
        try:
            response = await economyresponses.register(ctx.author.id, ctx.author.name, ctx.guild.id, ctx.author.display_avatar.url)
            await ctx.send(content=ctx.author.mention, embed=response)
        except Exception as e:
            await ctx.send(embed=await return_error('REGISTER', [ctx.author.id, ctx.author.name, ctx.guild.id], e))

    #--------------BONUS--------------  
    #COOLDOWN: 24 Hours
    
    @commands.command(name='bonus')
    async def bonus_command(self, ctx):
        bucket = self.bonus_cooldown.get_bucket(ctx)
        retry_after = bucket.update_rate_limit()
        
        if retry_after:
            return await ctx.send(f'You\'re on cooldown. Try again in {retry_after:.2f} seconds.')
        
        try:
            response = await economyresponses.bonus(ctx.author.id, ctx.guild.id, ctx.author.display_avatar.url)
            await ctx.send(content=ctx.author.mention, embed=response)
        except Exception as e:
            await ctx.send(embed=await return_error('BONUS', [ctx.author.id, ctx.guild.id], e))
            
    #--------------BALANCE--------------
    
    @commands.command(name='balance')
    async def balance_command(self, ctx, user: Optional[str]):
        try:
            response = await economyresponses.balance(ctx.author.id, ctx.guild.id, ctx.author.display_avatar.url, user)
            await ctx.send(content=ctx.author.mention, embed=response)
        except Exception as e:
            await ctx.send(embed=await return_error('BALANCE', [ctx.author.id , ctx.guild.id], e))

    #--------------PLACEBET-------------
    #team (REQUIRED): Three letter abbrev for your team
    #wager (REQUIRED): 
    
    @commands.command(name='placebet')
    async def bet_command(self, ctx, team: str, wager: float):
        try:
            response = await economyresponses.placebet(ctx.author.id, ctx.guild.id, team.upper(), wager, ctx.author.name, ctx.author.display_avatar.url)
            await ctx.send(content=ctx.author.mention, embed=response)
        except Exception as e:
            await ctx.send(embed=await return_error('PLACEBET', [ctx.author.id, ctx.guild.id, team.upper(), wager], e))
    
    @bet_command.error
    async def bet_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            embed=discord.Embed(
                title='placebet Usage',
                description='$placebet **team** **wager**\nUse three letter abbrev for your team. Min wager is $10\n\nExample: ```$placebet SJS 400```',
                color=discord.Color.lighter_gray()
            )
            await ctx.send(embed=embed)

    #--------------MYBETS-------------

    @commands.command(name='mybets')
    async def mybets_command(self, ctx):
        try:
            response = await economyresponses.mybets(ctx.author.id, ctx.guild.id, ctx.author.display_avatar.url)
            await ctx.send(content=ctx.author.mention, embed=response)
        except Exception as e:
            await ctx.send(embed=await return_error('MYBETS', [ctx.author.id, ctx.guild.id], e))

    #--------------REMOVEBET-------------
    #Team: Three letter abrrev for your team to remove
    
    @commands.command(name='removebet')
    async def removebet_command(self, ctx, team: str):
        try:
            response = await economyresponses.removebet(ctx.author.id, ctx.guild.id, team, ctx.author.display_avatar.url)
            await ctx.send(content=ctx.author.mention, embed=response)
        except Exception as e:
            await ctx.send(embed=await return_error('REMOVEBET', [ctx.author.id, ctx.guild.id, team], e))
    
    @removebet_command.error
    async def removebet_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            embed=discord.Embed(
                title='removebet Usage',
                description='$removebet **team**\nUse three letter abbrev for your team.\n\nExample: ```$removebet BOS```',
                color=discord.Color.lighter_gray()
            )
            await ctx.send(embed=embed)
    
    #--------------BETHISTORY-------------
    
    @commands.command(name='bethistory')
    async def bethistory_command(self, ctx):
        try:
            response = await economyresponses.bethistory(ctx.author.id, ctx.guild.id, ctx.author.name, ctx.author.display_avatar.url)
            await ctx.send(content=ctx.author.mention, embed=response)
        except Exception as e:
            await ctx.send(embed=await return_error('BETHISTORY', [ctx.author.id, ctx.guild.id], e))

    #--------------LEADERBOARD-------------

    @commands.command(name='leaderboard')
    async def leaderboard_command(self, ctx):
        try:
            response = await economyresponses.leaderboard(ctx.guild.id)
            await ctx.send(embed=response)
        except Exception as e:
            await ctx.send(embed=await return_error('LEADERBOARD', [ctx.guild.id], e))
    
class Moderator(commands.Cog):
    #--------------STARTGAME-------------
    #Team (REQUIRED): Three letter abbrev for your team
    #-u (OPTIONAL): Create an update role accessed by a reaction
    
    @commands.command(name='startgame')
    @commands.has_permissions(administrator=True)
    async def startgame_command(self, ctx, team: str, update_modifier: Optional[str]):
        try:
            response = await nhlresponses.startgame(team, ctx.channel.id, ctx.guild, update_modifier, ctx)
            await ctx.send(embed=response, delete_after=5)
            await ctx.message.delete()
        except Exception as e:
            await ctx.send(embed=await return_error('STARTGAME', [team], e))
    
    @startgame_command.error
    async def startgame_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            embed=discord.Embed(
                title='startgame Usage',
                description='$startgame **team** **-u** [OPT]\nUse three letter abbrev for your team. -u will create a role that will ping with each update as well as pin this message to the channel\n\nExample: ```$startgame BOS```',
                color=discord.Color.lighter_gray()
            )
            await ctx.send(embed=embed)
    
    #--------------WIPEUSER-------------
    #User (REQUIRED): Discord username or @username
    
    @commands.command(name='wipeuser')
    @commands.has_permissions(administrator=True)
    async def wipeuser_command(self, ctx, user: str):
        try:
            response = await modresponses.wipeuser(ctx.guild.id, user)
            await ctx.send(embed=response)
        except Exception as e:
            await ctx.send(embed=await return_error('WIPEUSER', [ctx.guild.id, user], e))
    
    @wipeuser_command.error
    async def wipeuser_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            embed=discord.Embed(
                title='wipeuser Usage',
                description='$wipeuser **user**',
                color=discord.Color.lighter_gray()
            )
            await ctx.send(embed=embed)
    
    #--------------ADDMONEY-------------
    #User (REQUIRED): Discord username or @username
    
    @commands.command(name='addmoney')
    @commands.has_permissions(administrator=True)
    async def addmoney_command(self, ctx, user: str, amount: int):
        try:
            response = await modresponses.addmoney(ctx.guild.id, user, amount)
            await ctx.send(embed=response)
        except Exception as e:
            await ctx.send(embed=await return_error('ADDMONEY', [ctx.guild.id, user, amount], e))
    
    @addmoney_command.error
    async def addmoney_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            embed=discord.Embed(
                title='addmoney Usage',
                description='$addmoney **user** **amount**',
                color=discord.Color.lighter_gray()
            )
            await ctx.send(embed=embed)
            
    #--------------TAKEMONEY-------------
    #User (REQUIRED): Discord username or @username
    
    @commands.command(name='takemoney')
    @commands.has_permissions(administrator=True)
    async def takemoney_command(self, ctx, user: str, amount: int):
        try:
            response = await modresponses.takemoney(ctx.guild.id, user, amount)
            await ctx.send(embed=response)
        except Exception as e:
            await ctx.send(embed=await return_error('TAKEMONEY', [ctx.guild.id, user, amount], e))
    
    @takemoney_command.error
    async def takemoney_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            embed=discord.Embed(
                title='takemoney Usage',
                description='$takemoney **user** **amount**',
                color=discord.Color.lighter_gray()
            )
            await ctx.send(embed=embed)

    #--------------WIPEECONOMY-------------
    #Confirmation (REQUIRED): Guild ID to make sure no accidental usage
    
    @commands.command(name='reseteconomy')
    @commands.has_permissions(administrator=True)
    async def reseteconomy_command(self, ctx, confirmation: int):
        try:
            response = await modresponses.reseteconomy(ctx.guild.id, confirmation) 
            await ctx.send(embed=response)
        except Exception as e:
            await ctx.send(embed=await return_error('RESETECONOMY', [ctx.guild.id], e))
    
    @reseteconomy_command.error
    async def reseteconomy_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            embed = discord.Embed(
                title='Error',
                description='You don\'t have permission for this.', 
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            embed=discord.Embed(
                title='Warning',
                description='Run again with this guilds id\n```$reseteconomy guild_id```\n**WARNING**: This action is irreversable',
                color=discord.Color.lighter_gray()
            )
            await ctx.send(embed=embed)
    
    #--------------ENABLEROLES-------------
    
    @commands.command(name='enableroles')
    @commands.has_permissions(administrator=True)
    async def enableroles_command(self, ctx):
        try:
            response = await modresponses.enableroles(ctx.guild)
            await ctx.send(embed=response)
        except Exception as e:
            await ctx.send(embed=await return_error('ENABLEROLES', [ctx.guild.id], e))

    #--------------DISABLEROLES-------------

    @commands.command(name='disableroles')
    @commands.has_permissions(administrator=True)
    async def disableroles_command(self, ctx):
        try:
            response = await modresponses.disableroles(ctx.guild)
            await ctx.send(embed=response)
        except Exception as e:
            await ctx.send(embed=await return_error('DISABLEROLES', [ctx.guild.id], e))
  
    #--------------PERMISSIONERROR-------------
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title='Error',
                description='You don\'t have permission for this.', 
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

class Scheduled(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_tables.start()
        self.update_games.start()
        
    def cog_unload(self):
        self.update_tables.cancel()
        self.update_games.cancel()

    @tasks.loop(hours=24)
    async def update_tables(self):
        now = datetime.datetime.now()
        season = 0
        if now.month < 7:
            season = int(str(now.year-1) + str(now.year))
        else:
            season = int(str(now.year) + str(now.year+1))
        await schedules.fetch_players(season)
        await schedules.fetch_standings()

    @update_tables.before_loop
    async def before_update_tables(self):
        await self.bot.wait_until_ready()

    @tasks.loop(seconds=10)
    async def update_games(self):
        await schedules.update_games(self.bot)
        
    @update_games.before_loop
    async def before_update_games(self):
        await self.bot.wait_until_ready()


async def return_error(command: str, parameters: list[str], e: str) -> discord.Embed:
    nhl.log_data (f'Error occured using command {command} with parameters: {parameters}, ERR: {e}')
    embed = discord.Embed(title = 'Error', color = discord.Color.red())
    embed.add_field(name='', value=f'Check parameters and try again', inline=False)
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
async def on_guild_join(guild):
    try:
        economyresponses.added_to_guild(guild.id)
        nhl.log_data(f'I was just added to {guild.name}. ID:{guild.id}')
    except Exception as e:
        nhl.log_data(f'Error with adding GUILD to DB: {guild.name} ID:{guild.id} | ERR: {e}')
    
@bot.event
async def on_guild_remove(guild):
    try:
        economyresponses.removed_from_guild(guild.id)
        nhl.log_data(f'I was just removed from {guild.name}. ID:{guild.id}')
    except Exception as e:
        nhl.log_data(f'Error with removing GUILD from DB: {guild.name} ID:{guild.id} | ERR: {e}')
    
@bot.event
async def on_guild_channel_delete(channel):
    try:
        economyresponses.channel_deleted(channel.id)
        nhl.log_data(f'Channel was deleted {channel.name}. ID:{channel.id}')
    except Exception as e:
        nhl.log_data(f'Error with removing CHANNEL from DB: {channel.name} ID:{channel.id} | ERR: {e}')
    
def main() -> None:
    bot.run(TOKEN)

if __name__ == '__main__':
    main()