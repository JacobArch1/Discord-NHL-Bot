from datetime import date, datetime, timedelta
import datetime
import sqlite3
import discord

def register(user_id: str, user_name: str, guild_id: str) -> discord.Embed:
    conn = sqlite3.connect('./databases/economy.db')
    c = conn.cursor()
    c.execute('SELECT * FROM User_Economy WHERE guild_id = ? AND user_id = ?', (guild_id, user_id,))
    user = c.fetchone()
    if user:
        embed = discord.Embed(
            title = 'Error', 
            color = discord.Color.red()
        )
        embed.add_field(
            name='', 
            value='You are already registered.', 
            inline=False
        )
    else:
        c.execute('INSERT INTO User_Economy (guild_id, user_id, balance, user_name) VALUES (?, ?, ?, ?)', (guild_id, user_id, 100, user_name,))
        embed = discord.Embed(
            title = 'Registered!', 
            color = discord.Color.green()
        )
        embed.add_field(
            name='', 
            value='You have succesfully registered.', 
            inline=False
        )
        conn.commit()

    conn.close()
    return embed

def bonus(user_id: str, guild_id: str) -> discord.Embed:
    conn = sqlite3.connect('./databases/economy.db')
    c = conn.cursor()

    c.execute('SELECT bonus FROM User_Economy WHERE guild_id = ? AND user_id = ?', (guild_id, user_id,))
    result = c.fetchone()

    if result is None:
        embed = discord.Embed(
            title='Error', 
            color=discord.Color.yellow()
        )
        embed.add_field(
            name='', 
            value='You are not registered in the economy. Use /register to register.', 
            inline=False
        )
    elif result[0] == 1:
        embed = discord.Embed(
            title='Notice', 
            color=discord.Color.yellow
        )
        embed.add_field(
            name='', 
            value='Your bonus has already been claimed.', 
            inline=False
        )
    else:
        bonus_amount = 500
        c.execute('UPDATE User_Economy SET bonus = 1, balance = balance + ? WHERE guild_id = ? AND user_id = ?', (bonus_amount, guild_id, user_id,))
        conn.commit()

        embed = discord.Embed(
            title='Claimed!', 
            color=discord.Color.green()
        )
        embed.add_field(
            name='', 
            value=f'You claimed your daily ${bonus_amount} bonus.', 
            inline=False
        )

    conn.close()
    return embed

def balance(user_id: str, guild_id: str) -> discord.Embed:
    conn = sqlite3.connect('./databases/economy.db')
    c = conn.cursor()
    
    c.execute('SELECT balance FROM User_Economy WHERE guild_id = ? AND user_id = ?', (guild_id, user_id,))
    balance = c.fetchone()
    if balance is None:
        embed = discord.Embed(
            title='Error', 
            color=discord.Color.yellow()
        )
        embed.add_field(
            name='', 
            value='You are not registered in the economy. Use /register to register.', 
            inline=False
        )
    else:
        embed = discord.Embed(
            title='Balance', 
            color=discord.Color.green()
        )
        embed.add_field(
            name='', 
            value=f'Your Balance is: ${balance[0]}', 
            inline=False
        )

    conn.close()
    return embed

def placebet(user_id: int, guild_id: str, team: str, wager: float) -> discord.Embed:
    conn = sqlite3.connect('./databases/economy.db')
    c = conn.cursor()
    current_time = datetime.datetime.now().time()
    current_date = str(date.today())
    c.execute('SELECT * FROM Current_Games WHERE home_team = ? OR away_team = ? AND start_date = ?', (team, team, current_date))
    game = c.fetchone()
    if game is None:
        embed = discord.Embed(
            title='Notice', 
            color=discord.Color.yellow()
        )
        embed.add_field(
            name='', 
            value='The team you selected is not playing today.', 
            inline=False
        )
        return embed
    game_start_time = datetime.datetime.strptime(game[6], '%H:%M:%S').time()
    close_time = (datetime.datetime.combine(datetime.datetime.today(), game_start_time) - timedelta(minutes=10)).time()
    if current_time > close_time:
        embed = discord.Embed(
            title='Notice', 
            color=discord.Color.yellow()
        )
        embed.add_field(
            name='', 
            value='Bets for this game are closed.', 
            inline=False
        )
        return embed
    c.execute('SELECT balance FROM User_Economy WHERE guild_id = ? AND user_id = ?', (guild_id, user_id,))
    balance = c.fetchone()
    if balance is None:
        embed = discord.Embed(
            title='Error', 
            color=discord.Color.yellow()
        )
        embed.add_field(
            name='', 
            value='You are not registered in the economy. Use /register to register.', 
            inline=False
        )
    elif balance[0] < wager:
        embed = discord.Embed(title='Error', color=discord.Color.red())
        embed.add_field(
            name='', 
            value='You do not have enough balance to place this bet.', 
            inline=False
        )
    elif wager < 1 or wager > 500:
        embed = discord.Embed(
            title='Error', 
            color=discord.Color.red()
        )
        embed.add_field(
            name='', 
            value='Your wager must be between $1 and $500.', 
            inline=False
        )
    else:
        c.execute('SELECT user_id FROM Betting_Pool WHERE guild_id = ? AND user_id = ? AND game_id = ?', (guild_id, user_id, game[1],))
        user = c.fetchone()
        if user:
            embed = discord.Embed(
                title='Error', 
                color=discord.Color.yellow()
            )
            embed.add_field(
                name='', 
                value='You have already placed a bet on this game.', 
                inline=False
            )
            return embed
        game_id = game[1]
        game_type = game[4]
        c.execute('UPDATE User_Economy SET balance = balance - ? WHERE guild_id = ? AND user_id = ?', (wager, guild_id, user_id,))
        c.execute('INSERT INTO Betting_Pool (game_id, guild_id, game_type, user_id, team, wager) VALUES (?, ?, ?, ?, ?, ?)', (game_id, guild_id, game_type, user_id, team, wager,))
        conn.commit()
        embed = discord.Embed(
            title='Success!', 
            color=discord.Color.green()
        )
        embed.add_field(
            name='', 
            value='Your bet has been placed.', 
            inline=False
        )
    return embed

def mybets(user_id: int, guild_id: str) -> discord.Embed:
    conn = sqlite3.connect('./databases/economy.db')
    c = conn.cursor()

    c.execute('SELECT * FROM Betting_Pool WHERE guild_id = ? AND user_id = ?', (guild_id, user_id,))
    bets = c.fetchall()
    if not bets:
        embed = discord.Embed(
            title='Notice', 
            color=discord.Color.yellow()
        )
        embed.add_field(
            name='', 
            value='You do not have any bets placed.', 
            inline=False
        )
    else:
        embed = discord.Embed(
            title='My Bets', 
            color=discord.Color.green()
        )
        for bet in bets:
            embed.add_field(
                name=f'Bet Id: {bet[0]}', 
                value=f'Moneyline: {bet[5]}: ${bet[6]}', 
                inline=False
            )

    conn.close()
    return embed

def removebet(user_id: int, guild_id: str, bet_id: int) -> discord.Embed:
    conn = sqlite3.connect('./databases/economy.db')
    c = conn.cursor()

    c.execute('SELECT * FROM Betting_Pool WHERE id = ? AND guild_id = ? AND user_id = ?', (bet_id, guild_id, user_id,))
    bet = c.fetchone()
    game_id = bet[1]

    c.execute('SELECT * FROM Current_Games WHERE game_id = ?', (game_id,))
    game = c.fetchone()
    
    game_start_time = datetime.datetime.strptime(game[6], '%H:%M:%S').time()
    close_time = (datetime.datetime.combine(datetime.datetime.today(), game_start_time) - timedelta(minutes=10)).time()
    current_time = datetime.datetime.now().time()

    if bet is None:
        embed = discord.Embed(
            title='Error', 
            color=discord.Color.red()
        )
        embed.add_field(
            name='', 
            value='Could not find bet.', 
            inline=False
        )
    elif current_time > close_time:
        embed = discord.Embed(
            title='Notice', 
            color=discord.Color.yellow()
        )
        embed.add_field(
            name='', 
            value='Betting for this game is closed. Cannot remove bet.'
        )
    else:
        refund = bet[6]
        c.execute('UPDATE User_Economy SET balance = balance + ? WHERE guild_id = ? AND user_id = ?', (refund, guild_id, user_id,))
        c.execute('DELETE FROM Betting_Pool WHERE guild_id = ? AND user_id = ?', (guild_id, user_id,))
        conn.commit()

        embed = discord.Embed(
            title='Success!', 
            color=discord.Color.green()
        )
        embed.add_field(
            name='', 
            value='Your bet has been removed.', 
            inline=False
        )

    conn.close()
    return embed

def leaderboard(guild_id: str) -> discord.Embed:
    conn = sqlite3.connect('./databases/economy.db')
    c = conn.cursor()
    c.execute('SELECT user_name, balance FROM User_Economy WHERE guild_id = ? ORDER BY balance DESC', (guild_id,))
    leaderboard = c.fetchall()
    embed = discord.Embed(
        title='Leaderboard', 
        color=discord.Color.green()
    )
    table = [
            '```',
            f'{'Rank':<5}{'User':<25}{'Balance':>5}\n',
        ]
    for i in range(min(10, len(leaderboard))):
        user_name, balance = leaderboard[i]
        table.append(f'{i + 1:<5}{user_name:<25}{balance:>5}\n')
    table.append('```')
    embed.add_field(
        name='', 
        value=''.join(table), 
        inline=False
    )
    conn.close()
    return embed