import csv
import discord
import requests
import datetime

BASE_URL = 'https://api-web.nhle.com'

#Current Lineup
teams = {'ANA', 'ARI', 'BOS', 'BUF', 'CAR', 'CBJ', 'CGY', 'CHI', 'COL', 'DAL', 'DET', 'EDM', 
         'FLA', 'LAK', 'MIN', 'MTL', 'NJD', 'NSH', 'NYI', 'NYR', 'OTT', 'PHI', 'PIT', 'SEA',  
         'SJS', 'STL', 'TBL', 'TOR', 'VAN', 'VGK', 'WPG', 'WSH'}

#No longer in the league
oldteams = {'AFM', 'ATL', 'BRK', 'CGS', 'CLE', 'CLR', 'DCG', 'DFL', 'HAM', 'HFD', 'KCS', 'MMR', 
            'MNS', 'MWN', 'NYA', 'OAK', 'PHX', 'PIR', 'QBD', 'QUA', 'QUE', 'SEN', 'SLE', 'TAN', 
            'TSP', 'UTA', 'WIN', }

#Team Colors
teams_colors = { 'ANA': '#F47A38', 'ARI': '#8C2633', 'BOS': '#FFB81C', 'BUF': '#003087', 'CAR': '#CE1126', 
                'CBJ': '#002654', 'CGY': '#D2001C', 'CHI': '#CF0A2C', 'COL': '#6F263D', 'DAL': '#006847', 
                'DET': '#ce1126', 'EDM': '#041E42', 'FLA': '#041E42', 'LAK': '#111111', 'MIN': '#A6192E', 
                'MTL': '#AF1E2D','NJD': '#CE1126', 'NSH': '#FFB81C', 'NYI': '#00539b', 'NYR': '#0038A8', 
                'OTT': '#000000', 'PHI': '#F74902', 'PIT': '#000000', 'SEA': '#001628','SJS': '#006D75', 
                'STL': '#002F87', 'TBL': '#002868', 'TOR': '#00205b', 'VAN': '#00205B', 'VGK': '#B4975A', 
                'WPG': '#041E42', 'WSH': '#041E42'}

def get_player_id(first_name: str, last_name: str) -> int:
    players = []
    with open('playerslist/players.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if first_name in row[1] and last_name in row[2]:
                return row[0]
            players.append(row)

    filtered_players = [row for row in players if last_name in row[2]]
    
    embed = discord.Embed(color=discord.Color.lighter_grey())
    embed.add_field(name = '', value='No player found...', inline=False)
    if filtered_players:
        players_names = [f'{row[1]} {row[2]}' for row in filtered_players]
        embed.add_field(name='Did you mean one of these players?', value='\n'.join(players_names), inline=False)
    return embed

def get_standings_end(season: str) -> str:
    with open('standingslist/standings.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if season in row[0]:
                return row[2]

def get_team_abbr(team: str) -> str:
    with open('teamslist/teams.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if team in row[1]:
                return row[0]

def get_team_name(team: str) -> str:
    with open('teamslist/teams.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if team in row[1]:
                return row[0]

def get_current_season() -> int:
    last_row = None
    with open('standingslist/standings.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            last_row = row
    if last_row:
        return int(last_row[0])

#  -------------------- API ENDPOINTS  -------------------- #
def connect_endpoint(endpoint: str):
    url = BASE_URL + endpoint
    response = requests.get(url)
    log_data(url, response.status_code)
    if response.status_code == 200:
        return response.json(), None
    else:
        return None, response.status_code

def get_data(category: str, params: dict):
    endpoint = category.format(**params)
    data, error_code = connect_endpoint(endpoint)
    if error_code:
        return {'error': f'Request failed with status code {error_code}'}
    return data

def log_data(url: str, status_code: int):
    current_time = datetime.datetime.now()
    timestamp = current_time.strftime(f'%Y-%m-%d %H:%M:%S')
    log_entry = f'[{timestamp}] {url} Response:{status_code}\n'
    with open('log.txt', 'a') as file:
        file.write(log_entry)

# ----- PLAYER INFORMATION ----- #
def get_game_log(player: int, season: int, game_type: int):
    return get_data('/v1/player/{player}/game-log/{season}/{game_type}', 
        {'player': player, 'season': season, 'game_type': game_type})

def get_specific_player_info(player: int):
    return get_data('/v1/player/{player}/landing', 
        {'player': player})

def get_game_log_as_of_now(player: int):
    return get_data('/v1/player/{player}/game-log/now', 
        {'player': player})

#SKATERS
def get_current_skaters_stats_leaders(categories: str, limit: int):
    return get_data('/v1/skater-stats-leaders/current?categories={categories}&limit={limit}', 
        {'categories': categories, 'limit': limit})

def get_skater_stats_leaders_for_specific_season(season: int, game_type: int, categories: str, limit: int):
    return get_data('/v1/skater-stats-leaders/{season}/{game_type}?categories={categories}&limit={limit}', 
        {'season': season, 'game_type': game_type, 'categories': categories, 'limit': limit})

#GOALIES
def get_current_goalie_stats_leaders(categories: str, limit: int):
    return get_data('/v1/goalie-stats-leaders/current?categories={categories}&limit={limit}', 
        {'categories': categories, 'limit': limit})

def get_goalie_stats_leaders_by_season(season: int, game_type: int, categories: str, limit: int):
    return get_data('/v1/goalie-stats-leaders/{season}/{game_type}?categories={categories}&limit={limit}', 
        {'season': season, 'game_type': game_type, 'categories': categories, 'limit': limit})

#PLAYER SPOTLIGHT
def get_players_in_spotlight():
    return get_data('/v1/player-spotlight', 
        {})

# ----- TEAM INFORMATION ----- #
def get_current_standings():
    return get_data('/v1/standings/now', 
        {})

def get_standings_by_date(date: str):
    return get_data('/v1/standings/{date}', 
        {'date': date})

def get_standings_for_each_season():
    return get_data('/v1/standings-season', 
        {})

#STATS
def get_club_stats(team: str):
    return get_data('/v1/club-stats/{team}/now', 
        {'team': team})

def get_club_stats_by_season(team: str, season: int, game_type: int):
    return get_data('/v1/club-stats/{team}/{season}/{game_type}', 
        {'team': team, 'season': season, 'game_type': game_type})

def get_team_scoreboard(team: str):
    return get_data('/v1/scoreboard/{team}/now', 
        {'team': team})

#ROSTER
def get_current_team_roster(team: str):
    return get_data('/v1/roster/{team}/current', 
        {'team': team})

def get_team_roster_by_season(team: str, season: int):
    return get_data('/v1/roster/{team}/{season}', 
        {'team': team, 'season': season})

def get_team_prospects(team: str):
    return get_data('/v1/prospects/{team}', 
        {'team': team})

#SCHEDULE
def get_team_schedule_season_now(team: str):
    return get_data('/v1/club-schedule-season/{team}/now', 
        {'team': team})

def get_team_schedule_season(team: str, season: int):
    return get_data('/v1/club-schedule-season/{team}/{season}', 
        {'team': team, 'season': season})

def get_team_schedule_month(team: str):
    return get_data('/v1/club-schedule/{team}/month/now', 
        {'team': team})

def get_team_schedule_month_now(team: str, month: str):
    return get_data('/v1/club-schedule/{team}/month/{month}', 
        {'team': team, 'month': month})

def get_week_schedule_now(team: str):
    return get_data('/v1/club-schedule/{team}/week/now', 
        {'team': team})

def get_week_schedule(team: str, date: str):
    return get_data('/v1/club-schedule/{team}/week/{date}', 
        {'team': team, 'date': date})

# ----- LEAGUE SCHEDULE ----- #
def get_current_schedule():
    return get_data('/v1/schedule/now', 
        {})

def get_schedule_by_date(date: str):
    return get_data('/v1/schedule/{date}', 
        {'date': date})

#SCHEDULE CALENDAR
def get_current_schedule_calendar():
    return get_data('/v1/schedule-calendar/now', 
        {})

def get_schedule_calendar_by_date(date: str):
    return get_data('/v1/schedule-calendar/{date}', 
        {'date': date})

# ----- GAME INFORMATION ----- #
def get_current_scores():
    return get_data('/v1/score/now', 
        {})

def get_daily_scores_by_date(date: str):
    return get_data('/v1/score/{date}', 
        {'date': date})

def get_current_scoreboard():
    return get_data('/v1/scoreboard/now', 
        {})

#WHERE TO WATCH
def get_streams():
    return get_data('/v1/where-to-watch', 
        {})

#GAME EVENTS
def get_play_by_play(game_id: int):
    return get_data('/v1/gamecenter/{game_id}/play-by-play', 
        {'game_id': game_id})

def get_landing(game_id: int):
    return get_data('/v1/gamecenter/{game_id}/landing', 
        {'game_id': game_id})

def get_boxscore(game_id: int):
    return get_data('/v1/gamecenter/{game_id}/boxscore', 
        {'game_id': game_id})

def get_game_story(game_id: int):
    return get_data('/v1/wsc/game-story/{game_id}', 
        {'game_id': game_id})

#NETWORK
def get_tv_schedule():
    return get_data('/v1/network/tv-schedule/now', 
        {})

def get_tv_schedule_by_date(date: str):
    return get_data('/v1/network/tv-schedule/{date}',
        {'date': date})

# ----- PLAYOFF INFORMATION ----- #
def get_playoff_carousel(season: int):
    return get_data('/v1/playoff-series/carousel/{season}/', 
        {'season': season})

#SCHEDULE
def get_series_schedule(season: int, series_letter: str):
    return get_data('/v1/schedule/playoff-series/{season}/{series_letter}', 
        {'season': season, 'series_letter': series_letter})

# ----- DRAFTS ----- #
def get_draft_rankings():
    return get_data('/v1/draft/rankings/now', 
        {})

def get_draft_rankings_by_date(season: int, prospect_category: int):
    return get_data('/v1/draft/rankings/{season}/{prospect_category}', 
        {'season': season, 'prospect_category': prospect_category})