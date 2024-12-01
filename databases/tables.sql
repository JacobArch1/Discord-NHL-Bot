CREATE TABLE IF NOT EXISTS User_Economy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    user_name TEXT NOT NULL,
    balance REAL NOT NULL DEFAULT 0.0,
    num_bets INTEGER NOT NULL DEFAULT 0,
    num_wins INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Jackpot (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    pot REAL NOT NULL DEFAULT 10000,
    cashout_odds REAL NOT NULL DEFAULT 0.1,
    num_tips INTEGER NOT NULL DEFAULT 0,
    last_tipper TEXT NOT NULL DEFAULT 'Nobody Yet',
    last_tipper_amount REAL NOT NULL DEFAULT 0.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Betting_Pool (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER NOT NULL,
    game_type INTEGER NOT NULL,
    guild_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    team TEXT NOT NULL,
    wager REAL NOT NULL DEFAULT 0.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Bet_History (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER NOT NULL,
    game_type INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    guild_id INTEGER NOT NULL,
    team TEXT NOT NULL,
    wager REAL,
    payout REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Current_Games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER NOT NULL,
    away_team TEXT NOT NULL,
    home_team TEXT NOT NULL,
    game_type INTEGER NOT NULL,
    start_date DATE NOT NULL,
    start_time TIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Update_List(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    game_id INTEGER NOT NULL,
    game_type INTEGER NOT NULL,
    channel_id INTEGER NOT NULL,
    last_event_id INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Server_Settings(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roles_enabled INTEGER NOT NULL DEFAULT 0,
    update_roles_enabled INTEGER NOT NULL DEFAULT 0,
    create_game_channels INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Players(
    id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Standings(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL
);