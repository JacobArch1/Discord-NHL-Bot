from datetime import date, datetime, timedelta
import datetime
import sqlite3
import discord
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

async def balance(user_id: int, guild_id: int, avatar: str, user: str) -> discord.Embed:
    conn = sqlite3.connect('./databases/main.db')
    c = conn.cursor()
    
    title = 'Your Balance'
    if user:
        try:
            user_id, user_name = get_id(conn, guild_id, user)
            title = f'{user_name}\'s Balance'
        except ValueError as e:
            embed = discord.Embed(
                title='Error',
                description=str(e),
                color=discord.Color.lighter_gray()
            )
            return embed
        
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
            value='You are not registered in the economy. Use $register to register.', 
            inline=False
        )
    else:
        embed = discord.Embed(
            title=title, 
            color=discord.Color.green()
        )
        embed.set_author(
            name='Balance', 
            icon_url=avatar
        )
        embed.add_field(
            name='', 
            value=f'${balance[0]}', 
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

def get_id(conn, guild_id: int, user:str) -> tuple[int, str]:
    c = conn.cursor()
    user_id = None
    
    if '@' in user:
        user_id = user.strip('<@!>')
        c.execute('SELECT user_id, user_name FROM User_Economy WHERE guild_id == ? AND user_id == ?', (guild_id, user_id,))
        user_info = c.fetchone()
    else:
        c.execute('SELECT user_id, user_name FROM User_Economy WHERE guild_id == ? AND user_name == ?', (guild_id, user,))
        user_info = c.fetchone()
    
    if user_info is None:
        raise ValueError('User not found or not registered')
    
    return user_info[0], user_info[1]

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
    tables = ['User_Economy', 'Jackpot', 'Bet_History', 'Betting_Pool', 'Server_Settings', 'Update_List']
    for table in tables:
        c.execute(f'DELETE FROM {table} WHERE guild_id = ?', (guild_id,))
        conn.commit()
    conn.close()
    
def channel_deleted(channel_id: int):
    conn = sqlite3.connect('./databases/main.db')
    c = conn.cursor()
    c.execute('DELETE FROM Update_List WHERE channel_id = ?', (channel_id,))
    conn.commit()
    conn.close()