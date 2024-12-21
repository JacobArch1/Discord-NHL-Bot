import sqlite3
import discord
import nhl

async def wipeuser(guild_id: int, user: str) -> discord.Embed:
    conn = sqlite3.connect('./databases/main.db')
    try:
        user_id, user_name = get_id(conn, guild_id, user)
    except ValueError as e:
        embed = discord.Embed(
            title='Error',
            description=str(e),
            color=discord.Color.lighter_gray()
        )
        return embed
    
    c = conn.cursor()
    c.execute('DELETE FROM Betting_Pool WHERE guild_id == ? AND user_id == ?', (guild_id, user_id,))
    conn.commit()
    c.execute('DELETE FROM User_Economy WHERE guild_id == ? AND user_id == ?', (guild_id, user_id,))
    conn.commit()
    conn.close()
    
    embed = discord.Embed(
        title='Success',
        description=f'{user_name} has been removed from the economy.',
        color=discord.Color.green()
    )
    return embed

async def addmoney(guild_id: int, user: str, money: float) -> discord.Embed:
    conn = sqlite3.connect('./databases/main.db')
    try:
        user_id, user_name = get_id(conn, guild_id, user)
    except ValueError as e:
        embed = discord.Embed(
            title='Error',
            description=str(e),
            color=discord.Color.lighter_gray()
        )
        return embed
    
    c = conn.cursor()
    c.execute('UPDATE User_Economy SET balance = balance + ? WHERE guild_id = ? AND user_id = ?', (money, guild_id, user_id,))
    conn.commit()
    conn.close()
    
    embed = discord.Embed(
        title='Success',
        description=f'Gave {user_name} ${money}.',
        color=discord.Color.green()
    )
    return embed

async def takemoney(guild_id: int, user: str, money: float) -> discord.Embed:
    conn = sqlite3.connect('./databases/main.db')
    try:
        user_id, user_name = get_id(conn, guild_id, user)
    except ValueError as e:
        embed = discord.Embed(
            title='Error',
            description=str(e),
            color=discord.Color.lighter_gray()
        )
        return embed
    
    c = conn.cursor()
    c.execute('UPDATE User_Economy SET balance = balance - ? WHERE guild_id = ? AND user_id = ?', (money, guild_id, user_id,))
    conn.commit()
    conn.close()
    
    embed = discord.Embed(
        title='Success',
        description=f'Removed ${money} from {user_name}.',
        color=discord.Color.green()
    )
    return embed

async def reseteconomy(guild_id: int, confirmation: int) -> discord.Embed:
    if guild_id != confirmation:
        embed = discord.Embed(
            title='Error',
            description=f'Incorrect guild id.',
            color=discord.Color.lighter_grey()
        )
        return embed
    
    conn = sqlite3.connect('./databases/main.db')
    c = conn.cursor()
    c.execute('DELETE FROM Betting_Pool WHERE guild_id = ?', (guild_id,))
    conn.commit()
    c.execute('DELETE FROM User_Economy WHERE guild_id = ?', (guild_id,))
    conn.commit()
    conn.close()
    
    embed = discord.Embed(
        title='Success',
        description=f'Reset Economy',
        color=discord.Color.green()
    )
    return embed

async def enableroles(guild: discord.Guild) -> discord.Embed:
    try:
        conn = sqlite3.connect('./databases/main.db')
        c = conn.cursor()
        c.execute('SELECT roles_enabled FROM Server_Settings WHERE guild_id = ?', (guild.id,))
        roles_enabled = c.fetchone()
        if roles_enabled == 1:
            conn.close()
            embed = discord.Embed(
                title='Error.',
                description=f'Roles are already enabled.',
                color=discord.Color.lighter_gray()
            )
            return embed
        for abbrev, team in nhl.teams.items():
            color = int(nhl.teams_colors.get(abbrev, '#111010').lstrip('#'), 16)
            await guild.create_role(name=team, permissions=discord.Permissions.none(), colour=color)
        embed = discord.Embed(
            title='Done.',
            description=f'Roles Enabled.',
            color=discord.Color.green()
        )
        c.execute('UPDATE Server_Settings SET roles_enabled = 1 WHERE guild_id = ?', (guild.id,))
        conn.commit()
        conn.close()
    except discord.errors.Forbidden:
        embed = discord.Embed(
            title='Error.',
            description=f'I don\'t have permissions to create roles.',
            color=discord.Color.lighter_gray()
        )
    return embed
    
async def disableroles(guild: discord.Guild) -> discord.Embed:
    try:
        conn = sqlite3.connect('./databases/main.db')
        c = conn.cursor()
        c.execute('SELECT roles_enabled FROM Server_Settings WHERE guild_id = ?', (guild.id,))
        roles_enabled = c.fetchone()
        if roles_enabled == 0:
            conn.close()
            embed = discord.Embed(
                title='Error.',
                description=f'Roles are not enabled.',
                color=discord.Color.lighter_gray()
            )
            return embed
        for role in guild.roles:
            if role.name in nhl.teams.values():
                await role.delete()
        embed = discord.Embed(
            title='Done.',
            description=f'Roles Disabled.',
            color=discord.Color.green()
        )
        c.execute('UPDATE Server_Settings SET roles_enabled = 0 WHERE guild_id = ?', (guild.id,))
        conn.commit()
        conn.close()
    except discord.errors.Forbidden:
        embed = discord.Embed(
            title='Error.',
            description=f'I don\'t have permissions to create roles.',
            color=discord.Color.lighter_gray()
        )
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
