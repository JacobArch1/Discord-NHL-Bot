from datetime import datetime, timedelta
import discord
import sqlite3
from collections import defaultdict
import nhl

async def get_help():
    embed = discord.Embed(
        title=f'Help',
        description='Click the buttons to get info about commands',
        color=discord.Color.lighter_gray()
    )
    return embed

async def get_player_stats(first_name: str, last_name: str, player_id: int) -> discord.Embed:
    first_name = first_name.capitalize()
    last_name = last_name.capitalize()
    conn = sqlite3.connect('./databases/main.db')
    c = conn.cursor()
    c.execute('SELECT id FROM Players WHERE first_name == ? AND last_name == ?', (first_name, last_name,))
    player = c.fetchall()
    
    if len(player) > 1 and player_id == None:
        embed=discord.Embed(
            title='Multiple Players Found',
            description='Run this command again with the ID after the name',
            color=discord.Color.lighter_gray()
        )
        for choice in player:
            choice_info = nhl.get_specific_player_info(choice[0])
            team = choice_info.get('currentTeamAbbrev', None)
            emoji = f'<:{team}:{nhl.team_emojis.get(team)}>' if team else ''
            embed.add_field(
                name='',
                value=f'ID: {choice[0]} Team: {emoji} {team}',
                inline=False
            )
        return embed
    
    if not player:
        close_players = []
        embed = discord.Embed(color=discord.Color.lighter_grey())
        c.execute('SELECT * FROM Players WHERE last_name == ?', (last_name,))
        close_players = c.fetchall()
        embed.add_field(
            name='', 
            value='Player Not Found', 
            inline=False
        )
        if close_players:
            embed.add_field(
                name='Did you mean one of these players?', 
                value='', 
                inline=False
            )
        for player in close_players:
            embed.add_field(
                name='', 
                value=f'{player[1]} {player[2]}', 
                inline=False
            )
        return embed
    
    if not player_id:
        player_id = player[0]
    player_info = nhl.get_specific_player_info(player_id[0])
    if 'careerTotals' not in player_info:
        embed = discord.Embed(color=discord.Color.lighter_grey())
        embed.add_field(
            name='', 
            value='No stats available for this player', 
            inline=False
        )
        return embed
    
    if 'regularSeason' in player_info['careerTotals']:
        regular_season_stats = player_info['careerTotals']['regularSeason']
    else:
        regular_season_stats = {}
    
    if 'playoffs' in player_info['careerTotals']:
        playoffs_stats = player_info['careerTotals']['playoffs']
    else:
        playoffs_stats = {}

    table = [
        '```',
        f'{'Stat':<10}{'RegSe':>7}{'PlOff':>7}{'Total':>7}\n',
    ]

    if player_info.get('position', '?') == 'G':
        stats = [
            ('GP:', regular_season_stats.get('gamesPlayed', 0), playoffs_stats.get('gamesPlayed', 0), True),
            ('GS:', regular_season_stats.get('gamesStarted', 0), playoffs_stats.get('gamesStarted', 0), True),
            ('W:', regular_season_stats.get('wins', 0), playoffs_stats.get('wins', 0), True),
            ('L:', regular_season_stats.get('losses', 0), playoffs_stats.get('losses', 0), True),
            ('OT:', regular_season_stats.get('otLosses', 0), playoffs_stats.get('otLosses', 0), True),
            ('SA:', regular_season_stats.get('shotsAgainst', 0), playoffs_stats.get('shotsAgainst', 0), True),
            ('GA:', regular_season_stats.get('goalsAgainst', 0), playoffs_stats.get('goalsAgainst', 0), True),
            ('SO:', regular_season_stats.get('shutouts', 0), playoffs_stats.get('shutouts', 0), True),
            ('A:', regular_season_stats.get('assists', 0), playoffs_stats.get('assists', 0), True),
            ('GAA:', round(regular_season_stats.get('goalsAgainstAvg', 0), 2), round(playoffs_stats.get('goalsAgainstAvg', 0), 2), False),
            ('SV%:', round(regular_season_stats.get('savePctg', 0), 3), round(playoffs_stats.get('savePctg', 0), 3), False),
        ]
    else: 
        stats = [
            ('GP:', regular_season_stats.get('gamesPlayed', 0), playoffs_stats.get('gamesPlayed', 0), True),
            ('G:', regular_season_stats.get('goals', 0), playoffs_stats.get('goals', 0), True),
            ('A:', regular_season_stats.get('assists', 0), playoffs_stats.get('assists', 0), True),
            ('P:', regular_season_stats.get('points', 0), playoffs_stats.get('points', 0), True),
            ('+/-:', regular_season_stats.get('plusMinus', 0), playoffs_stats.get('plusMinus', 0), False),
            ('PIM:', regular_season_stats.get('pim', 0), playoffs_stats.get('pim', 0), True),
            ('PPG:', regular_season_stats.get('powerPlayGoals', 0), playoffs_stats.get('powerPlayGoals', 0), True),
            ('PPP:', regular_season_stats.get('powerPlayPoints', 0), playoffs_stats.get('powerPlayPoints', 0), True),
            ('SHG:', regular_season_stats.get('shorthandedGoals', 0), playoffs_stats.get('shorthandedGoals', 0), True),
            ('SHP:', regular_season_stats.get('shorthandedPoints', 0), playoffs_stats.get('shorthandedPoints', 0), True),
            ('TOI/G:', regular_season_stats.get('avgToi', 0), playoffs_stats.get('avgToi', 0), False),
            ('GWG:', regular_season_stats.get('gameWinningGoals', 0), playoffs_stats.get('gameWinningGoals', 0), True),
            ('OTG:', regular_season_stats.get('otGoals', 0), playoffs_stats.get('otGoals', 0), True),
            ('S:', regular_season_stats.get('shots', 0), playoffs_stats.get('shots', 0), True),
            ('S%:', round(regular_season_stats.get('shootingPctg', 0) * 100, 1), round(playoffs_stats.get('shootingPctg', 0) * 100, 1), False),
            ('FO%:', round(regular_season_stats.get('faceoffWinningPctg', 0) * 100, 1), round(playoffs_stats.get('faceoffWinningPctg', 0) * 100, 1), False)
        ]
    for stat, regular_season, playoffs, add in stats:
        if add:
            total = regular_season + playoffs
        else:
            total = '-'
        table.append(f'{stat:<10}{regular_season:>7}{playoffs:>7}{total:>7}')

    table.append('```')
    formatted_table = '\n'.join(table)

    embed = discord.Embed(
        title='',
        color = discord.Color(int(nhl.teams_colors.get(player_info.get('currentTeamAbbrev', '???'), '#FFFFFF').lstrip('#'), 16))
    )
    embed.set_author(
        name=f'{player_info['firstName']['default']} {player_info['lastName']['default']} #{player_info.get('sweaterNumber', '?')} [{player_info.get('position', '?')}]', 
        icon_url=player_info.get('headshot')
    )
    embed.add_field(
        name='Career Statistics', 
        value=formatted_table, 
        inline=False
    )
    if 'fullTeamName' in player_info:
        team_name = player_info['fullTeamName'].get('default', 'Unknown Team')
    else:
        team_name = 'No NHL Team'
    embed.set_footer(text=f'{team_name}{'PID: ' + str(player_info['playerId']):>50}')
    return embed

async def get_standings(season: str) -> discord.Embed:
    if season == '':
        standings = nhl.get_current_standings()
        pre_title = 'Current'
    else:
        conn = sqlite3.connect('./databases/main.db')
        c = conn.cursor()
        c.execute('SELECT * FROM Standings WHERE id == ?', (season,))
        end_date = c.fetchone()
        if not end_date:
            embed = discord.Embed(color=discord.Color.red())
            embed.add_field(
                name='Error', 
                value='Check Your Season Parameter', 
                inline=False
            )
            return embed
        conn.close()
        end_date = end_date[2]
        standings = nhl.get_standings_by_date(end_date)
        pre_title = season[:4] + '-' + season[4:]
    divisions = defaultdict(list)
    
    for team in standings['standings']:
        division_name = team['divisionName']
        divisions[division_name].append(team)
    divisions = dict(divisions)
    
    for division in divisions:
        divisions[division] = sorted(divisions[division], key=lambda x: x.get('points', 0), reverse=True)
    
    embed = discord.Embed(
        title = pre_title + ' Standings',
        color = discord.Color(0xFFFFFF)    
    )
    
    for division, teams in divisions.items():
        table = [
            '```',
            f'{'Team':<23}{'GP':>4}{'W':>4}{'L':>4}{'OTL':>5}{'P':>4}{'STR':>4}\n',
        ]
        for team in teams:
            games_played = team.get('homeGamesPlayed', 0) + team.get('roadGamesPlayed')
            wins = team.get('wins', 0)
            losses = team.get('losses', 0)
            ot_losses = team.get('homeOtLosses', 0) + team.get('roadOtLosses', 0)
            points = team.get('points', 0)
            streak = f'{team.get('streakCode', '?')}{team.get('streakCount', 0)}'
            
            teamname = f'{nhl.teams.get(team['teamAbbrev']['default'])} {team.get('clinchIndicator', '')}'
            table.append(f'{teamname:<23}{games_played:>4}{wins:>4}{losses:>4}{ot_losses:>5}{points:>4}{streak:>4}')
        table.append('```')
        formatted_table = '\n'.join(table)
        embed.add_field(
            name=division, 
            value=formatted_table[:1024], 
            inline=False
        )
        embed.set_footer(text=f'p - Clinched President\'s Trophy \nx - Clinched Playoff Spot \ny - Clinched Division \nz - Clinched Conference \ne - Eliminated from Playoff Contention')

    return embed

async def get_leaders(category: str) -> discord.Embed:
    category = category.lower()

    if category in ('goals', 'assists', 'points', 'plusminus'):
        if category == ('plusminus'):
            category = 'plusMinus'
        results = nhl.get_current_skaters_stats_leaders(category, 10)
    elif category in ('wins','shutouts','savepctg'):
        if category == ('savepctg'):
            category = 'savePctg'
        results = nhl.get_current_goalie_stats_leaders(category, 10)
    else:
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(
            name='Error', 
            value='Category Not Found.', 
            inline=False
        )
        return embed

    embed = discord.Embed(
        title = 'Leaders for ' + category,
        color = discord.Color(0xFFFFFF)    
    )
    
    table = [
        '```',
        f'{'Name':<20}{'Team':>5}{'Val':>5}\n',
    ]
    for player in results[category]:
        playername = f'{player['firstName']['default']} {player['lastName']['default']}'
        table.append(f'{playername:<20}{player.get('teamAbbrev', 'NUL'):>5}{player.get('value', 0):>5}')
    table.append('```')
    formatted_table = '\n'.join(table)
    embed.add_field(
        name='',
        value=formatted_table[:1024], 
        inline=False
    )

    return embed

async def get_roster(team: str, season: str) -> discord.Embed:
    verified = nhl.verify_team(team)
    if isinstance(verified, discord.Embed):
        return verified
    team_roster = nhl.get_team_roster_by_season(team, season)
    
    if 'goalies' not in team_roster:
        embed = discord.Embed(color=discord.Color.lighter_gray())
        embed.add_field(
            name='Error', 
            value='No roster available', 
            inline=False
        )
        return embed
    
    if season == 'current':
        pre_title = 'Current'
    else:
        pre_title = season[:4] + '-' + season[4:]
    embed = discord.Embed(
        title = f'<:{team}:{nhl.team_emojis.get(team)}> {pre_title} Roster For {team}',
        color = discord.Color(int(nhl.teams_colors.get(team, '#FFFFFF').lstrip('#'), 16))    
    )
    
    table = [
        '```',
        f'{'#':<3}{'Name':<25}{'Ht':>3}{'Wt':>4}\n',
    ]
    for player in team_roster['goalies']:
        playername = f'{player['firstName']['default']} {player['lastName']['default']}'
        table.append(f'{player.get('sweaterNumber', '-'):<3}{playername:<25}{player.get('heightInInches','-'):>3}{player.get('weightInPounds','-'):>4}')
    table.append('```')
    goalie_table = '\n'.join(table)
    embed.add_field(
        name='Goalies', 
        value=goalie_table[:1024], 
        inline=False
    )

    table = [
        '```',
        f'{'#':<3}{'Name':<25}{'Ht':>3}{'Wt':>4}\n',
    ]
    for player in team_roster['forwards']:
        playername = f'{player['firstName']['default']} {player['lastName']['default']}'
        table.append(f'{player.get('sweaterNumber', '-'):<3}{playername:<25}{player.get('heightInInches','-'):>3}{player.get('weightInPounds','-'):>4}')
    table.append('```')
    forward_table = '\n'.join(table)
    embed.add_field(
        name='Forwards', 
        value=forward_table[:1024], 
        inline=False
    )

    table = [
        '```',
        f'{'#':<3}{'Name':<25}{'Ht':>3}{'Wt':>4}\n',
    ]
    for player in team_roster['defensemen']:
        playername = f'{player['firstName']['default']} {player['lastName']['default']}'
        table.append(f'{player.get('sweaterNumber', '-'):<3}{playername:<25}{player.get('heightInInches','-'):>3}{player.get('weightInPounds','-'):>4}')
    table.append('```')
    defense_table = '\n'.join(table)
    embed.add_field(
        name='Defensemen',
          value=defense_table[:1024], 
          inline=False
    )

    return embed

async def get_prospects(team: str) -> discord.Embed:
    verified = nhl.verify_team(team)
    if isinstance(verified, discord.Embed):
        return verified
    
    team_roster = nhl.get_team_prospects(team)
    
    embed = discord.Embed(
        title = f'<:{team}:{nhl.team_emojis.get(team)}> Prospects For {team}',
        color = discord.Color(int(nhl.teams_colors.get(team, '#FFFFFF').lstrip('#'), 16))    
    )
    
    table = [
        '```',
        f'{'#':<3}{'Name':<25}{'Ht':>3}{'Wt':>4}\n',
    ]
    for player in team_roster['goalies']:
        playername = f'{player['firstName']['default']} {player['lastName']['default']}'
        table.append(f'{player.get('sweaterNumber', '-'):<3}{playername:<25}{player.get('heightInInches','-'):>3}{player.get('weightInPounds','-'):>4}')
    table.append('```')
    goalie_table = '\n'.join(table)
    embed.add_field(
        name='Goalies', 
        value=goalie_table[:1024], 
        inline=False
    )

    table = [
        '```',
        f'{'#':<3}{'Name':<25}{'Ht':>3}{'Wt':>4}\n',
    ]
    for player in team_roster['forwards']:
        playername = f'{player['firstName']['default']} {player['lastName']['default']}'
        table.append(f'{player.get('sweaterNumber', '-'):<3}{playername:<25}{player.get('heightInInches','-'):>3}{player.get('weightInPounds','-'):>4}')
    table.append('```')
    forward_table = '\n'.join(table)
    embed.add_field(
        name='Forwards', 
        value=forward_table[:1024], 
        inline=False
    )

    table = [
        '```',
        f'{'#':<3}{'Name':<25}{'Ht':>3}{'Wt':>4}\n',
    ]
    for player in team_roster['defensemen']:
        playername = f'{player['firstName']['default']} {player['lastName']['default']}'
        table.append(f'{player.get('sweaterNumber', '-'):<3}{playername:<25}{player.get('heightInInches','-'):>3}{player.get('weightInPounds','-'):>4}')
    table.append('```')
    defense_table = '\n'.join(table)
    embed.add_field(
        name='Defensemen',
          value=defense_table[:1024], 
          inline=False
    )

    return embed

async def get_playoff_bracket() -> discord.Embed:
    conn = sqlite3.connect('./databases/main.db')
    c = conn.cursor()
    c.execute('SELECT * FROM Standings ORDER BY rowid DESC LIMIT 1')
    season = c.fetchone()
    c.close()
    brackets = nhl.get_playoff_carousel(season[2])
    if 'rounds' not in brackets:
        embed = discord.Embed(color=discord.Color.lighter_gray())
        embed.add_field(
            name='Error', 
            value='No playoff information available', 
            inline=False
        )
        return embed

    embed = discord.Embed(color=discord.Color(0xFFFFFF))

    for round_data in brackets['rounds']:
        round_number = round_data['roundNumber']
        series_list = round_data['series']
        
        table = ['']

        for series in series_list:
            top_seed = series['topSeed']
            bottom_seed = series['bottomSeed']
            table.append(f'<:{top_seed['abbrev']}:{nhl.team_emojis.get(top_seed['abbrev'])}> {top_seed['abbrev']} **{top_seed['wins']} - {bottom_seed['wins']}** {bottom_seed['abbrev']} <:{bottom_seed['abbrev']}:{nhl.team_emojis.get(bottom_seed['abbrev'])}>')
        
        table = '\n'.join(table)
        embed.add_field(
            name=f'Round {round_number}', 
            value=table, 
            inline=False
        )

    return embed

async def get_team_schedule(team: str) -> discord.Embed:
    verified = nhl.verify_team(team)
    if isinstance(verified, discord.Embed):
        return verified
    schedule = nhl.get_week_schedule_now(team)
    embed = discord.Embed(
        title=f'{nhl.teams.get(team)} Week Schedule',
        color = discord.Color(int(nhl.teams_colors.get(team, '#FFFFFF').lstrip('#'), 16))
    )

    empty_list = True

    for game in schedule['games']:
        venue = game['venue']['default']
        est_offset = abs(int(game['easternUTCOffset'].split(":")[0]))
        time = timestamp(game['startTimeUTC'], est_offset, 'f')
        symbol = '🟢' if game['gameState'] in ['LIVE', 'CRIT'] else '🔴' if game['gameState'] in ['OFF', 'FINAL'] else '🔵'

        home_team = game['homeTeam']['abbrev']
        away_team = game['awayTeam']['abbrev']

        embed.add_field(
            name='',
            value=f'<:{away_team}:{nhl.team_emojis.get(away_team)}> {away_team} @ {home_team} <:{home_team}:{nhl.team_emojis.get(home_team)}> {time} {symbol} {venue}',
            inline=False
        )
        empty_list = False
    if empty_list:
        embed.add_field(
            name=f'No Games Scheduled For {team} This week', 
            value=''
        )
        return embed
    return embed

async def get_league_schedule() -> discord.Embed:
    schedule = nhl.get_current_schedule()
    games_today = schedule['gameWeek'][0]['games']
    
    embed = discord.Embed(
        title='Today\'s Games',
        color=discord.Color(0xFFFFFF)
    )
    
    empty_list = True
    
    for game in games_today:
        away_team = game['awayTeam']['abbrev']
        home_team = game['homeTeam']['abbrev']
        est_offset = abs(int(game['easternUTCOffset'].split(":")[0]))
        time = timestamp(game['startTimeUTC'], est_offset, 't')
        symbol = '🟢' if game['gameState'] in ['LIVE', 'CRIT'] else '🔴' if game['gameState'] in ['OFF', 'FINAL'] else '🔵'
        venue = game['venue']['default']

        embed.add_field(
            name='',
            value=f'<:{away_team}:{nhl.team_emojis.get(away_team)}> {away_team} @ {home_team} <:{home_team}:{nhl.team_emojis.get(home_team)}> {time} {symbol} {venue}',
            inline=False
        )
        empty_list = False
    if empty_list:
        embed.add_field(
            name=f'No Games Scheduled Today', 
            value=''
        )
        return embed
    return embed

async def get_live_score(team: str) -> discord.Embed:
    verified = nhl.verify_team(team)
    if isinstance(verified, discord.Embed):
        return verified
    results = nhl.get_team_scoreboard(team)
    games = results['gamesByDate']
    now = datetime.now()
    today = now.strftime('%Y-%m-%d')
    scoreboard = None
    
    for game in games:
        date = game['date']
        game_state = game['games'][0]['gameState']

        if game_state in ['LIVE', 'CRIT', 'FINAL'] or date == today:
            game_id = game['games'][0]['id']
            scoreboard = nhl.get_boxscore(game_id)
            break

    if scoreboard is None:
        embed = discord.Embed(title='Error', color=discord.Color.lighter_gray())
        embed.add_field(
            name='', 
            value='This team is not playing today.'
        )
        return embed
    
    time_remaining = scoreboard.get('clock', {}).get('timeRemaining', 0)
    period = scoreboard.get('periodDescriptor', {}).get('number', 0)
    away_team = scoreboard['awayTeam']['abbrev']
    home_team = scoreboard['homeTeam']['abbrev']
    away_score = scoreboard['awayTeam'].get('score', 0)
    home_score = scoreboard['homeTeam'].get('score', 0)

    if game_state in ['LIVE', 'CRIT']:
        color = discord.Color.green()
    elif game_state in ['FINAL', 'OFF']:
        winner = away_team if away_score > home_score else home_team
        color = int(nhl.teams_colors.get(winner, '#FFFFFF').lstrip('#'), 16)
    else:
        color = discord.Color(0xFFFFFF)
    
    embed = discord.Embed(title=f'P{period:<3}{time_remaining:>36}', color=color)
    embed.add_field(
        name='', 
        value=f'<:{home_team}:{nhl.team_emojis.get(home_team)}> {home_team} **{home_score} - {away_score}** {away_team} <:{away_team}:{nhl.team_emojis.get(away_team)}>'
    )
    embed.set_footer(text=f'{scoreboard['gameState']}')
    return embed

async def get_game_story(team: str, date: str) -> discord.Embed:
    verified = nhl.verify_team(team)
    if isinstance(verified, discord.Embed):
        return verified
    results = nhl.get_team_scoreboard(team)
    games = results['gamesByDate']
    game_id = 0

    for game in games:
        game_date = game['date']
        game_state = game['games'][0]['gameState']

        if date in game_date and game_state in ['OFF','FINAL']:
            game_id = game['games'][0]['id']
            break
    
    if game_id == 0:
        embed = discord.Embed(color=discord.Color.lighter_gray())
        embed.add_field(name='', value='Game could not be found or is still ongoing.', inline=False)
        return embed
    
    game_story = nhl.get_game_story(game_id)
    home_team = game_story['homeTeam']['abbrev']
    away_team = game_story['awayTeam']['abbrev']
    venue = (f'{game_story['venue']['default']}, {game_story['venueLocation']['default']}')
    game_date = game_story['gameDate']
    title = (f'{nhl.teams.get(away_team)} @ {nhl.teams.get(home_team)} ({game_date})\n{venue}')

    home_score = game_story['homeTeam']['score']
    away_score = game_story['awayTeam']['score']
    description = (f'Final Score: <:{home_team}:{nhl.team_emojis.get(home_team)}> **{home_score} - {away_score} ** <:{away_team}:{nhl.team_emojis.get(away_team)}>')

    embed = discord.Embed(
        title=title, 
        color=discord.Color.light_gray(), 
        description=description
    )
    
    goal_highlights = game_story['summary']['scoring']
    for period in goal_highlights:
        descriptor = period['periodDescriptor']['number']
        period_num = (
            '1st' if descriptor == 1 else
            '2nd' if descriptor == 2 else
            '3rd' if descriptor == 3 else
            f'{descriptor}th')
        embed.add_field(
            name=f'\n{period_num} Period Goals',
            value='', 
            inline=False
        )
        goals = period['goals']
        if not goals:
            embed.add_field(
                name='',
                value='No goals scored this period.',
                inline=False
            )
        for goal in goals:
            scoring_team = goal['teamAbbrev']['default']
            goal_scorer = goal['name']['default']
            tog = goal['timeInPeriod']
            strength = goal['strength']
            if goal['assists']:
                assister = goal['assists'][0]['name']['default']
            else:
                assister = 'None'
            video = goal.get('highlightClipSharingUrl', '[No Video]')
            if strength != 'ev':
                strength = strength.upper()
            else:
                strength = ''
            embed.add_field(
                name='', 
                value=f'<:{scoring_team}:{nhl.team_emojis.get(scoring_team)}> [**{scoring_team}** {strength} Goal Scored By: **{goal_scorer}** @ {tog}, Asst: {assister}]({video})', 
                inline=False
            )

    home_team_abbr = game_story['homeTeam']['abbrev']
    away_team_abbr = game_story['awayTeam']['abbrev']
    team_stats = game_story['summary']['teamGameStats']
    table = [
        '```',
        f'{'STAT':<16}{f'{home_team_abbr}':>8}{f'{away_team_abbr}':>5}\n',
    ]
    desired_stats = {'sog': 'SOG', 
                     'powerPlay': 'POWER PLAY GOALS', 
                     'pim': 'PENALTY MINUTES', 
                     'hits': 'HITS', 
                     'blockedShots': 'BLOCKED SHOTS', 
                     'giveaways': 'GIVEAWAYS', 
                     'takeaways': 'TAKEAWAYS'}
    for stat in team_stats:
        if stat['category'] in desired_stats:
            table.append(f'{desired_stats[stat['category']]:<16}{stat['homeValue']:>8}{stat['awayValue']:>5}')
    table.append('```')
    table = '\n'.join(table)
    embed.add_field(
        name='Team Statistics', 
        value=table, 
        inline=False
    )

    three_stars = game_story['summary']['threeStars']
    table = ['']
    for star in three_stars:
        number = star['star']
        number = (
            '1st' if number == 1 else
            '2nd' if number == 2 else
            '3rd' if number == 3 else
            f'{number}th')
        points = f'Points: {star.get('points', 'X')}'
        table.append(f'{number} Star: {star['name']} <:{star['teamAbbrev']}:{nhl.team_emojis.get(star['teamAbbrev'])}> {points if points != 'Points: X' else ''}')
    table.append('')
    table.reverse()
    table = '\n'.join(table)
    embed.add_field(
        name='Three Stars', 
        value=table, 
        inline=False
    )
    return embed

class GameView(discord.ui.View):
    def __init__(self, user_id: str, role: discord.Role, guild: discord.Guild):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.role = role
        self.guild = guild
    
    @discord.ui.button(label='Get Update Role', style=discord.ButtonStyle.success)
    async def add_button_pressed(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.user

        if self.role in member.roles:
            await interaction.response.send_message(content='You already have the role.', ephemeral=True, delete_after=5)
            return

        await member.add_roles(self.role)
        await interaction.response.send_message(content='Done! You will be pinged with updates.', ephemeral=True, delete_after=5)
        
    @discord.ui.button(label='Remove Update Role', style=discord.ButtonStyle.gray)
    async def remove_button_pressed(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.user
        
        if self.role not in member.roles:
            await interaction.response.send_message(content='You do not have the role.', ephemeral=True, delete_after=5)
            return

        await member.remove_roles(self.role)
        await interaction.response.send_message(content='Done! You will no longer get update pings.', ephemeral=True, delete_after=5)
        
    @discord.ui.button(label='📌', style=discord.ButtonStyle.gray)
    async def pin_button_pressed(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message('You don\'t have permission to pin.', ephemeral=True)
            return
        
        content = 'Pinned.'
        if interaction.message.pinned:
            await interaction.message.unpin()
            content = 'Unpinned.'
        else:
            await interaction.message.pin()
            
        await interaction.response.send_message(content=content, ephemeral=True, delete_after=3)


async def startgame(team: str, channel_id: int, guild: discord.Guild, update_modifier: str, ctx) -> discord.Embed:
    verified = nhl.verify_team(team)
    if isinstance(verified, discord.Embed):
        return verified
    
    results = nhl.get_team_scoreboard(team)
    games = results['gamesByDate']
    now = datetime.now()
    today = now.strftime('%Y-%m-%d')
    game_id = 0
    
    conn = sqlite3.connect('./databases/main.db')
    c = conn.cursor()
    
    desired_game = None
    
    for game in games:
        date = game['date']
        game_state = game['games'][0]['gameState']

        if game_state == 'LIVE' or date == today:
            desired_game = game['games'][0]
            break
    if not desired_game:
        embed = discord.Embed(
            title='Error', 
            color=discord.Color.lighter_gray(), 
            description='This team is not playing today.'
        )
        return embed
    if game_state in ['OFF','FINAL']:
        embed = discord.Embed(
            title='Error', 
            color=discord.Color.lighter_gray(), 
            description='This game has ended.'
        )
        return embed
    
    game_id = desired_game['id']
    
    c.execute('SELECT * FROM Update_List WHERE guild_id = ? AND channel_id = ? AND game_id = ?', (guild.id, channel_id, game_id,))
    result = c.fetchone()
    
    if result is not None:
        embed = discord.Embed(
            title='Error', 
            color=discord.Color.lighter_gray(), 
            description='This channel is already recieving updates for this game.'
        )
        return embed
    
    c.execute('INSERT INTO Update_List (guild_id, game_id, game_type, channel_id) VALUES (?, ?, ?, ?)', (guild.id, game_id, 2, channel_id,))
    conn.commit()
    
    away_team = desired_game['awayTeam']['abbrev']
    home_team = desired_game['homeTeam']['abbrev']
    est_offset = abs(int(desired_game['easternUTCOffset'].split(":")[0]))
    time = timestamp(desired_game['startTimeUTC'], est_offset, 't')
    venue = desired_game['venue']['default']
    
    game_msg = discord.Embed(
        title=f'<:{away_team}:{nhl.team_emojis.get(away_team)}> {nhl.teams.get(away_team)} @ <:{home_team}:{nhl.team_emojis.get(home_team)}> {nhl.teams.get(home_team)}',
        description=f'**Start Time**: {time}\n**Arena**: {venue}',
        color=discord.Color.lighter_grey()
    )
    
    if update_modifier == '-u':
        role_name = f'{away_team}v{home_team} Updates'
        role = await guild.create_role(name=role_name, permissions=discord.Permissions.none(), color=discord.Color.lighter_gray())
        c.execute('UPDATE Update_List SET update_role_id = ? WHERE game_id = ? AND channel_id = ?', (role.id, game_id, channel_id))
        conn.commit()
        await ctx.send(embed=game_msg, view=GameView(ctx.author.id, role, guild))
    else:
        await ctx.send(embed=game_msg)
        
    embed = discord.Embed(
        title='Done!', 
        color=discord.Color.green(), 
        description=f'This channel will begin recieving game updates for {team}.'
    )
    
    conn.close()
    return embed

def timestamp(time: str, offset: int, type: chr) -> str:
    dt = datetime.strptime(time, '%Y-%m-%dT%H:%M:%SZ')
    est_time = dt - timedelta(hours=offset)
    
    return (f'<t:{int(est_time.timestamp())}:{type}>')