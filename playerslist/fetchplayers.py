import nhl
import time
import sqlite3
import pandas as pd

def fetch_players(season: int):
    conn = sqlite3.connect('players.db')
    try:
        create_player_table(conn)
        for team in nhl.teams:
            time.sleep(0.1)
            print(f'Fetching players for {team} in season {season}')
            results = nhl.get_team_roster_by_season(team, season)
            if 'error' in results:
                print(f'Error fetching players for {team}')
                continue
            forwards_info = extract_player_info(results.get('forwards', []))
            defensemen_info = extract_player_info(results.get('defensemen', []))
            goalies_info = extract_player_info(results.get('goalies', []))
            all_players_info = forwards_info + defensemen_info + goalies_info
            for player in all_players_info:
                c = conn.cursor()
                c.execute('''SELECT * FROM players WHERE id = ?''', (player['id'],))
                if c.fetchone():
                    continue
                else:
                    insert_player(conn, player)
    finally:
        convert()
        conn.close()

def extract_player_info(players):
    extracted_info = []
    for player in players:
        player_info = {
            'id': player['id'],
            'firstName': player['firstName']['default'],
            'lastName': player['lastName']['default']
        }
        extracted_info.append(player_info)
    return extracted_info

def create_player_table(conn):
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS players (id INTEGER PRIMARY KEY, firstName TEXT, lastName TEXT)''')
    conn.commit()

def insert_player(conn, player):
    c = conn.cursor()
    c.execute('''INSERT INTO players (id, firstName, lastName) VALUES (?, ?, ?)'''
              , (player['id'], player['firstName'], player['lastName']))
    conn.commit()

def convert():
    conn = sqlite3.connect('players.db')
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    for table_name in tables:
        table_name = table_name[0]
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        df.to_csv(f"{table_name}.csv", index=False)

if __name__ == '__main__':
    fetch_players()
    print("All Players Fetched! :)")
