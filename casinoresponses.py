import sqlite3
import discord
import random

def slots(user_id: int, guild_id: int, wager: float) -> discord.Embed:
    conn = sqlite3.connect('./databases/main.db')
    results = check_db(conn, user_id, wager)
    if isinstance(results, discord.Embed):
        return results

    symbols = ['🍒', '🍋', '🍊', '🍎', '💎', '💰']
    weights = [0.63, 0.58, 0.53 , 0.46, 0.37, 0.10]

    spin = random.choices(symbols, weights=weights, k=3)

    if spin[0] == spin[1] == spin[2]:
        if spin[0] == '🍒':
            embed = discord.Embed(
                title='Congrats!', 
                color=discord.Color.green()
            )
            payout = wager * 2
        elif spin[0] == '🍋':
            embed = discord.Embed(
                title='Congrats!', 
                color=discord.Color.yellow()
            )
            payout = wager * 5
        elif spin[0] == '🍊':
            embed = discord.Embed(
                title='Congrats!', 
                color=discord.Color.orange()
            )
            payout = wager * 7
        elif spin[0] == '🍎':
            embed = discord.Embed(
                title='Congrats!', 
                color=discord.Color.red()
            )
            payout = wager * 10
        elif spin[0] == '💎':
            embed = discord.Embed(
                title='JACKPOT!!!!!', 
                color=discord.Color.teal()
            )
            payout = wager * 50
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
            payout = wager * 10
        elif (spin[0] == '💰' and (spin[1] == '💰' or spin[2] == '💰')) or (spin[1] == '💰' and spin[2] == '💰'):
            embed = discord.Embed(
                title='Close...', 
                color=discord.Color(int('#FAEDB7'.lstrip('#'), 16))
            )
            payout = wager * 50
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
    results = check_db(conn, user_id, guild_id, wager)
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
        payout = wager * 1.15
    else:
        embed = discord.Embed(
            title='Try Again!', 
            color=discord.Color(int('#000000'.lstrip('#'), 16))
        )
        payout = 0

    embed.add_field(
        name='', 
        value=f'🪙 = {coin_flip[0]}', inline=False
    )
    embed.set_footer(text=f'Payout: ${round(payout, 2)}')
    return embed

def check_db(conn, user_id: int, guild_id: int, wager: float) -> bool:
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
    elif wager < 100:
        embed = discord.Embed(
            title='Error', 
            color=discord.Color.yellow()
        )
        embed.add_field(
            name='', 
            value='Wager must be more than $100.', 
            inline=False
        )
        return embed
    else:
        c.execute('UPDATE User_Economy SET balance = balance - ? WHERE guild_id = ? AND user_id = ?', (wager, guild_id, user_id))
        conn.commit()
        return True