import matplotlib.pyplot as plt
from PIL import Image
import nhl
import discord
import sqlite3

async def send_events(game_id: int, update_list: list, bot):
    results = nhl.get_play_by_play(game_id)
    
    away_team_id = results['awayTeam']['id']
    away_team_abbrev = results['awayTeam']['abbrev']
    away_team = [away_team_id, away_team_abbrev]
    
    home_team_id = results['homeTeam']['id']
    home_team_abbrev = results['homeTeam']['abbrev']
    home_team = [home_team_id, home_team_abbrev]
    
    events = results['plays']
    
    if events:
        event = events[-1]
    else:
        return
    
    event_id = event['eventId']
    event_type = event['typeDescKey']
    
    desired_events = {'period-start', 'period-end', 'goal', 'penalty', 'game-end'}
    
    if event_type not in desired_events:
        return
    
    embed = craft_embed(event, event_type, game_id, away_team, home_team)
    
    for channel_id in update_list:
        conn = sqlite3.connect('./databases/main.db')
        c = conn.cursor()
        c.execute('SELECT last_event_id FROM Update_List WHERE channel_id = ?', (channel_id, ))
        last_event_id = c.fetchone()
        
        if event_id != last_event_id:
            channel = bot.get_channel(channel_id)
            if channel:
                await channel.send(embed=embed)
                
def craft_embed(event: dict, type: str, game_id: int, away_team: dict, home_team: dict) -> discord.Embed:
    if type in 'goal':
        event_details = event['details']
        
        scorer_id = event_details['scoringPlayerId']
        conn = sqlite3.connect('./databases/main.db')
        c = conn.cursor()
        c.execute('SELECT * FROM Players WHERE id = ?', (scorer_id,))
        result = c.fetchone()
        first_name, last_name = 'Unknown', 'Player'
        if result[0] is not None:
            first_name, last_name = result[1], result[2]
        
        team_id = event_details['evenOwnerTeamId']
        
        scoring_team = '???'
        if team_id in home_team:
            scoring_team = home_team[team_id]
        else:
            scoring_team = away_team[team_id]
        
        time_of_goal = event['timeInPeriod']
        
        embed = discord.Embed(
            title=f'{scoring_team} Goal!',
            color=discord.Color(int(nhl.teams_colors.get(scoring_team).lstrip('#'), 16)),
            description=f'Scored by {first_name} {last_name} @ {time_of_goal}'
        )
        
        return embed
    embed = discord.Embed(
        title=f'Event',
        color=discord.Color.green(),
        description=f'Haven\'t handled this type yet'
    )
    
    return embed

#If you know a way to host this image without a bunch of BS. LMK
def create_map(x: int, y: int, game_id: int):
    rink_width = 200
    rink_height = 85

    rink_image = Image.open('./images/Rink.png')

    x_coord, y_coord = x, y

    image_width, image_height = rink_image.size

    image_x = int((x_coord + rink_width / 2) * (image_width / rink_width))
    image_y = int((rink_height / 2 - y_coord) * (image_height / rink_height))

    plt.figure(figsize=(10, 5))
    plt.imshow(rink_image)
    plt.scatter(image_x, image_y, color='black', s=50, marker='D')
    plt.axis('off')

    output_filename = f'./mapimages/{game_id}.png'
    plt.savefig(output_filename, bbox_inches='tight', dpi=300)