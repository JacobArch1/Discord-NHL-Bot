import nhl
import datetime
import sqlite3
import eventresponse
import discord
import os

async def update_games(bot):
    conn = sqlite3.connect('./databases/main.db')
    c = conn.cursor()
    c.execute('SELECT game_id FROM Current_Games')
    games_list = c.fetchall()
    for game in games_list:
        game_id = game[0]
        results = nhl.get_boxscore(game_id)
        
        state = results['gameState']
        game_type = results['gameType']
        if state == 'OFF':
            c.execute('DELETE FROM Current_Games WHERE game_id = ?', (game_id,))
            conn.commit()
            c.execute('DELETE FROM Update_List WHERE game_id = ?', (game_id,))            
            conn.commit()
            await remove_maps(game_id)
        else: 
            if state == 'FINAL':
                await cashout(conn, results, game_id, game_type)
                await end_poker_games(conn, results, game_id, bot)
            c.execute('SELECT * FROM Update_List WHERE game_id = ?', (game_id,))
            results = c.fetchall()
            channel_ids = [row[4] for row in results]
            await eventresponse.send_events(game_id, channel_ids, bot)
    
    c.execute('SELECT * FROM Current_Games')
    games = c.fetchall()
    now = datetime.datetime.now()
    if not games and now.hour >= 12:
        await get_todays_games(conn)
    conn.close()

async def cashout(conn, results: dict, game_id: int, game_type: int):
    c = conn.cursor()
    c.execute('SELECT * FROM Betting_Pool WHERE game_id == ?', (game_id,))
    bets = c.fetchall()

    if game_type == 1:
        multiplier = 1.25
    else:
        multiplier = game_type

    home_score = results['homeTeam']['score']
    away_score = results['awayTeam']['score']

    if home_score > away_score:
        winner = results['homeTeam']['abbrev']
    else:
        winner = results['awayTeam']['abbrev']

    for bet in bets:
        bet_id = bet[0]
        guild_id = bet[3]
        user_id = bet[4]
        team = bet[5] 
        wager = bet[6]

        payout = 0
        bet_won = (team == winner)
        if bet_won:
            payout = wager * multiplier

        c.execute('UPDATE User_Economy SET balance = balance + ? WHERE guild_id = ? AND user_id = ?', (payout, guild_id, user_id,))
        c.execute('INSERT INTO Bet_History (game_id, game_type, user_id, guild_id, team, wager, payout) VALUES (?, ?, ?, ?, ?, ?, ?)', (game_id, game_type, user_id, guild_id, team, wager, payout,))
        c.execute('DELETE FROM Betting_Pool WHERE id = ?', (bet_id,))
        conn.commit()
        
async def end_poker_games(conn, results: dict, game_id: int, bot):
    c = conn.cursor()
    c.execute('SELECT * FROM Poker_Pool WHERE game_id == ?', (game_id,))
    games = c.fetchall()
    
    home_team = results['homeTeam']['abbrev']
    home_score = results['homeTeam']['score']
    away_team = results['awayTeam']['abbrev']
    away_score = results['awayTeam']['score']

    if home_score > away_score:
        winning_team = home_team
    else:
        winning_team = away_team
        
    for game in games:
        poker_game_id = game[0]
        guild_id = game[2]
        user_id = game[4]
        opponent_id = game[5]
        user_team = game[6]
        opponent_pot = game[7]
        user_pot = game[8]
        opponent_pot = game[9]
        full_pot = opponent_pot + user_pot
        
        winning_msg = discord.Embed(
            title='Poker Game Ended.',
            description=f'You Won: {full_pot} 💵\n\n**Game Result:**\n<:{home_team}:{nhl.team_emojis.get(home_team)}> {home_team}: {home_score}\n<:{away_team}:{nhl.team_emojis.get(away_team)}> {away_team}: {away_score}',
            color=discord.Color.green(),
        )
        
        losing_msg = discord.Embed(
            title='Poker Game Ended.',
            description=f'You Lost\n\n**Game Result:**\n<:{home_team}:{nhl.team_emojis.get(home_team)}> {home_team}: {home_score}\n<:{away_team}:{nhl.team_emojis.get(away_team)}> {away_team}: {away_score}',
            color=discord.Color.red(),
        )
        
        opponent_user = await bot.fetch_user(opponent_id)
        user = await bot.fetch_user(user_id)
        
        if user_team == winning_team:
            await user.send(embed=winning_msg)
            await opponent_user.send(embed=losing_msg)
            c.execute('UPDATE User_Economy SET balance = balance + ? WHERE guild_id = ? AND user_id = ?', (full_pot, guild_id, user_id,))
        else:
            await user.send(embed=losing_msg)
            await opponent_user.send(embed=winning_msg)
            c.execute('UPDATE User_Economy SET balance = balance + ? WHERE guild_id = ? AND user_id = ?', (full_pot, guild_id, opponent_id,))
        
        c.execute('DELETE FROM Poker_Pool WHERE id = ?', (poker_game_id,))
        conn.commit()

async def remove_maps(game_id):
    map_path = './images/Maps'
    for item in os.listdir(map_path):
        if item == f"{game_id}.png":
            item_path = os.path.join(map_path, item)
            os.unlink(item_path)

async def get_todays_games(conn):
    c = conn.cursor()
    c.execute('DELETE FROM Current_Games')
    conn.commit()

    schedule = nhl.get_current_schedule()
    games_today = schedule['gameWeek'][0]['games']
    for game in games_today:
        game_id = game['id']
        game_type = game['gameType']
        away_team = game['awayTeam']['abbrev']
        home_team = game['homeTeam']['abbrev']
        game_state = game['gameState']
        est_offset = abs(int(game['easternUTCOffset'].split(":")[0]))

        dt = datetime.datetime.strptime(game['startTimeUTC'], '%Y-%m-%dT%H:%M:%SZ')
        updated_datetime_obj = dt - datetime.timedelta(hours=est_offset)

        est_date = str(updated_datetime_obj.date())
        est_time = str(updated_datetime_obj.time())

        if game_state not in ['OFF', 'FINAL']:
            c.execute(
                'INSERT INTO Current_Games (game_id, game_type, away_team, home_team, start_date, start_time) VALUES (?, ?, ?, ?, ?, ?)',
                (game_id, game_type, away_team, home_team, est_date, est_time)
            )
            conn.commit()

async def fetch_players(season: int):
    conn = sqlite3.connect('./databases/main.db')
    c = conn.cursor()
    conn.commit()
    for team in nhl.teams:
        results = nhl.get_team_roster_by_season(team, season)
        if 'error' in results:
            continue
        forwards_info = await extract_player_info(results.get('forwards', []))
        defensemen_info = await extract_player_info(results.get('defensemen', []))
        goalies_info = await extract_player_info(results.get('goalies', []))
        all_players_info = forwards_info + defensemen_info + goalies_info
        for player in all_players_info:
            c = conn.cursor()
            c.execute('SELECT * FROM Players WHERE id = ?', (player['id'],))
            if c.fetchone():
                continue
            else:
                c.execute('INSERT INTO Players (id, first_name, last_name) VALUES (?, ?, ?)', (player['id'], player['firstName'], player['lastName']))
                conn.commit()
    conn.close()
    nhl.log_data(f'Recent Players Fetched')

async def extract_player_info(players):
    extracted_info = []
    for player in players:
        player_info = {
            'id': player['id'],
            'firstName': player['firstName']['default'],
            'lastName': player['lastName']['default']
        }
        extracted_info.append(player_info)
    return extracted_info

async def fetch_standings():
    conn = sqlite3.connect('./databases/main.db')
    c = conn.cursor()
    c.execute('DELETE FROM Standings')
    results = nhl.get_standings_for_each_season()
    seasons = results['seasons']
    c = conn.cursor()
    for season in seasons:
        season_id = season.get('id', 0)
        start_date = season.get('standingsStart', '')
        end_date = season.get('standingsEnd', '')
        c.execute('INSERT INTO Standings (id, start_date, end_date) VALUES (?, ?, ?)', (season_id, start_date, end_date))
        conn.commit()
    conn.close()
    nhl.log_data(f'New Standings Fetched')