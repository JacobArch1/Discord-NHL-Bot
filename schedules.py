import nhl
import datetime
import sqlite3

def reset_bonus():
    conn = sqlite3.connect('economy.db')
    c = conn.cursor()
    c.execute('UPDATE Global_Economy SET bonus = 0')
    conn.commit()
    conn.close()
    log_entry = f'Bonuses have been reset at {datetime.datetime.now().strftime(f'%Y-%m-%d %H:%M:%S')}\n'
    with open('./logs/schedulelog.txt', 'a') as file:
        file.write(log_entry)

def check_game_ended():
    conn = sqlite3.connect('economy.db')
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
        c.execute('SELECT balance FROM Global_Economy WHERE user_id = ?', (user_id,))
        balance_row = c.fetchone()
        balance = balance_row[0]

        bet_won = (team == winner)
        if bet_won:
            balance += wager * multiplier

        c.execute('UPDATE Global_Economy SET balance = ? WHERE user_id = ?', (balance, user_id))
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
    log_entry = f'Games for {est_date} have been added to the database at {datetime.datetime.now().strftime(f'%Y-%m-%d %H:%M:%S')}\n'
    with open('./logs/schedulelog.txt', 'a') as file:
        file.write(log_entry)