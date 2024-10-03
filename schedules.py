import nhl
import datetime
import sqlite3

def get_todays_games():
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
    with open('./logs/schedulelog.txt', 'a') as file:
        file.write(log_entry)


def reset_bonus():
    conn = sqlite3.connect('economy.db')
    c = conn.cursor()
    c.execute("UPDATE Global_Economy SET bonus = 0")
    conn.commit()
    conn.close()
    log_entry = f'Bonuses have been reset at {datetime.datetime.now().strftime(f'%Y-%m-%d %H:%M:%S')}\n'
    with open('./logs/schedulelog.txt', 'a') as file:
        file.write(log_entry)

def check_game_ended():
    conn = sqlite3.connect('economy.db')
    c = conn.cursor()
    c.execute("SELECT game_id FROM Current_Games")
    games_list = c.fetchall()
    
    for game in games_list:
        game_id = game[0]
        results = nhl.get_boxscore(game_id)
        
        state = results["gameState"]
        if state == "FINAL":
            cashout(results, game_id)
    conn.commit()
    conn.close()

def cashout(results: str, game_id: id):
    conn = sqlite3.connect('economy.db')
    c = conn.cursor()
    c.execute("SELECT * FROM Betting_Pool WHERE game_id == ?", (game_id))
    bets = c.fetchall()

    home_score = results["homeTeam"]["score"]
    away_score = results["awayTeam"]["score"]

    if home_score > away_score:
        money_line_winner = results["homeTeam"]["abbrev"]
    else:
        money_line_winner = results["awayTeam"]["abbrev"]
    
    total_score = home_score + away_score

    for bet in bets:
        user_id, moneyline, moneyline_wager, puckline, puckline_wager, over_under, greater_or_less, over_under_wager = bet
        c = conn.cursor()
        c.execute("SELECT balance FROM Global_Economy WHERE user_id = ?", (user_id))
        balance_row = c.fetchone()
        balance = balance_row[0]

        if moneyline_wager > 0:
            moneyline_bet_won = (moneyline == money_line_winner)
            if moneyline_bet_won:
                balance += moneyline_wager
        
        if puckline_wager > 0:
            if puckline > 0:
                puckline_bet_won = (away_score + puckline > home_score)
            else:
                puckline_bet_won = (away_score - abs(puckline) > home_score)
            if puckline_bet_won:
                balance += puckline_wager

        if over_under_wager > 0:
            if greater_or_less == '>':
                over_under_bet_won = (total_score > over_under)
            elif greater_or_less == '<':
                over_under_bet_won = (total_score < over_under)
            if over_under_bet_won:
                balance += over_under_wager

        c.execute("UPDATE Global_Economy SET balance = ? WHERE user_id = ?", (balance, user_id))
    conn.commit()
    conn.close()