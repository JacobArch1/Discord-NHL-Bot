import sqlite3
import discord

def wipeuser(guild_id: int, username: str) -> discord.Embed:
    conn = sqlite3.connect('./databases/main.db')
    user_id = get_id(conn, guild_id, username)
    if isinstance(user_id, discord.Embed):
        return user_id
    
    c = conn.cursor()
    c.execute('DELETE FROM Betting_Pool WHERE guild_id == ? AND user_id == ?', (guild_id, user_id[0],))
    conn.commit()
    c.execute('DELETE FROM User_Economy WHERE guild_id == ? AND user_name == ?', (guild_id, username,))
    conn.commit()
    conn.close()
    
    embed = discord.Embed(
        title='Success', 
        color=discord.Color.green()
    )
    embed.add_field(
        name='',
        value=f'{username} has been removed from the economy.',
        inline='False'
    )
    return embed

def addmoney(guild_id: int, username: str, money: float) -> discord.Embed:
    conn = sqlite3.connect('./databases/main.db')
    user_id = get_id(conn, guild_id, username)
    if isinstance(user_id, discord.Embed):
        return user_id
    
    c = conn.cursor()
    c.execute('UPDATE User_Economy SET balance = balance + ? WHERE guild_id = ? AND user_id = ?', (money, guild_id, user_id[0],))
    conn.commit()
    conn.close()
    
    embed = discord.Embed(
        title='Success', 
        color=discord.Color.green()
    )
    embed.add_field(
        name='',
        value=f'Gave {username} ${money}.',
        inline=False
    )
    return embed

def takemoney(guild_id: int, username: str, money: float) -> discord.Embed:
    conn = sqlite3.connect('./databases/main.db')
    user_id = get_id(conn, guild_id, username)
    if isinstance(user_id, discord.Embed):
        return user_id
    
    c = conn.cursor()
    c.execute('UPDATE User_Economy SET balance = balance - ? WHERE guild_id = ? AND user_id = ?', (money, guild_id, user_id[0],))
    conn.commit()
    conn.close()
    
    embed = discord.Embed(
        title='Success', 
        color=discord.Color.green()
    )
    embed.add_field(
        name='',
        value=f'Removed ${money} from {username}.',
        inline=False
    )
    return embed

def reseteconomy(guild_id: int) -> discord.Embed:
    conn = sqlite3.connect('./databases/main.db')
    c = conn.cursor()
    c.execute('DELETE FROM Betting_Pool WHERE guild_id = ?', (guild_id,))
    conn.commit()
    c.execute('DELETE FROM User_Economy WHERE guild_id = ?', (guild_id,))
    conn.commit()
    conn.close()
    
    embed = discord.Embed(
        title='Success', 
        color=discord.Color.green()
    )
    embed.add_field(
        name='',
        value=f'Reset Economy.',
        inline=False
    )
    return embed
    

def get_id(conn, guild_id: int, username:str) -> int:
    c = conn.cursor()
    c.execute('SELECT user_id FROM User_Economy WHERE guild_id == ? AND user_name == ?', (guild_id, username,))
    user_id = c.fetchone()
    
    if user_id is None:
        embed = discord.Embed(
            title='Error', 
            color=discord.Color.lighter_gray()
        )
        embed.add_field(
            name='',
            value='User not found',
            inline='False'
        )
        return embed
    return user_id