import discord
import nhlresponses
import economyresponses
import casinoresponses
import datetime

def get_response(command: str, parameters: list[str]) -> discord.Embed:
    try:
        if command.startswith('info'):
            return nhlresponses.get_info()
        elif command.startswith('playerstats'):
            first_name = parameters[0]
            last_name = parameters[1]
            return nhlresponses.get_player_stats(first_name, last_name)
        elif command.startswith('currentstandings'):
            return nhlresponses.get_standings('')
        elif command.startswith('standings'):
            season = parameters.replace('-', '')
            return nhlresponses.get_standings(season)  
        elif command.startswith('leaders'):
            position = parameters[0]
            category = parameters[1]
            return nhlresponses.get_leaders(position, category)
        elif command.startswith('teamroster'):
            team = parameters[0]
            season = parameters[1].replace('-', '')
            return nhlresponses.get_team_roster(team, season)
        elif command.startswith('playoffbracket'):
            return nhlresponses.get_playoff_bracket()
        elif command.startswith('teamschedule'):
            team = parameters
            return nhlresponses.get_team_schedule(team)
        elif command.startswith('schedule'):
            return nhlresponses.get_league_schedule()
        elif command.startswith('score'):
            team = parameters
            return nhlresponses.get_live_score(team)
        elif command.startswith('gamestory'):
            team = parameters[0]
            date = parameters[1]
            return nhlresponses.get_game_story(team, date)
        elif command.startswith('register'):
            user_id = parameters[0]
            user_name = parameters[1]
            return economyresponses.register(user_id, user_name)
        elif command.startswith('bonus'):
            user_id = parameters[0]
            return economyresponses.bonus(user_id)
        elif command.startswith('balance'):
            user_id = parameters[0]
            return economyresponses.balance(user_id)
        elif command.startswith('placebet'):
            user_id = parameters[0]
            team = parameters[1].upper()
            wager = float(parameters[2])
            return economyresponses.placebet(user_id, team, wager)
        elif command.startswith('mybets'):
            user_id = parameters[0]
            return economyresponses.mybets(user_id)
        elif command.startswith('removebet'):
            user_id = parameters[0]
            bet_id = float(parameters[1])
            return economyresponses.removebet(user_id, bet_id)
        elif command.startswith('leaderboard'):
            return economyresponses.leaderboard()
        elif command.startswith('slots'):
            user_id = parameters[0]
            wager = float(parameters[1])
            return casinoresponses.slots(user_id, wager)
        elif command.startswith('coinflip'):
            user_id = parameters[0]
            side = parameters[1]
            wager = float(parameters[2])
            return casinoresponses.coinflip(user_id, side, wager)
        else:
            return return_error()
    except Exception as e:
        log_error(command, parameters, e)
        return return_error()
    
def log_error(command: str, parameters: str, e: str):
    current_time = datetime.datetime.now()
    timestamp = current_time.strftime(f'%Y-%m-%d %H:%M:%S')
    log_entry = f'Error occured using command {command} with parameters: {parameters}, ERR: {e} | AT: {timestamp}\n'
    with open('./logs/errorlog.txt', 'a') as file:
        file.write(log_entry)

def return_error() -> discord.Embed:
    embed = discord.Embed(title = 'Error', color = discord.Color.red())
    embed.add_field(name='', value='Problem with your request. Check you parameters and retry the command', inline=False)
    embed.set_footer(text='If your parameters are correct theres likely no results for your request. If this is a code issue, the error has been logged.')
    return embed
