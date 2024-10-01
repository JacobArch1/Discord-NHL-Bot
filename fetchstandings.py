import sqlite3
import time
import pandas as pd
import nhl

def fetch_standings():
    conn = sqlite3.connect('standings.db')
    c = conn.cursor()
    c.execute("DELETE FROM standings")
    try:
        time.sleep(0.1)
        results = nhl.get_standings_for_each_season()
        if 'error' in results:
            print(f'Error fetching standings: {results["error"]}')
        else:
            insert_standings(conn, results['seasons'])
    except Exception as e:
        print(f'An error occurred: {e}')
    finally:
        convert_to_csv()
        print('Standings fetched and saved successfully')
        conn.close()

def insert_standings(conn, seasons):
    try:
        c = conn.cursor()
        for season in seasons:
            season_id = season.get('id', 0)
            start_date = season.get('standingsStart', '')
            end_date = season.get('standingsEnd', '')
            print(f'Inserting standings for season {season_id}')
            c.execute('''INSERT INTO standings (id, startDate, endDate) 
                         VALUES (?, ?, ?)''', (season_id, start_date, end_date))
        conn.commit()
    except sqlite3.Error as e:
        print(f'Database error: {e}')
    except Exception as e:
        print(f'An error occurred: {e}')

def convert_to_csv():
    conn = sqlite3.connect('standings.db')
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        for table_name in tables:
            table_name = table_name[0]
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
            df.to_csv(f"{table_name}.csv", index=False)
    except Exception as e:
        print(f'An error occurred while converting to CSV: {e}')
    finally:
        conn.close()

fetch_standings()