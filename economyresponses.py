from datetime import date, datetime, timedelta
import datetime
import sqlite3
import discord

def register(user_id: str) -> discord.Embed:
    conn = sqlite3.connect('economy.db')
    c = conn.cursor()
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

def bonus(user_id: str) -> discord.Embed:
    conn = sqlite3.connect('economy.db')
    c = conn.cursor()

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

def balance(user_id: str) -> discord.Embed:
    conn = sqlite3.connect('economy.db')
    c = conn.cursor()
    
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

def placebet(user_id: int, moneyline: str, moneyline_wager: float, puckline: float, puckline_wager: float, over_under: float, over_under_wager: float) -> discord.Embed:
    conn = sqlite3.connect('economy.db')
    c = conn.cursor()
    current_time = datetime.datetime.now().time()
    current_date = str(date.today())
    c.execute('SELECT * FROM Current_Games WHERE home_team = ? OR away_team = ? AND start_date = ?', (moneyline, moneyline, current_date))
    game = c.fetchone()
    if game is None:
        embed = discord.Embed(title="Notice", color=discord.Color.yellow())
        embed.add_field(name="", value="The team you selected is not playing today.", inline=False)
        return embed
    
    game_start_time = datetime.datetime.strptime(game[6], '%H:%M:%S').time()
    one_hour_before_start = (datetime.datetime.combine(datetime.datetime.today(), game_start_time) - timedelta(hours=1)).time()

    if current_time > one_hour_before_start:
        embed = discord.Embed(title="Notice", color=discord.Color.yellow())
        embed.add_field(name="", value="Bets for this game are closed.", inline=False)
        return embed

    c.execute('SELECT balance FROM Global_Economy WHERE user_id = ?', (user_id,))
    balance = c.fetchone()
    if balance is None:
        embed = discord.Embed(title="Error", color=discord.Color.yellow())
        embed.add_field(name="", value="You are not registered in the economy. Use /register to register.", inline=False)
    elif balance[0] < moneyline_wager + (puckline_wager if puckline_wager else 0) + (over_under_wager if over_under_wager else 0):
        embed = discord.Embed(title="Error", color=discord.Color.red())
        embed.add_field(name="", value="You do not have enough balance to place this bet.", inline=False)
    elif moneyline_wager < 1 or moneyline_wager > 500:
        embed = discord.Embed(title="Error", color=discord.Color.red())
        embed.add_field(name="", value="Your money line wager between $1 and $500.", inline=False)
    elif puckline and (puckline_wager < 1 or puckline_wager > 500):
        embed = discord.Embed(title="Error", color=discord.Color.red())
        embed.add_field(name="", value="Your puck line wager between $1 and $500.", inline=False)
    elif over_under and (over_under_wager < 1 or over_under_wager > 500):
        embed = discord.Embed(title="Error", color=discord.Color.red())
        embed.add_field(name="", value="Your over/under wager between $1 and $500.", inline=False)
    else:
        c.execute('SELECT user_id FROM Betting_Pool WHERE user_id = ? AND game_id = ?', (user_id, game[1]))
        user = c.fetchone()
        if user:
            embed = discord.Embed(title="Error", color=discord.Color.yellow())
            embed.add_field(name="", value="You have already placed a bet on this game.", inline=False)
            return embed
        game_id = game[1]
        game_type = game[4]
        c.execute('UPDATE Global_Economy SET balance = balance - ? WHERE user_id = ?', (moneyline_wager, user_id))
        c.execute('INSERT INTO Betting_Pool (game_id, game_type, user_id, moneyline, moneyline_bet, puckline, puckline_bet, over_under, over_under_bet) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                    (game_id, game_type, user_id, moneyline, moneyline_wager, puckline, puckline_wager, over_under, over_under_wager))
        conn.commit()

        embed = discord.Embed(title="Success!", color=discord.Color.green())
        embed.add_field(name="", value="Your bet has been placed.", inline=False)
    return embed

def mybets(user_id: int) -> discord.Embed:
    conn = sqlite3.connect('economy.db')
    c = conn.cursor()

    c.execute('SELECT * FROM Betting_Pool WHERE user_id = ?', (user_id,))
    bets = c.fetchall()
    if not bets:
        embed = discord.Embed(title="Notice", color=discord.Color.yellow())
        embed.add_field(name="", value="You do not have any bets placed.", inline=False)
    else:
        embed = discord.Embed(title="My Bets", color=discord.Color.green())
        for bet in bets:
            embed.add_field(name=f"Bet Id: {bet[0]}", value=f"Moneyline: [{bet[4]}]: ${bet[7]}\nPuckline: [{bet[5]}]: ${bet[8]}\nOver/Under: [{bet[6]}]: ${bet[9]}", inline=False)

    conn.close()
    return embed

def removebet(user_id: int, bet_id: int) -> discord.Embed:
    conn = sqlite3.connect('economy.db')
    c = conn.cursor()

    c.execute('SELECT * FROM Betting_Pool WHERE id = ? AND user_id = ?', (bet_id, user_id))
    bet = c.fetchone()
    if bet is None:
        embed = discord.Embed(title="Error", color=discord.Color.red())
        embed.add_field(name="", value="Could not find bet.", inline=False)
    else:
        refund = bet[7] + bet[8] + bet[9]
        c.execute('UPDATE Global_Economy SET balance = balance + ? WHERE user_id = ?', (refund, user_id))
        c.execute('DELETE FROM Betting_Pool WHERE user_id = ?', (user_id,))
        conn.commit()

        embed = discord.Embed(title="Success!", color=discord.Color.green())
        embed.add_field(name="", value="Your bet has been removed.", inline=False)

    conn.close()
    return embed