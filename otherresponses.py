import discord

def help() -> discord.Embed:
    embed = discord.Embed(title = "Command List", color = discord.Color(0x6203fc))
    embed.add_field(name="playerstats", value="```Parameters: [firstName] [lastName] \nDisplays player stats```", inline=False)
    embed.add_field(name="currentstandings", value="```Show standings for the current season```", inline=False)
    embed.add_field(name="standings", value="```Parameters: [YYYY-YYYY] \nShow standings from given year (end of season)```", inline=False)
    embed.add_field(name="leaders", value="```Parameters: [position] [category] \nShow the top 5 leaders in given category```", inline=False)
    return embed

def glossary() -> discord.Embed:
    embed = discord.Embed(title = "Glossary", color = discord.Color(0x6203fc))
    embed.add_field(name="Skater Stats", value=f"""```\nGP - Games Played\nG - Goals\nP - Points\n+/- - Plus Minus\nPIM - Penalty Minutes
PPG - Power Play Goals\nPPP - Power Play Points\nSHG - Short Handed Goals\nSHP - Short Handed Points\nTOI/G - Time On Ice per Game
GWG - Game Winning Goals\nOTG - Overtime Goals\nS - Shots\nS% - Shooting Pctg\nFO% - Faceoff Win Pctg```""", inline=False)
    embed.add_field(name="Goalie Stats", value=f"""```\nGP - Games Played\nGS - Games Started\nW - Wins\nL - Losses\nOT - Over Time Losses
SA - Shots Against\nGA - Goals Against\nSO - Shutouts\nA - Assists\nGAA - Goals Against Avg\nSV% - Save Pctg```""", inline=False)
    embed.add_field(name="Skater Leader Categories", value="""```\nGoals\nAssists\nPoints```""", inline=False)
    embed.add_field(name="Goalie Leader Categories", value="""```\nWins\nSavePctg\nShutouts```""", inline=False)
    return embed