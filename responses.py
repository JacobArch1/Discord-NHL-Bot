import sqlite3
import discord
import nhlresponses
from unidecode import unidecode

def get_response(command: str, parameters: str, user_mention: str) -> discord.Embed:
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
            first_name, last_name = parameters.split(' ')
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
            season = parameters.replace('-', '')
            return nhlresponses.get_standings(season)  
        except Exception as e:
            print(e)
            return return_error()
    elif command.startswith('leaders'):
        try:
            position, category = parameters.split(' ')
            return nhlresponses.get_leaders(position, category)
        except Exception as e:
            print(e)
            return return_error()
    elif command.startswith('teamroster'):
        try:
            team, season = parameters.split(' ')
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
    elif command.startswith('register'):
        try:
            conn = sqlite3.connect('economy.db')
            c = conn.cursor()
            user_id = parameters

            c.execute('SELECT * FROM Global_Economy WHERE user_id = ?', (user_id,))
            user = c.fetchone()
            if user:
                embed = discord.Embed(title = "Error", color = discord.Color.red())
                embed.add_field(name="", value="You are already registered.", inline=False)
            else:
                c.execute('INSERT INTO Global_Economy (user_id, balance) VALUES (?, ?)', (user_id, 100))
                embed = discord.Embed(title = "Registered!", color = discord.Color.green())
                embed.add_field(name="", value="You have succesfully registered to the global economy.", inline=False)
                conn.commit()

            conn.close()
            return embed
        except Exception as e:
            print(e)
            return return_error()
    elif command.startswith('bonus'):
        try:
            conn = sqlite3.connect('economy.db')
            c = conn.cursor()
            user_id = parameters

            c.execute('SELECT bonus FROM Global_Economy WHERE user_id = ?', (user_id,))
            result = c.fetchone()

            if result is None:
                embed = discord.Embed(title="Error", color=discord.Color.yellow())
                embed.add_field(name="", value="You are not registered in the economy. Use /register to register.", inline=False)
            elif result[0] == 1:
                embed = discord.Embed(title="Notice", color=discord.Color.yellow())
                embed.add_field(name="", value="Your bonus has already been claimed.", inline=False)
            else:
                bonus_amount = 50
                c.execute('UPDATE Global_Economy SET bonus = 1, balance = balance + ? WHERE user_id = ?', (bonus_amount, user_id))
                conn.commit()

                embed = discord.Embed(title="Claimed!", color=discord.Color.green())
                embed.add_field(name="", value="You claimed your daily $50 bonus.", inline=False)

            conn.close()
            return embed
        except Exception as e:
            print(e)
            return return_error()
    elif command.startswith('balance'):
        try:
            conn = sqlite3.connect('economy.db')
            c = conn.cursor()
            user_id = parameters

            c.execute('SELECT balance FROM Global_Economy WHERE user_id = ?', (user_id,))
            balance = c.fetchone()
            if balance is None:
                embed = discord.Embed(title="Error", color=discord.Color.yellow())
                embed.add_field(name="", value="You are not registered in the economy. Use /register to register.", inline=False)
            else:
                embed = discord.Embed(title="Balance", color=discord.Color.green())
                embed.add_field(name="", value=f"Your Balance is: ${balance[0]}", inline=False)

            conn.close()
            return embed
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
