import matplotlib.pyplot as plt
from PIL import Image
import nhl
import discord
import sqlite3

async def send_events(game_id: int, update_list: list, bot):
    results = nhl.get_play_by_play(game_id)
    
    away_team_id = results['awayTeam']['id']
    away_team_abbrev = results['awayTeam']['abbrev']
    away_score = results['awayTeam']['score']
    away_team = {'id' : away_team_id, 'abbrev': away_team_abbrev}
    
    home_team_id = results['homeTeam']['id']
    home_team_abbrev = results['homeTeam']['abbrev']
    home_score = results['homeTeam']['score']
    home_team = {'id': home_team_id, 'abbrev': home_team_abbrev}
    
    events = results['plays']
    
    if events:
        event = events[-1]
    else:
        return
    
    event_id = event['eventId']
    event_type = event['typeDescKey']
    
    if event_type in 'faceoff':
        event = events[-2]
    
    desired_events = {'period-start', 'period-end', 'goal', 'penalty', 'game-end'}
    
    if event_type not in desired_events:
        return
    
    embed = craft_embed(event, event_type, away_team, home_team, away_score, home_score)
    conn = sqlite3.connect('./databases/main.db')
    
    for channel_id in update_list:
        
        c = conn.cursor()
        c.execute('SELECT last_event_id FROM Update_List WHERE channel_id = ? AND game_id = ?', (channel_id, game_id,))
        last_event_id = c.fetchone()

        if event_id != last_event_id[0]:
            channel = bot.get_channel(channel_id)
            if channel:
                c.execute('UPDATE Update_List SET last_event_id = ? WHERE channel_id = ? AND game_id = ?', (event_id, channel_id, game_id,))
                conn.commit()
                await channel.send(embed=embed)
    conn.close()

def craft_embed(event: dict, type: str, away_team: dict, home_team: dict, away_score: int, home_score: int) -> discord.Embed:
    event_details = event.get('details', '')
    if type in 'goal':
        scorer_id = event_details['scoringPlayerId']
        conn = sqlite3.connect('./databases/main.db')
        c = conn.cursor()
        c.execute('SELECT * FROM Players WHERE id = ?', (scorer_id,))
        result = c.fetchone()
        first_name, last_name = 'Unknown', 'Player'
        if result[0] is not None:
            first_name, last_name = result[1], result[2]
        conn.close()
        
        team_id = event_details['eventOwnerTeamId']
        
        scoring_team = '???'
        if team_id == home_team['id']:
            scoring_team = home_team['abbrev']
        elif team_id == away_team['id']:
            scoring_team = away_team['abbrev']
        
        time_of_goal = event['timeInPeriod']
        
        embed = discord.Embed(
            title=f'{nhl.teams.get(scoring_team, 'Unknown Team')} Goal!',
            color=discord.Color(int(nhl.teams_colors.get(scoring_team).lstrip('#'), 16)),
            description=f'Scored by **{first_name} {last_name}** @ {time_of_goal}'
        )
        
        return embed
    elif type in ['period-start','period-end']:
        if type == 'period-start':
            title = 'Period has started.'
        else:
            title = 'Period has ended.'
        descriptor = event['periodDescriptor']['number']
        period_num = (
            '1st' if descriptor == 1 else
            '2nd' if descriptor == 2 else
            '3rd' if descriptor == 3 else
            f'{descriptor}th')
        embed = discord.Embed(
            title=f'{period_num} {title}',
            color=discord.Color(int('#000000'.lstrip('#'), 16)),
            description=f'-- Score --\n{home_team['abbrev']}: {home_score}\n{away_team['abbrev']}: {away_score}'
        )
        
        return embed
    elif type in ['penalty']:
        offender_id = event_details['committedByPlayerId']
        conn = sqlite3.connect('./databases/main.db')
        c = conn.cursor()
        c.execute('SELECT * FROM Players WHERE id = ?', (offender_id,))
        result = c.fetchone()
        first_name, last_name = 'Unknown', 'Player'
        if result[0] is not None:
            first_name, last_name = result[1], result[2]
        conn.close()
        
        team_id = event_details['eventOwnerTeamId']
        
        offending_team = '???'
        if team_id == home_team['id']:
            offending_team = home_team['abbrev']
        elif team_id == away_team['id']:
            offending_team = away_team['abbrev']
        
        time_of_penalty = event['timeInPeriod']
        penalty_type = event_details.get('descKey','???').replace('-', ' ')
        duration = event_details.get('duration','')
        
        embed = discord.Embed(
            title=f'{nhl.teams.get(offending_team, 'Unknown Team')} Penalty.',
            color=discord.Color(int(nhl.teams_colors.get(offending_team).lstrip('#'), 16)),
            description=f'{first_name} {last_name} For **{penalty_type.upper()}** @ {time_of_penalty}\nDuration: {duration} Minutes.'
        )
        
        return embed
    elif type in ['game-end']:
        winning_team = away_team['abbrev']
        if home_score > away_score:
            winning_team = home_team['abbrev']
        
        descriptor = event['periodDescriptor']['periodType']
        period_type = (
            'regulation' if descriptor == 'REG' else
            'overtime' if descriptor == 'OT' else
            'the shootout' if descriptor == 'SO' else
            f'???')
        
        embed = discord.Embed(
            title=f'{nhl.teams.get(winning_team)} win in {period_type}!',
            color=discord.Color(int(nhl.teams_colors.get(winning_team).lstrip('#'), 16)),
            description=f'-- Final Score --\n{home_team["abbrev"]}: {home_score}\n{away_team["abbrev"]}: {away_score}'
        )
        
        return embed
        
    embed = discord.Embed(
        title=f'{type} Event',
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