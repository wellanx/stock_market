import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS stocks (
        ticker TEXT PRIMARY KEY,
        current_price REAL NOT NULL,
        drift REAL NOT NULL,
        volatility REAL NOT NULL
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_portfolio (
        ticker TEXT PRIMARY KEY,
        quantity INTEGER NOT NULL,
        total_cost REAL NOT NULL,
        avg_purc_price REAL NOT NULL,
        current_price REAL,
        percentage_change REAL
    )
    """)

cursor.execute("""
    CREATE TABLE IF NOT EXISTS player (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        balance REAL NOT NULL
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
    INSERT OR IGNORE INTO player (id, balance)
    VALUES (?, ?)
""", (1, 10_000.00))
conn.commit()