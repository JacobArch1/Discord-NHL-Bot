import nhl
import datetime
import sqlite3

def get_weeks_games():
    conn = sqlite3.connect('economy.db')
    c = conn.cursor()
    c.execute('DELETE FROM Current_Games')

    schedule = nhl.get_current_schedule()
    games_today = schedule['gameWeek'][0]['games']
    for game in games_today:
        game_id = game['id']
        game_type = game['gameType']
        away_team = game['awayTeam']['abbrev']
        home_team = game['homeTeam']['abbrev']

        dt = datetime.datetime.strptime(game['startTimeUTC'], "%Y-%m-%dT%H:%M:%SZ")
        updated_datetime_obj = dt - datetime.timedelta(hours=4)

        est_date = str(updated_datetime_obj.date())
        est_time = str(updated_datetime_obj.time())

        c.execute("SELECT * FROM Current_Games WHERE game_id = ?", (game['id'],))
        if c.fetchone() is None:
            c.execute(
                "INSERT INTO Current_Games (game_id, game_type, away_team, home_team, start_date, start_time) VALUES (?, ?, ?, ?, ?, ?)",
                (game_id, game_type, away_team, home_team, est_date, est_time)
            )
            conn.commit()
    conn.close()
    log_entry = f'Games for {est_date} have been added to the database at {datetime.datetime.now().strftime(f'%Y-%m-%d %H:%M:%S')}\n'
    with open('schedulelog.txt', 'a') as file:
        file.write(log_entry)


def reset_bonus():
    conn = sqlite3.connect('economy.db')
    c = conn.cursor()
    c.execute("UPDATE Global_Economy SET bonus = 0")
    conn.commit()
    conn.close()
    log_entry = f'Bonuses have been reset at {datetime.datetime.now().strftime(f'%Y-%m-%d %H:%M:%S')}\n'
    with open('schedulelog.txt', 'a') as file:
        file.write(log_entry)

#Once every minute we should run a command to check if the game is over and if so, get the results and cash out bets.

#At the end of the season we need to run fetchplayers.py and fetch standings.py 