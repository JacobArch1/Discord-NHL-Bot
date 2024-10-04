import discord
import nhlresponses
import economyresponses
import datetime

def get_response(command: str, parameters: str) -> discord.Embed:
    if command.startswith('playerstats'):
        try:
            first_name, last_name = parameters.split(' ')
            return nhlresponses.get_player_stats(first_name, last_name)
        except Exception as e:
            log_error(command, parameters, e)
            return return_error()
    elif command.startswith('currentstandings'):
        try:
            return nhlresponses.get_standings('')
        except Exception as e:
            log_error(command, parameters, e)
            return return_error()
    elif command.startswith('standings'):
        try:
            season = parameters.replace('-', '')
            return nhlresponses.get_standings(season)  
        except Exception as e:
            log_error(command, parameters, e)
            return return_error()
    elif command.startswith('leaders'):
        try:
            position, category = parameters.split(' ')
            return nhlresponses.get_leaders(position, category)
        except Exception as e:
            log_error(command, parameters, e)
            return return_error()
    elif command.startswith('teamroster'):
        try:
            team, season = parameters.split(' ')
            season = season.replace('-', '')
            return nhlresponses.get_team_roster(team, season)
        except Exception as e:
            log_error(command, parameters, e)
            return return_error()
    elif command.startswith('playoffbracket'):
        try:
            return nhlresponses.get_playoff_bracket()
        except Exception as e:
            log_error(command, parameters, e)
            return return_error()
    elif command.startswith('teamschedule'):
        try:
            team = parameters
            return nhlresponses.get_team_schedule(team)
        except Exception as e:
            log_error(command, parameters, e)
            return return_error()
    elif command.startswith('schedule'):
        try:
            return nhlresponses.get_league_schedule()
        except Exception as e:
            log_error(command, parameters, e)
            return return_error()
    elif command.startswith('register'):
        try:
            user_id, user_name = parameters.split(' ')
            return economyresponses.register(user_id, user_name)
        except Exception as e:
            log_error(command, parameters, e)
            return return_error()
    elif command.startswith('bonus'):
        try:
            user_id = parameters
            return economyresponses.bonus(user_id)
        except Exception as e:
            log_error(command, parameters, e)
            return return_error()
    elif command.startswith('balance'):
        try:
            user_id = parameters
            return economyresponses.balance(user_id)
        except Exception as e:
            log_error(command, parameters, e)
            return return_error()
    elif command.startswith('placebet'):
        try:
            user_id, moneyline, moneyline_wager, over_under, greater_or_less, over_under_wager = parameters.split('|')
            moneyline = moneyline.upper()
            moneyline_wager = float(moneyline_wager)
            over_under = float(over_under) if over_under != 'None' else 0.0
            greater_or_less if greater_or_less in ['>', '<'] else None
            over_under_wager = float(over_under_wager) if over_under_wager != 'None' else 0.0
            return economyresponses.placebet(user_id, moneyline, moneyline_wager, over_under, greater_or_less, over_under_wager)
        except Exception as e:
            log_error(command, parameters, e)
            return return_error()
    elif command.startswith('mybets'):
        try:
            user_id = parameters
            return economyresponses.mybets(user_id)
        except Exception as e:
            log_error(command, parameters, e)
            return return_error()
    elif command.startswith('removebet'):
        try:
            user_id, bet_id = parameters.split('-')
            return economyresponses.removebet(user_id, bet_id)
        except Exception as e:
            log_error(command, parameters, e)
            return return_error()
    elif command.startswith('leaderboard'):
        try:
            return economyresponses.leaderboard()
        except Exception as e:
            log_error(command, parameters, e)
            return return_error()
    else: 
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
    embed.set_footer(text='If your parameters are correct theres likely no results for your request. Alternatively, theres an issue with my code.')
    return embed
