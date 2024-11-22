import requests
import datetime

BASE_URL = 'https://api-web.nhle.com'

teams = {'ANA' : 'Anaheim Ducks',  
         'BOS' : 'Boston Bruins', 
         'BUF' : 'Buffalo Sabres', 
         'CAR' : 'Carolina Hurricanes', 
         'CBJ' : 'Columbus Blue Jackets', 
         'CGY' : 'Calgary Flames', 
         'CHI' : 'Chicago Blackhawks', 
         'COL' : 'Colorado Avalanche', 
         'DAL' : 'Dallas Stars', 
         'DET' : 'Detroit Red Wings', 
         'EDM' : 'Edmonton Oilers', 
         'FLA' : 'Florida Panthers', 
         'LAK' : 'Los Angeles Kings', 
         'MIN' : 'Minnesota Wild', 
         'MTL' : 'Montreal Canadiens', 
         'NJD' : 'New Jersey Devils', 
         'NSH' : 'Nashville Predators', 
         'NYI' : 'New York Islanders', 
         'NYR' : 'New York Rangers', 
         'OTT' : 'Ottawa Senators', 
         'PHI' : 'Philadelphia Flyers', 
         'PIT' : 'Pittsburgh Penguins',  
         'SEA' : 'Seattle Kraken',  
         'SJS' : 'San Jose Sharks', 
         'STL' : 'St. Louis Blues', 
         'TBL' : 'Tampa Bay Lightning', 
         'TOR' : 'Toronto Maple Leafs', 
         'VAN' : 'Vancouver Canucks', 
         'VGK' : 'Vegas Golden Knights', 
         'WPG' : 'Winnipeg Jets', 
         'WSH' : 'Washington Capitals',
         'UTA' : 'Utah Hockey Club'}

teams_colors = {'ANA': '#F47A38', 
                'ARI': '#8C2633', 
                'BOS': '#FFB81C', 
                'BUF': '#003087', 
                'CAR': '#CE1126', 
                'CBJ': '#002654', 
                'CGY': '#D2001C', 
                'CHI': '#CF0A2C', 
                'COL': '#6F263D', 
                'DAL': '#006847', 
                'DET': '#ce1126', 
                'EDM': '#041E42', 
                'FLA': '#041E42', 
                'LAK': '#111111', 
                'MIN': '#A6192E', 
                'MTL': '#AF1E2D', 
                'NJD': '#CE1126', 
                'NSH': '#FFB81C', 
                'NYI': '#00539b', 
                'NYR': '#0038A8', 
                'OTT': '#000000', 
                'PHI': '#F74902', 
                'PIT': '#000000', 
                'SEA': '#001628', 
                'SJS': '#006D75', 
                'STL': '#002F87', 
                'TBL': '#002868', 
                'TOR': '#00205b',
                'VAN': '#00205B', 
                'VGK': '#B4975A', 
                'WPG': '#041E42', 
                'WSH': '#041E42',
                'UTA': '#71AFE5'}

team_emojis = {'ANA': 1309592481020510208,
               'BOS': 1309592803143323771,
               'BUF': 1309592477254025288,
               'CAR': 1309592474003570708,
               'CBJ': 1309592466789498993,
               'CGY': 1309592772117921885,
               'CHI': 1309592737603125261,
               'COL': 1309592469410807809,
               'DAL': 1309592703696240721,
               'DET': 1309592463861743667,
               'EDM': 1309592680354807889,
               'FLA': 1309592460342591528,
               'LAK': 1309592457159118848,
               'MIN': 1309592645902794862,
               'MTL': 1309592454214844466,
               'NJD': 1309592446551724152,
               'NSH': 1309592453145165945,
               'NYI': 1309592445125922948,
               'NYR': 1309592441434669197,
               'OTT': 1309592439543042059,
               'PHI': 1309592438385414184,
               'PIT': 1309592436565217331,
               'SJS': 1309592434724044871,
               'STL': 1309592433054580836,
               'TBL': 1309592430617559110,
               'TOR': 1309592428176605315,
               'UTA': 1309592413748199526,
               'VAN': 1309592421599936632,
               'VGK': 1309592420010299493,
               'WPG': 1309592416054939658,
               'WSH': 1309592417237860402}

#  -------------------- API ENDPOINTS  -------------------- #
def connect_endpoint(endpoint: str):
    url = BASE_URL + endpoint
    response = requests.get(url)
    if response.status_code == 200:
        return response.json(), None
    else:
        log_data(f'REQUEST ERROR Using URL:{url} Response:{response.status_code}')
        return None, response.status_code

def get_data(category: str, params: dict):
    endpoint = category.format(**params)
    data, error_code = connect_endpoint(endpoint)
    if error_code:
        return {'error': f'Request failed with status code {error_code}'}
    return data

def log_data(message: str):
    current_time = datetime.datetime.now()
    timestamp = current_time.strftime(f'%Y-%m-%d %H:%M:%S')
    with open('./logs/log.txt', 'a') as file:
        file.write(f'{message} | AT {timestamp}\n')

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

def get_playoff_bracket(year: str):
    return get_data('/v1/playoff-bracket/{year}',
        {'year': year})

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
