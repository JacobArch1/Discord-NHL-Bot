import nhl
import datetime
import sqlite3

def reset_bonus():
    conn = sqlite3.connect('./databases/economy.db')
    c = conn.cursor()
    c.execute('UPDATE User_Economy SET bonus = 0')
    conn.commit()
    conn.close()
    log_entry = f'Bonuses have been reset at {datetime.datetime.now().strftime(f'%Y-%m-%d %H:%M:%S')}\n'
    with open('./logs/schedulelog.txt', 'a') as file:
        file.write(log_entry)

def check_game_ended():
    conn = sqlite3.connect('./databases/economy.db')
    c = conn.cursor()
    c.execute('SELECT game_id FROM Current_Games')
    games_list = c.fetchall()
    
    for game in games_list:
        game_id = game[0]
        results = nhl.get_boxscore(game_id)
        
        state = results['gameState']
        game_type = results['gameType']
        if state == 'FINAL' or state == 'OFF':
            cashout(conn, results, game_id, game_type)
            c.execute('DELETE FROM Current_Games WHERE game_id = ?', (game_id,))
            c.execute('SELECT * FROM Current_Games')
            games = c.fetchall()
            if not games:
                get_todays_games(conn)
            conn.commit()
    conn.close()
 
def cashout(conn, results: dict, game_id: int, game_type: int):
    c = conn.cursor()
    c.execute('SELECT * FROM Betting_Pool WHERE game_id == ?', (game_id,))
    bets = c.fetchall()

    multiplier = game_type + .25

    home_score = results['homeTeam']['score']
    away_score = results['awayTeam']['score']

    if home_score > away_score:
        winner = results['homeTeam']['abbrev']
    else:
        winner = results['awayTeam']['abbrev']

    for bet in bets:
        bet_id = bet[0]
        user_id = bet[3]
        team = bet[4] 
        wager = bet[5] 

        c = conn.cursor()
        c.execute('SELECT balance FROM User_Economy WHERE user_id = ?', (user_id,))
        balance_row = c.fetchone()
        balance = balance_row[0]

        bet_won = (team == winner)
        if bet_won:
            balance += wager * multiplier

        c.execute('UPDATE User_Economy SET balance = ? WHERE user_id = ?', (balance, user_id))
        c.execute('DELETE FROM Betting_Pool WHERE id = ?', (bet_id,))
        conn.commit()

def get_todays_games(conn):
    c = conn.cursor()
    c.execute('DELETE FROM Current_Games')

    schedule = nhl.get_current_schedule()
    games_today = schedule['gameWeek'][0]['games']
    for game in games_today:
        game_id = game['id']
        game_type = game['gameType']
        away_team = game['awayTeam']['abbrev']
        home_team = game['homeTeam']['abbrev']

        dt = datetime.datetime.strptime(game['startTimeUTC'], '%Y-%m-%dT%H:%M:%SZ')
        updated_datetime_obj = dt - datetime.timedelta(hours=4)

        est_date = str(updated_datetime_obj.date())
        est_time = str(updated_datetime_obj.time())

        c.execute('SELECT * FROM Current_Games WHERE game_id = ?', (game['id'],))
        if c.fetchone() is None:
            c.execute(
                'INSERT INTO Current_Games (game_id, game_type, away_team, home_team, start_date, start_time) VALUES (?, ?, ?, ?, ?, ?)',
                (game_id, game_type, away_team, home_team, est_date, est_time)
            )
            conn.commit()
    if games_today is None:
        log_entry = f'No games today, Database cleared at {datetime.datetime.now().strftime(f'%Y-%m-%d %H:%M:%S')}\n'
    else:
        log_entry = f'Games for {est_date} have been added to the database at {datetime.datetime.now().strftime(f'%Y-%m-%d %H:%M:%S')}\n'
    with open('./logs/schedulelog.txt', 'a') as file:
        file.write(log_entry)

def fetch_players(season: int):
    conn = sqlite3.connect('./databases/players.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS players (id INTEGER PRIMARY KEY, firstName TEXT, lastName TEXT)''')
    conn.commit()
    for team in nhl.teams:
        results = nhl.get_team_roster_by_season(team, season)
        if 'error' in results:
            continue
        forwards_info = extract_player_info(results.get('forwards', []))
        defensemen_info = extract_player_info(results.get('defensemen', []))
        goalies_info = extract_player_info(results.get('goalies', []))
        all_players_info = forwards_info + defensemen_info + goalies_info
        for player in all_players_info:
            c = conn.cursor()
            c.execute('''SELECT * FROM players WHERE id = ?''', (player['id'],))
            if c.fetchone():
                continue
            else:
                c.execute('''INSERT INTO players (id, firstName, lastName) VALUES (?, ?, ?)''', (player['id'], player['firstName'], player['lastName']))
                conn.commit()
    conn.close()
    log_entry = f'Recent Players Fetched at {datetime.datetime.now().strftime(f'%Y-%m-%d %H:%M:%S')}\n'
    with open('./logs/schedulelog.txt', 'a') as file:
        file.write(log_entry)

def extract_player_info(players):
    extracted_info = []
    for player in players:
        player_info = {
            'id': player['id'],
            'firstName': player['firstName']['default'],
            'lastName': player['lastName']['default']
        }
        extracted_info.append(player_info)
    return extracted_info

def fetch_standings():
    conn = sqlite3.connect('./databases/standings.db')
    c = conn.cursor()
    c.execute("DELETE FROM standings")
    results = nhl.get_standings_for_each_season()
    seasons = results['seasons']
    c = conn.cursor()
    for season in seasons:
        season_id = season.get('id', 0)
        start_date = season.get('standingsStart', '')
        end_date = season.get('standingsEnd', '')
        c.execute('''INSERT INTO standings (id, startDate, endDate) VALUES (?, ?, ?)''', (season_id, start_date, end_date))
        conn.commit()
    conn.close()
    log_entry = f'New Standings Fetched at {datetime.datetime.now().strftime(f'%Y-%m-%d %H:%M:%S')}\n'
    with open('./logs/schedulelog.txt', 'a') as file:
        file.write(log_entry)