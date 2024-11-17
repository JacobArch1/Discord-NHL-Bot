from datetime import date, datetime, timedelta
import datetime
import sqlite3
import discord
import random

def register(user_id: str, user_name: str, guild_id: str) -> discord.Embed:
    conn = sqlite3.connect('./databases/main.db')
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
    conn = sqlite3.connect('./databases/main.db')
    c = conn.cursor()
    c.execute('SELECT user_name FROM User_Economy WHERE guild_id = ? AND user_id = ?', (guild_id, user_id,))
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
    else:
        bonus_amount = 500
        c.execute('UPDATE User_Economy SET balance = balance + ? WHERE guild_id = ? AND user_id = ?', (bonus_amount, guild_id, user_id,))
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
    conn = sqlite3.connect('./databases/main.db')
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
    conn = sqlite3.connect('./databases/main.db')
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
    results = check_db(conn, user_id, guild_id, wager, 10)
    if isinstance(results, discord.Embed):
        return results
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
    conn = sqlite3.connect('./databases/main.db')
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
    conn = sqlite3.connect('./databases/main.db')
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
    conn = sqlite3.connect('./databases/main.db')
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

def slots(user_id: int, guild_id: int, wager: float) -> discord.Embed:
    conn = sqlite3.connect('./databases/main.db')
    results = check_db(conn, user_id, guild_id, wager, 10)
    if isinstance(results, discord.Embed):
        return results

    symbols = ['🍒', '🍋', '🍊', '🍎', '💎', '💰']
    weights = [0.25, 0.10, 0.03 , 0.014, 0.005, 0.001]

    spin = random.choices(symbols, weights=weights, k=3)

    if spin[0] == spin[1] == spin[2]:
        if spin[0] == '🍒':
            embed = discord.Embed(
                title='Congrats!', 
                color=discord.Color.green()
            )
            payout = wager * 4
        elif spin[0] == '🍋':
            embed = discord.Embed(
                title='Congrats!', 
                color=discord.Color.yellow()
            )
            payout = wager * 10
        elif spin[0] == '🍊':
            embed = discord.Embed(
                title='Congrats!', 
                color=discord.Color.orange()
            )
            payout = wager * 30
        elif spin[0] == '🍎':
            embed = discord.Embed(
                title='Congrats!', 
                color=discord.Color.red()
            )
            payout = wager * 65
        elif spin[0] == '💎':
            embed = discord.Embed(
                title='JACKPOT!!!!!', 
                color=discord.Color.teal()
            )
            payout = wager * 250
        elif spin[0] == '💰':
            embed = discord.Embed(
                title='SUPER JACKPOT!!!!!', 
                color=discord.Color.gold()
            )
            payout = wager * 1000
    elif spin[0] == spin[1] or spin[1] == spin[2] or spin[0] == spin[2]:
        if (spin[0] == '💎' and (spin[1] == '💎' or spin[2] == '💎')) or (spin[1] == '💎' and spin[2] == '💎'):
            embed = discord.Embed(
                title='Close...', 
                color=discord.Color(int('#BCF6EA'.lstrip('#'), 16))
            )
            payout = wager * 50
        elif (spin[0] == '💰' and (spin[1] == '💰' or spin[2] == '💰')) or (spin[1] == '💰' and spin[2] == '💰'):
            embed = discord.Embed(
                title='Close...', 
                color=discord.Color(int('#FAEDB7'.lstrip('#'), 16))
            )
            payout = wager * 100
        else:
            embed = discord.Embed(
                title='Close...', 
                color=discord.Color(int('#FFFFFF'.lstrip('#'), 16))
            )
            payout = wager * 0.5
    else:
        embed = discord.Embed(
            title='Try Again!', 
            color=discord.Color(int('#000000'.lstrip('#'), 16))
        )
        payout = 0

    c = conn.cursor()
    c.execute('UPDATE User_Economy SET balance = balance + ? WHERE guild_id = ? AND user_id = ?', (round(payout,2), guild_id, user_id))
    conn.commit()
    conn.close()
    embed.add_field(
        name='', 
        value=f'{spin[0]}--{spin[1]}--{spin[2]}'
    )
    embed.set_footer(text=f'Payout: ${round(payout, 2)}')
    return embed

def coinflip(user_id: int, guild_id: int, side: str, wager: float) -> discord.Embed:
    conn = sqlite3.connect('./databases/main.db')
    results = check_db(conn, user_id, guild_id, wager, 10)
    if isinstance(results, discord.Embed):
        return results
    elif side not in ['H', 'T']:
        embed = discord.Embed(
            title='Error', 
            color=discord.Color.yellow()
        )
        embed.add_field(
            name='', 
            value='Please enter \'H\' or \'T\'.', 
            inline=False
        )
        return embed
    
    symbols = ['H', 'T']
    coin_flip = random.choices(symbols, k=1)

    if side in [coin_flip[0]]:
        embed = discord.Embed(
            title='Congrats!', 
            color=discord.Color.green()
        )
        payout = wager * 1.50
    else:
        embed = discord.Embed(
            title='Try Again!', 
            color=discord.Color(int('#000000'.lstrip('#'), 16))
        )
        payout = wager * 0.5
        
    c = conn.cursor()
    c.execute('UPDATE User_Economy SET balance = balance + ? WHERE guild_id = ? AND user_id = ?', (round(payout,2), guild_id, user_id))
    conn.commit()
    conn.close()

    embed.add_field(
        name='', 
        value=f'🪙 = {coin_flip[0]}', inline=False
    )
    embed.set_footer(text=f'Payout: ${round(payout, 2)}')
    return embed

def roulette(user_id: int, guild_id: int, color: str, color_wager: float, number: int, number_wager: float):
    param_error = False
    if color is None and number is None:
        param_error = True
        message = 'Select at least one category to bet on.' 
    elif color is not None and color_wager is None:
        param_error = True
        message = 'Provide a wager for your selected color.'
    elif number is not None and number_wager is None:
        param_error = True
        message = 'Provide a wager for your selected number.'
    elif number_wager is not None and number is None:
        param_error = True
        message = 'Provide a number.'
    elif color_wager is not None and color is None:
        param_error = True
        message = 'Provide a color.'
    elif color is not None and color not in ['R', 'B']:
        param_error = True
        message = 'Please enter \'R\' or \'B\' for your color.'
    if number is not None and not (1 <= number <= 36):
        param_error = True
        message = 'Number must be between 1 and 36.'
    if param_error:
        embed = discord.Embed(
            title='Error', 
            color=discord.Color.yellow()
        )
        embed.add_field(
            name='', 
            value=message, 
            inline=False
        )
        return embed
    
    min_wager = 0
    wager = 0
    if color_wager is not None:
        wager += color_wager
        min_wager += 10
    if number_wager is not None:
        wager += number_wager
        min_wager += 10
    conn = sqlite3.connect('./databases/main.db')
    results = check_db(conn, user_id, guild_id, wager, min_wager)
    if isinstance(results, discord.Embed):
        return results
    
    reds = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
    blacks = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
    
    ball = random.randint(1, 36)
    if ball in reds:
        ball_color = 'R'
        symbol = '🔴'
    if ball in blacks:
        ball_color = 'B'
        symbol = '⚫'
        
    payout = 0
    if color == ball_color:
        embed = discord.Embed(
            title='Congrats!', 
            color=discord.Color.green()
        )
        payout += color_wager * 2
    if number == ball:
        embed = discord.Embed(
            title='CONGRATS!', 
            color=discord.Color.gold()
        )
        payout += color_wager * 10
    if payout == 0:
        embed = discord.Embed(
            title='Try Again!', 
            color=discord.Color(int('#000000'.lstrip('#'), 16))
        )
    c = conn.cursor()
    c.execute('UPDATE User_Economy SET balance = balance + ? WHERE guild_id = ? AND user_id = ?', (round(payout,2), guild_id, user_id))
    conn.commit()
    conn.close()
    
    embed.add_field(
        name='',
        value=f'{symbol}{ball}',
        inline=False
    )
    embed.set_footer(text=f'Payout: ${round(payout, 2)}')
    return embed

def check_db(conn, user_id: int, guild_id: int, wager: float, min_wager: int) -> bool:
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
            value='You are not registered in the economy. Use /register to register.', inline=False
        )
        return embed
    elif balance[0] < wager:
        embed = discord.Embed(
            title='Error', 
            color=discord.Color.yellow()
        )
        embed.add_field(
            name='', 
            value='You dont have enough money to place this wager.', 
            inline=False
        )
        return embed
    elif wager < min_wager:
        embed = discord.Embed(
            title='Error', 
            color=discord.Color.yellow()
        )
        embed.add_field(
            name='', 
            value=f'Wager must be more than ${min_wager}.', 
            inline=False
        )
        return embed
    else:
        c.execute('UPDATE User_Economy SET balance = balance - ? WHERE guild_id = ? AND user_id = ?', (wager, guild_id, user_id))
        conn.commit()
        return True