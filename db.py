import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute("PRAGMA foreign_keys = ON")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS stocks (
        ticker TEXT PRIMARY KEY,
        current_price REAL NOT NULL,
        drift REAL NOT NULL,
        volatility REAL NOT NULL
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        balance REAL NOT NULL,
        is_bot INTEGER NOT NULL DEFAULT 0
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_portfolio (
        player_id INTEGER NOT NULL,
        ticker TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        total_cost REAL NOT NULL,
        avg_purc_price REAL NOT NULL,
        current_price REAL,
        percentage_change REAL,

        PRIMARY KEY (player_id, ticker),

        FOREIGN KEY (player_id) REFERENCES players(id),
        FOREIGN KEY (ticker) REFERENCES stocks(ticker)
    )
    """)

cursor.execute("""
    CREATE TABLE IF NOT EXISTS transaction_history (
        transaction_type TEXT NOT NULL,
        ticker TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        total_amount REAL NOT NULL,
        date INTEGER NOT NULL
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS game_state (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        current_day INTEGER NOT NULL DEFAULT 1
    )
""")

cursor.executemany("""
    INSERT OR IGNORE INTO stocks (ticker, current_price, drift, volatility)
    VALUES (?, ?, ?, ?)
    """, [
        ('AI', 2500.00, 0.15, 0.45),
        ('CYBERNETICS', 2000.00, 0.12, 0.35),
        ('GAMEDEV', 1000.00, 0.10, 0.50),
        ('ROCKET_ENGINEERING', 3000, 0.08, 0.30),
        ('MECHANICAL_ENGINEERING', 2800, 0.06, 0.18),
        ('CHIP_PRODUCTION', 2700, 0.10, 0.28)
    ]
)

cursor.execute("""
    INSERT OR IGNORE INTO game_state (id, current_day)
    VALUES (1, 1)
""")

conn.commit()