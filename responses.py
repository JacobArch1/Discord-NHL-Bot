import discord
import nhlresponses
from unidecode import unidecode

def get_response(command: str, user_message: str) -> str:
    if command.startswith('help'):
        embed = discord.Embed(title = "Command List", color = discord.Color(0x6203fc))
        embed.add_field(name="playerstats", value="```Parameters: [firstName] [lastName] \nDisplays player stats```", inline=False)
        embed.add_field(name="currentstandings", value="```Show standings for the current season```", inline=False)
        embed.add_field(name="standings", value="```Parameters: [YYYY-YYYY] \nShow standings from given year (end of season)```", inline=False)
        embed.add_field(name="leaders", value="```Parameters: [position] [category] \nShow the top 5 leaders in given category```", inline=False)
        return embed
    elif command.startswith('glossary'):
        embed = discord.Embed(title = "Glossary", color = discord.Color(0x6203fc))
        embed.add_field(name="Skater Stats", value=f"""```\nGP - Games Played\nG - Goals\nP - Points\n+/- - Plus Minus\nPIM - Penalty Minutes
PPG - Power Play Goals\nPPP - Power Play Points\nSHG - Short Handed Goals\nSHP - Short Handed Points\nTOI/G - Time On Ice per Game
GWG - Game Winning Goals\nOTG - Overtime Goals\nS - Shots\nS% - Shooting Pctg\nFO% - Faceoff Win Pctg```""", inline=False)
        embed.add_field(name="Goalie Stats", value=f"""```\nGP - Games Played\nGS - Games Started\nW - Wins\nL - Losses\nOT - Over Time Losses
SA - Shots Against\nGA - Goals Against\nSO - Shutouts\nA - Assists\nGAA - Goals Against Avg\nSV% - Save Pctg```""", inline=False)
        embed.add_field(name="Skater Leader Categories", value="""```\nGoals\nAssists\nPoints```""", inline=False)
        embed.add_field(name="Goalie Leader Categories", value="""```\nWins\nSavePctg\nShutouts```""", inline=False)
        return embed
    elif command.startswith('playerstats'):
        try:
            first_name, last_name = user_message.split(' ')
            first_name = unidecode(first_name)
            last_name = unidecode(last_name)
            return nhlresponses.get_player_stats(first_name, last_name)
        except Exception as e:
            print(e)
            return return_error()
    elif command.startswith('currentstandings'):
        try:
            return nhlresponses.get_standings('')
        except Exception as e:
            print(e)
            return return_error()
    elif command.startswith('standings'):
        try:
            user_message = user_message.replace('-', '')
            return nhlresponses.get_standings(user_message)  
        except Exception as e:
            print(e)
            return return_error()
    elif command.startswith('leaders'):
        try:
            position, category = user_message.split(' ')
            return nhlresponses.get_leaders(position, category)
        except Exception as e:
            print(e)
            return return_error()
    elif command.startswith('teamroster'):
        try:
            team, season = user_message.split(' ')
            season = season.replace('-', '')
            return nhlresponses.get_team_roster(team, season)
        except Exception as e:
            print(e)
            return return_error()
    elif command.startswith('playoffbracket'):
        try:
            return nhlresponses.get_playoff_bracket()
        except Exception as e:
            print(e)
            return return_error()
    else: 
        print(e)
        return return_error()
    
def return_error() -> discord.Embed:
    embed = discord.Embed(title = "Error", color = discord.Color.red())
    embed.add_field(name="", value="Problem with your request. Check you parameters and retry the command", inline=False)
    embed.set_footer(value="If your parameters are correct theres likely no results for your request. Alternatively, theres and issue with my code.")
    return embed
