from datetime import date, datetime, timedelta
import datetime
import sqlite3
import discord
import random
import nhl

async def register(user_id: int, user_name: str, guild_id: int, avatar: str) -> discord.Embed:
    conn = sqlite3.connect('./databases/main.db')
    c = conn.cursor()
    c.execute('SELECT * FROM User_Economy WHERE guild_id = ? AND user_id = ?', (guild_id, user_id,))
    user = c.fetchone()
    if user:
        embed = discord.Embed(
            title = 'Error', 
            color = discord.Color.lighter_gray()
        )
        embed.set_author(
            name='Register', 
            icon_url=avatar
        )
        embed.add_field(
            name='', 
            value='You are already registered.', 
            inline=False
        )
    else:
        c.execute('INSERT INTO User_Economy (guild_id, user_id, balance, user_name) VALUES (?, ?, ?, ?)', (guild_id, user_id, 1000, user_name,))
        embed = discord.Embed(
            title = 'Success!', 
            color = discord.Color.green()
        )
        embed.set_author(
            name='Register', 
            icon_url=avatar
        )
        embed.add_field(
            name='', 
            value='You have succesfully registered.', 
            inline=False
        )
        conn.commit()

    conn.close()
    return embed

async def bonus(user_id: int, guild_id: str, avatar: str) -> discord.Embed:
    conn = sqlite3.connect('./databases/main.db')
    c = conn.cursor()
    c.execute('SELECT user_name FROM User_Economy WHERE guild_id = ? AND user_id = ?', (guild_id, user_id,))
    result = c.fetchone()

    if result is None:
        embed = discord.Embed(
            title='Error', 
            color=discord.Color.lighter_gray()
        )
        embed.set_author(
            name='Bonus', 
            icon_url=avatar
        )
        embed.add_field(
            name='', 
            value='You are not registered in the economy. Use /register to register.', 
            inline=False
        )
    else:
        bonus_amount = 1000
        c.execute('UPDATE User_Economy SET balance = balance + ? WHERE guild_id = ? AND user_id = ?', (bonus_amount, guild_id, user_id,))
        conn.commit()

        embed = discord.Embed(
            title='Claimed!', 
            color=discord.Color.green()
        )
        embed.set_author(
            name='Bonus', 
            icon_url=avatar
        )
        embed.add_field(
            name='', 
            value=f'You claimed your daily ${bonus_amount} bonus.', 
            inline=False
        )

    conn.close()
    return embed

async def beg(user_id: int, guild_id: int, avatar: str) -> discord.Embed:
    conn = sqlite3.connect('./databases/main.db')
    c = conn.cursor()
    c.execute('SELECT user_name FROM User_Economy WHERE guild_id = ? AND user_id = ?', (guild_id, user_id,))
    result = c.fetchone()

    if result is None:
        embed = discord.Embed(
            title='Error', 
            color=discord.Color.lighter_gray()
        )
        embed.set_author(
            name='Beg', 
            icon_url=avatar
        )
        embed.add_field(
            name='', 
            value='You are not registered in the economy. Use /register to register.', 
            inline=False
        )
    
    beg_amount = random.randint(50, 100)
    c.execute('UPDATE User_Economy SET balance = balance + ? WHERE guild_id = ? AND user_id = ?', (beg_amount, guild_id, user_id,))
    conn.commit()
    
    embed = discord.Embed(
        title='You begged for money.', 
        color=discord.Color.green()
    )
    embed.set_author(
        name='Beg', 
        icon_url=avatar
    )
    embed.add_field(
        name='',
        value=f'And earned ${beg_amount}. 💵',
        inline=False
    )
    
    return embed

async def balance(user_id: int, guild_id: int, avatar: str) -> discord.Embed:
    conn = sqlite3.connect('./databases/main.db')
    c = conn.cursor()
    
    c.execute('SELECT balance FROM User_Economy WHERE guild_id = ? AND user_id = ?', (guild_id, user_id,))
    balance = c.fetchone()
    if balance is None:
        embed = discord.Embed(
            title='Error', 
            color=discord.Color.lighter_gray()
        )
        embed.set_author(
            name='Balance', 
            icon_url=avatar
        )
        embed.add_field(
            name='', 
            value='You are not registered in the economy. Use /register to register.', 
            inline=False
        )
    else:
        embed = discord.Embed(
            title='', 
            color=discord.Color.green()
        )
        embed.set_author(
            name='Balance', 
            icon_url=avatar
        )
        embed.add_field(
            name='', 
            value=f'Your Balance is: ${balance[0]}', 
            inline=False
        )

    conn.close()
    return embed

async def placebet(user_id: int, guild_id: int, team: str, wager: float, user_name: str, avatar: str) -> discord.Embed:
    verified = nhl.verify_team(team)
    if isinstance(verified, discord.Embed):
        return verified
    conn = sqlite3.connect('./databases/main.db')
    
    results = check_db(conn, user_id, guild_id, wager, 10)
    if isinstance(results, discord.Embed):
        return results
    
    game = check_bet_valid(conn, team)
    if isinstance(game, discord.Embed):
        return game
    
    c = conn.cursor()
    game_id = game[1]
    game_type = game[4]

    c.execute('INSERT INTO Betting_Pool (game_id, guild_id, game_type, user_id, team, wager) VALUES (?, ?, ?, ?, ?, ?)', (game_id, guild_id, game_type, user_id, team, wager,))
    conn.commit()
    embed = discord.Embed(
        title=f'{user_name} Placed a bet.', 
        description=f'${round(wager,2)} on {team.upper()}', 
        color=discord.Color.green()
    )
    embed.set_author(
        name='Bet', 
        icon_url=avatar
    )
    return embed

async def mybets(user_id: int, guild_id: int, avatar: str) -> discord.Embed:
    conn = sqlite3.connect('./databases/main.db')
    c = conn.cursor()

    c.execute('SELECT * FROM Betting_Pool WHERE guild_id = ? AND user_id = ?', (guild_id, user_id,))
    bets = c.fetchall()
    if not bets:
        embed = discord.Embed(
            title='Error', 
            description='You do not have any bets placed.', 
            color=discord.Color.lighter_gray()
        )
    else:
        embed = discord.Embed(
            title='Your active bets.', 
            color=discord.Color.green()
        )
        embed.set_author(
            name='Bets', 
            icon_url=avatar
        )
        for bet in bets:
            embed.add_field(
                name=f'', 
                value=f'**{bet[5]}**: ${bet[6]}', 
                inline=False
            )

    conn.close()
    return embed

async def bethistory(user_id: int, guild_id: int, user_name: str, avatar: str) -> discord.Embed:
    conn = sqlite3.connect('./databases/main.db')
    c = conn.cursor()

    c.execute('SELECT * FROM Bet_History WHERE guild_id = ? AND user_id = ? ORDER BY id DESC LIMIT 10', (guild_id, user_id,))
    bets = c.fetchall()
    if not bets:
        embed = discord.Embed(
            title='Error', 
            color=discord.Color.lighter_gray()
        )
        embed.set_author(
            name='Bet History', 
            icon_url=avatar
        )
        embed.add_field(
            name='', 
            value='Your history is empty.', 
            inline=False
        )
    else:
        embed = discord.Embed(
            title=f'{user_name}\'s Bet History', 
            color=discord.Color.green()
        )
        embed.set_author(
            name='Bet History', 
            icon_url=avatar
        )
        for bet in bets:
            embed.add_field(
                name=f'', 
                value=f'**{bet[5]}**: ${bet[6]} | Payout: ${bet[7]}', 
                inline=False
            )

    conn.close()
    return embed

async def removebet(user_id: int, guild_id: int, team: str, avatar: str) -> discord.Embed:
    conn = sqlite3.connect('./databases/main.db')
    c = conn.cursor()

    c.execute('SELECT * FROM Betting_Pool WHERE team = ? AND guild_id = ? AND user_id = ?', (team, guild_id, user_id,))
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
            description='Could not find bet.', 
            color=discord.Color.lighter_gray()
        )
    elif current_time > close_time:
        embed = discord.Embed(
            title='Error', 
            description='Betting for this game is closed. Cannot remove bet.',
            color=discord.Color.lighter_gray()
        )
    else:
        refund = bet[6]
        c.execute('UPDATE User_Economy SET balance = balance + ? WHERE guild_id = ? AND user_id = ?', (refund, guild_id, user_id,))
        c.execute('DELETE FROM Betting_Pool WHERE guild_id = ? AND user_id = ?', (guild_id, user_id,))
        conn.commit()

        embed = discord.Embed(
            title='Success!', 
            description='Your bet has been removed.', 
            color=discord.Color.green()
        )

    conn.close()
    return embed

async def leaderboard(guild_id: str) -> discord.Embed:
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

async def slots(user_id: int, guild_id: int, wager: float, user_name: str, avatar: str) -> discord.Embed:
    conn = sqlite3.connect('./databases/main.db')
    results = check_db(conn, user_id, guild_id, wager, 1)
    if isinstance(results, discord.Embed):
        return results
    
    if wager not in [1, 5, 10, 100]:
        embed = discord.Embed(
            title='Wager must be $1, $5, $10, $100',
            color=discord.Color.lighter_gray()
        )
        embed.set_author(
            name='Slots', 
            icon_url=avatar
        )
        return embed

    symbols = ['🍒', '🍋', '🍊', '🍎', '💎', '💰']
    weights = [38, 28, 20, 10, 3, 1]

    spin = random.choices(symbols, weights=weights, k=3)

    title='Try Again!'
    color=discord.Color(int('#000000'.lstrip('#'), 16))
    payout = 0
    
    if spin[0] == spin[1] == spin[2]:
        if spin[0] == '🍒':
            title='You Win!'
            color=discord.Color.green()
            payout = wager * 2
        elif spin[0] == '🍋':
            title='You Win!'
            color=discord.Color.yellow()
            payout = wager * 4
        elif spin[0] == '🍊':
            title='You Win!'
            color=discord.Color.orange()
            payout = wager * 8
        elif spin[0] == '🍎':
            title='You Win!'
            color=discord.Color.red()
            payout = wager * 10
        elif spin[0] == '💎':
            title='JACKPOT!'
            color=discord.Color.teal()
            payout = 1000
        elif spin[0] == '💰':
            title='SUPER JACKPOT!!'
            color=discord.Color.gold()
            payout = 10000
    elif spin[0] == spin[1] or spin[1] == spin[2] or spin[0] == spin[2]:
        if (spin[0] == '💎' and (spin[1] == '💎' or spin[2] == '💎')) or (spin[1] == '💎' and spin[2] == '💎'):
            title='Close...'
            color=discord.Color(int('#BCF6EA'.lstrip('#'), 16))
            payout = 100
        elif (spin[0] == '💰' and (spin[1] == '💰' or spin[2] == '💰')) or (spin[1] == '💰' and spin[2] == '💰'):
            title='Close...'
            color=discord.Color(int('#FAEDB7'.lstrip('#'), 16))
            payout = 100
        
    embed = discord.Embed(
        title=f'{user_name} Played Slots',
        color=color,
    )
    embed.set_author(
        name='Slots', 
        icon_url=avatar
    )
    c = conn.cursor()
    c.execute('UPDATE User_Economy SET balance = balance + ? WHERE guild_id = ? AND user_id = ?', (round(payout,2), guild_id, user_id))
    conn.commit()
    conn.close()
    embed.add_field(
        name='', 
        value=f'>>|{spin[0]}--{spin[1]}--{spin[2]}|<<\n\n**----{title}----**\n\n**Wager:** ${wager} 💸\n**Payout:** ${round(payout, 2)} 💵'
    )
    embed.set_footer(text=f'{generate_phrase(wager, payout)}')
    embed.set_thumbnail(url='https://icons.iconarchive.com/icons/microsoft/fluentui-emoji-3d/512/Slot-Machine-3d-icon.png')
    return embed

async def coinflip(user_id: int, guild_id: int, side: str, user_name: str, avatar: str) -> discord.Embed:
    conn = sqlite3.connect('./databases/main.db')
    results = check_db(conn, user_id, guild_id, 10, 10)
    if isinstance(results, discord.Embed):
        return results
    
    side = side.lower()
    if side not in ['h', 't', 'heads', 'tails']:
        embed = discord.Embed(
            title='Error', 
            description='Please enter \'H\' or \'T\'.', 
            color=discord.Color.lighter_gray()
        )
        return embed
    
    if side in ['h', 'heads']:
        side = 'Heads'
    else:
        side = 'Tails'
     
    symbols = ['Heads', 'Tails']
    coin_flip = random.choices(symbols, k=1)

    if side in [coin_flip[0]]:
        title='Congrats!'
        color=discord.Color.green()
        payout = 20
    else:
        title='Try Again!'
        color=discord.Color(int('#000000'.lstrip('#'), 16))
        payout = 0
        
    c = conn.cursor()
    c.execute('UPDATE User_Economy SET balance = balance + ? WHERE guild_id = ? AND user_id = ?', (round(payout,2), guild_id, user_id))
    conn.commit()
    conn.close()

    embed = discord.Embed(
        title=f'{user_name} Flipped a Coin',
        color=color,
    )
    embed.set_author(
        name='Coin Flip', 
        icon_url=avatar
    )
    embed.add_field(
        name='', 
        value=f'Coin Landed On: **{coin_flip[0]}**\nYou Picked: **{side}**\n\n**----{title}----**\n**Payout:** ${payout}💵', 
        inline=False
    )
    embed.set_thumbnail(url='https://www.iconpacks.net/icons/1/free-coin-icon-794-thumb.png')
    return embed

async def roulette(user_id: int, guild_id: int, category_one: str, category_one_wager: float, category_two: str, category_two_wager: float, user_name: str, avatar: str) -> discord.Embed:
    color = None
    color_wager = None
    number = None
    number_wager = None
    param_error = False

    category_one = category_one.lower() if category_one and isinstance(category_one, str) else category_one
    category_two = category_two.lower() if category_two and isinstance(category_two, str) else category_two

    if category_one is None and category_two is None:
        param_error = True
        message = 'Select at least one category to bet on.'
    if (category_one and category_one_wager is None) or (category_two and category_two_wager is None):
        param_error = True
        message = 'Missing a wager.'
    if category_one in ['r', 'b', 'red', 'black'] and category_two in ['r', 'b', 'red', 'black']:
        param_error = True
        message = 'You cannot bet on two colors.'

    if category_one in ['red', 'r', 'black', 'b']:
        color, color_wager = category_one, category_one_wager
        number, number_wager = category_two, category_two_wager
    elif category_two in ['red', 'r', 'black', 'b']:
        color, color_wager = category_two, category_two_wager
        number, number_wager = category_one, category_one_wager
    else:
        number, number_wager = category_one, category_one_wager

    if color and color not in ['r', 'b', 'red', 'black']:
        param_error = True
        message = 'Please enter \'Red\' or \'Black\' (R/B) for your color.'

    if number:
        try:
            number = int(number)
            if not (1 <= number <= 36):
                param_error = True
                message = 'Number must be between 1 and 36.'
        except ValueError:
            param_error = True
            message = 'Enter a valid number.'

    if param_error:
        embed = discord.Embed(
            title='Error',
            color=discord.Color.lighter_gray()
        )
        embed.set_author(
            name='Roulette',
            icon_url=avatar
        )
        embed.add_field(
            name='',
            value=message,
            inline=False
        )
        return embed
    
    color_guess = None
    if color in ['r', 'red']:
        color_guess = 'Red'
    elif color in ['b', 'black']:
        color_guess = 'Black'
    min_wager = 0
    wager = 0
    wager_title = ''
    if color_wager is not None:
        wager += color_wager
        min_wager += 10
        wager_title += f'${color_wager} on {color_guess}\n'
    if number_wager is not None:
        wager += number_wager
        min_wager += 10
        wager_title += f'${number_wager} on **[{number}]**\n'
    
    conn = sqlite3.connect('./databases/main.db')
    results = check_db(conn, user_id, guild_id, wager, min_wager)
    if isinstance(results, discord.Embed):
        return results
    
    reds = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
    blacks = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
    
    ball = random.randint(1, 36)
    if ball in reds:
        ball_color = 'Red'
        symbol = '🟥'
    if ball in blacks:
        ball_color = 'Black'
        symbol = '⬛'
    
    payout = 0
    title='Try Again!'
    color=discord.Color(int('#000000'.lstrip('#'), 16))
    if color_guess == ball_color:
        title='Congrats!'
        color=discord.Color.green()
        payout += color_wager * 2
    if number == ball:
        title='CONGRATS!'
        color=discord.Color.gold()
        payout += color_wager * 10
    
    c = conn.cursor()
    c.execute('UPDATE User_Economy SET balance = balance + ? WHERE guild_id = ? AND user_id = ?', (round(payout,2), guild_id, user_id))
    conn.commit()
    conn.close()
    
    embed = discord.Embed(
        title=f'{user_name} Played Roulette',
        color=color,
    )
    embed.set_author(
        name='Roulette', 
        icon_url=avatar
    )
    embed.add_field(
        name='',
        value=f'Ball Landed On: {symbol}**[{ball}]** \n\n**Wager:** 💸\n{wager_title}\n**----{title}----**\n\n**Payout:** ${payout} 💵',
        inline=False
    )
    embed.set_footer(text=f'{generate_phrase(wager, payout)}')
    embed.set_thumbnail(url='https://cdn-icons-png.flaticon.com/512/3425/3425938.png')
    return embed

async def jackpot(guild_id: int, user_id: int, amount: float, user_name: str, avatar: str) -> discord.Embed:
    conn = sqlite3.connect('./databases/main.db')
    results = check_db(conn, user_id, guild_id, amount, 1)
    if isinstance(results, discord.Embed):
        return results
    
    if amount > 100:
        embed = discord.Embed(
            title='Error', 
            color=discord.Color.lighter_gray()
        )
        embed.set_author(
            name='Jackpot', 
            icon_url=avatar
        )
        embed.add_field(
            name='', 
            value='Max wager is $100.', inline=False
        )
        return embed
    
    c = conn.cursor()
    c.execute('SELECT * FROM Jackpot WHERE guild_id = ?', (guild_id,))
    jackpot = c.fetchone()
    
    if jackpot is None:
        c.execute('INSERT INTO Jackpot (guild_id, pot, cashout_odds, num_tips, last_tipper, last_tipper_amount) VALUES (?, ?, ?, ?, ?, ?)', (guild_id, 5000, 0.1, 0, 'Nobody Yet', 0.0,))
        conn.commit()
        c.execute('SELECT * FROM Jackpot WHERE guild_id = ?', (guild_id,))
        jackpot = c.fetchone()
    
    pot = jackpot[2]
    cashout_odds = jackpot[3]

    pot += amount
    bet_multiplier = amount / 100
    total_odds = cashout_odds + bet_multiplier
    
    title = f'Your tip is appreciated ❤️'
    content = f'**The pot is now at:** ${pot} 💵'
    color=discord.Color(int('#000000'.lstrip('#'), 16))
    if random.uniform(0, 100) < cashout_odds:
        title = f'THE POT HAS SPILLED!!!!'
        content = f'**{user_name} Has Won:** ${pot} 💵\nCongratulations!'
        color=discord.Color.gold()
        c.execute('UPDATE Jackpot SET pot = 10000, cashout_odds = 0.1, num_tips = 0, last_tipper = \'Nobody Yet\', last_tipper_amount = 0.0 WHERE guild_id = ?;', (guild_id,))
        conn.commit()
        c.execute('UPDATE User_Economy SET balance = balance + ? WHERE guild_id = ? AND user_id = ?', (pot, guild_id, user_id,))
        conn.commit()
    else:
        new_cashout_odds = min(cashout_odds + 0.1, 100.0)
        c.execute('UPDATE Jackpot SET pot = ?, cashout_odds = ?, num_tips = num_tips + 1, last_tipper = ?, last_tipper_amount = ? WHERE guild_id = ?;', (pot, new_cashout_odds, user_name, amount, guild_id))
        conn.commit()
    conn.close()
    
    embed = discord.Embed(
        title=f'{user_name} Tipped The Jackpot',
        color=color,
    )
    embed.set_author(
        name='Jackpot', 
        icon_url=avatar
    )
    embed.add_field(
        name='',
        value=f'**Amount Tipped:** ${amount} 💸\n**Cashout Odds:** {round(cashout_odds,2)}%\n\n**Bet Multiplier:** {round(bet_multiplier,2)}%\n{round(total_odds,2)}% Total Odds\n\n**----{title}----**\n\n{content}'
    )
    embed.set_thumbnail(url='https://cdn0.iconfinder.com/data/icons/st-patrick-s-day-icon-t-event-flat/64/StPatricksDay-Flat-PotofGold-512.png')
    
    return embed

async def checkjackpot(guild_name: str, guild_id: int) -> discord.Embed:
    conn = sqlite3.connect('./databases/main.db')
    c = conn.cursor()
    c.execute('SELECT * FROM Jackpot WHERE guild_id = ?', (guild_id,))
    jackpot = c.fetchone()
    
    cashout_odds = round(jackpot[3], 2)
    amount = round(jackpot[2], 2)
    last_tipper = jackpot[5]
    last_tipper_amount = round(jackpot[6], 2)
    
    embed = discord.Embed(
        title=f'{guild_name} Jackpot',
        color=discord.Color(int('#000000'.lstrip('#'), 16))
    )
    embed.add_field(
        name='',
        value=f'**Cashout Odds:** {cashout_odds}%\n**Amount:** ${amount} 💵\n\nLast Tipper: {last_tipper} tipped ${last_tipper_amount} 💸'
    )
    embed.set_thumbnail(url='https://cdn0.iconfinder.com/data/icons/st-patrick-s-day-icon-t-event-flat/64/StPatricksDay-Flat-PotofGold-512.png')
    
    return embed

async def hockeypoker(bot, guild_id: int, user_id: int, opponent: str, team: str, wager: float) -> discord.Embed:
    verified = nhl.verify_team(team)
    if isinstance(verified, discord.Embed):
        return verified
    
    conn = sqlite3.connect('./databases/main.db')
    results = check_db(conn, user_id, guild_id, wager, 100)
    if isinstance(results, discord.Embed):
        return results
    
    opponent_id = get_id(conn, guild_id, opponent)
    if isinstance(opponent_id, discord.Embed):
        return opponent_id
    
    c = conn.cursor()
    c.execute('SELECT balance FROM User_Economy WHERE guild_id == ? and user_id == ?', (guild_id, opponent_id[0],))
    balance = c.fetchone()
    if balance[0] < wager:
        embed = discord.Embed(
            title='Error',
            description='User cannot match wager.',
            color=discord.Color.lighter_grey()
        )
        return embed

    game = check_bet_valid(conn, team)
    if isinstance(game, discord.Embed):
        return game
    
    c.execute(f'SELECT user_id FROM Poker_Pool WHERE guild_id = ? AND user_id = ? AND game_id = ?', (guild_id, user_id, game[1],))
    user_playing = c.fetchone()
    if user_playing:
        embed = discord.Embed(
            title='Error', 
            description='You are already playing this game.', 
            color=discord.Color.lighter_gray()
        )
        return embed
    
    c.execute('SELECT user_id FROM Poker_Pool WHERE guild_id = ? AND opponent_id = ? AND game_id = ?', (guild_id, opponent_id[0], game[1],))
    opponent_playing = c.fetchone()
    if opponent_playing:
        embed = discord.Embed(
            title='Error', 
            description='Opponent is already playing this game or has an active request.', 
            color=discord.Color.lighter_gray()
        )
        return embed
    
    user = await bot.fetch_user(user_id)
    away_team = game[2]
    home_team = game[3]
    user_team = None
    opponent_team = None
    
    if away_team == team:
        user_team = away_team
        opponent_team = home_team
    else:
        user_team = home_team
        opponent_team = away_team
    
    challenge_msg = discord.Embed(
        title='Hockey Poker Challenge!',
        description=f'{user.name} has challenged you to hockey poker.\nYou will be playing as {opponent_team} against {user_team}',
        color=discord.Color.gold()
    )
    
    opponent_user = await bot.fetch_user(opponent_id[0])
    await opponent_user.send(embed=challenge_msg, view=ChallengeView(opponent_id[0], guild_id, wager))
    
    embed = discord.Embed(
        title='Success', 
        description=f'Your challenge has been sent to {opponent_user.name}.', 
        color=discord.Color.green()
    )
    
    c.execute('INSERT INTO Poker_Pool (game_id, game_type, guild_id, user_id, opponent_id, user_team, opponent_team, user_pot, opponent_pot) VALUES (?,?,?,?,?,?,?,?,?)', 
              (game[1], game[4], guild_id, user_id, opponent_id[0], user_team, opponent_team, wager, wager))
    
    conn.commit()
    conn.close()
    return embed

class ChallengeView(discord.ui.View):
    def __init__(self, user_id: int, guild_id: int, wager: int):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.guild_id = guild_id
        self.wager = wager
    
    @discord.ui.button(label='Accept', style=discord.ButtonStyle.success)
    async def accept_button_pressed(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message('You\'re not allowed to interact with this message.', ephemeral=True, delete_after=3)
            return
        
        conn = sqlite3.connect('./databases/main.db')
        c = conn.cursor()
        c.execute('SELECT balance FROM User_Economy WHERE guild_id == ? and user_id == ?', (self.guild_id, self.user_id,))
        balance = c.fetchone()
        if balance[0] < self.wager:
            embed = discord.Embed(
                title='Error',
                description='You don\'t have enough money.',
                color=discord.Color.lighter_grey()
            )
            return embed
        
        embed = discord.Embed(
            title='Challenge Accepted!',
            description='Bot will DM you when the game starts',
            color=discord.Color.gold()
        )
        
        c.execute('UPDATE User_Economy SET balance = balance - ? WHERE guild_id = ? AND user_id = ?', (self.wager, self.guild_id, self.user_id,))
        conn.commit()
        c.execute('UPDATE Poker_Pool SET opponent_accepted = 1 WHERE opponent_id = ?', (self.user_id,))
        conn.commit()
        conn.close()
    
        await interaction.response.edit_message(embed=embed, view=None)
        
    @discord.ui.button(label='Decline', style=discord.ButtonStyle.danger)
    async def decline_button_pressed(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message('You\'re not allowed to interact with this message.', ephemeral=True, delete_after=3)
            return
        
        embed = discord.Embed(
            title='Challenge Declined',
            description='Opponent has been notified.',
            color=discord.Color.red()
        )
        
        conn = sqlite3.connect('./databases/main.db')
        c = conn.cursor()
        c.execute('SELECT * FROM Poker_Pool WHERE opponent_id = ?', (self.user_id,))
        match_data = c.fetchone()
        opponent_wager = match_data[8]
        opponent_id = match_data[4]
        
        c.execute('UPDATE User_Economy SET balance = balance + ? WHERE guild_id = ? AND user_id = ?', (opponent_wager, self.guild_id, opponent_id,))
        c.execute('DELETE FROM Poker_Pool WHERE opponent_id = ?', (self.user_id,))
        conn.commit()
        conn.close()
        
        await interaction.response.edit_message(embed=embed, view=None)

def get_id(conn, guild_id: int, user:str) -> int:
    c = conn.cursor()
    user_id = None
    
    if '@' in user:
        user_id = user.replace('<@', '')
        user_id = user_id.replace('>','')
        c.execute('SELECT user_id FROM User_Economy WHERE guild_id == ? AND user_id == ?', (guild_id, user_id,))
        user_id = c.fetchone()
    else:
        c.execute('SELECT user_id FROM User_Economy WHERE guild_id == ? AND user_name == ?', (guild_id, user,))
        user_id = c.fetchone()
    
    if user_id is None:
        embed = discord.Embed(
            title='Error',
            description='User not found or not registered',
            color=discord.Color.lighter_gray()
        )
        return embed
    return user_id

def check_db(conn, user_id: int, guild_id: int, wager: float, min_wager: int) -> bool:
    c = conn.cursor()
    c.execute('SELECT balance FROM User_Economy WHERE guild_id = ? AND user_id = ?', (guild_id, user_id,))
    balance = c.fetchone()
    if balance is None:
        embed = discord.Embed(
            title='Error', 
            color=discord.Color.lighter_gray()
        )
        embed.add_field(
            name='', 
            value='You are not registered in the economy. Use $register to register.', inline=False
        )
        return embed
    elif balance[0] < wager:
        embed = discord.Embed(
            title='Error', 
            color=discord.Color.lighter_gray()
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
            color=discord.Color.lighter_gray()
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

def check_bet_valid(conn, team: str) -> list:
    c = conn.cursor()
    current_time = datetime.datetime.now().time()
    current_date = str(date.today())
    c.execute('SELECT * FROM Current_Games WHERE home_team = ? OR away_team = ? AND start_date = ?', (team, team, current_date))
    game = c.fetchone()
    if game is None:
        embed = discord.Embed(
            title='Error',
            description='The team you selected is not playing today.', 
            color=discord.Color.lighter_gray()
        )
        return embed
    game_start_time = datetime.datetime.strptime(game[6], '%H:%M:%S').time()
    close_time = (datetime.datetime.combine(datetime.datetime.today(), game_start_time) - timedelta(minutes=10)).time()
    if current_time > close_time:
        embed = discord.Embed(
            title='Error', 
            description='Bets for this game are closed.', 
            color=discord.Color.lighter_gray()
        )
        return embed
    return game

def added_to_guild(guild_id: int):
    conn = sqlite3.connect('./databases/main.db')
    c = conn.cursor()
    c.execute('INSERT INTO Server_Settings (guild_id, roles_enabled, update_roles_enabled, create_game_channels) VALUES (?, ?, ?, ?)', (guild_id, 0, 0, 0))
    conn.commit()
    conn.close()

def removed_from_guild(guild_id: int):
    conn = sqlite3.connect('./databases/main.db')
    c = conn.cursor()
    c.execute('DELETE FROM User_Economy WHERE guild_id = ?', (guild_id,))
    conn.commit()
    c.execute('DELETE FROM Jackpot WHERE guild_id = ?', (guild_id,))
    conn.commit()
    c.execute('DELETE FROM Bet_History WHERE guild_id = ?', (guild_id,))
    conn.commit()
    c.execute('DELETE FROM Betting_Pool WHERE guild_id = ?', (guild_id,))
    conn.commit()
    c.execute('DELETE FROM Server_Settings WHERE guild_id = ?', (guild_id,))
    conn.commit()
    c.execute('DELETE FROM Update_List WHERE guild_id = ?', (guild_id,))
    conn.commit()
    c.execute('DELETE FROM Server_Settings WHERE guild_id = ?', (guild_id,))
    conn.commit()
    conn.close()
    
def channel_deleted(channel_id: int):
    conn = sqlite3.connect('./databases/main.db')
    c = conn.cursor()
    c.execute('DELETE FROM Update_List WHERE channel_id = ?', (channel_id,))
    conn.commit()
    conn.close()
    
def generate_phrase(wager: float, payout: float):
    loss_phrases = [
        'Gambling addiction? Maybe just stop, idk.',
        '9/10 gamblers quit right before the big win.',
        'You could have bought something useful with that.',
        'The wife\'s gonna be upset about this.',
        'Looks like the kids won\'t be eating this week.',
        'One more spin can\'t hurt. Right?',
        'The next spin will be the jackpot. Trust me.',
        'You\'re bound to win eventually.',
        'Retirement is for quitters.',
        'The machine is testing your willpower. Keep going.',
        'This machine IS up to casino standards.'
    ]

    huge_loss_phrases = [
        'Why did you do that?',
        'Putting more money in doesn\'t increase your chances.',
        'Time to go home.',
        'The bar is always open.',
        'It must be rigged.'
    ]

    win_phrases = [
        'See? I told you you\'d win! Eventually...',
        'Play again while you\'re up!',
        'Everyone is impressed with you!',
        'Your parents are still disappointed in you!',
        'How much of that will you put back in?'
    ]

    huge_win_phrases = [
        'LEAVE NOW!',
        'The floor supervisors are looking for you.',
        'This win will be paid out over 5 years.',
        'Everyone loves you!',
        'Gambling ALWAYS pays off!',
        'Is this going to your kids? Or back in the machine?',
        'This isn\'t real money btw.'
    ]
    
    won = payout > 0
    huge_wager = wager >= 10000
    
    if won and huge_wager:
        phrase_list = huge_win_phrases
    elif not won and huge_wager:
        phrase_list = huge_loss_phrases
    elif won and not huge_wager:
        phrase_list = win_phrases
    else:
        phrase_list = loss_phrases
        
    return random.choice(phrase_list)