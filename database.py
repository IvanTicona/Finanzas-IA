import sqlite3

def setup_database() -> sqlite3.Connection:
    """Crea una DB SQLite para un sistema financiero: clientes, activos y transacciones."""
    conn = sqlite3.connect("finance.sqlite")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY,
            full_name TEXT NOT NULL,
            risk_profile TEXT NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assets (
            ticker TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            asset_type TEXT NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY,
            client_id INTEGER,
            ticker TEXT,
            tx_type TEXT NOT NULL,
            quantity REAL NOT NULL,
            price_usd REAL NOT NULL,
            FOREIGN KEY (client_id) REFERENCES clients (id),
            FOREIGN KEY (ticker) REFERENCES assets (ticker)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS queries (
            id TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            result TEXT
        );
    """)

    cursor.executemany("INSERT OR IGNORE INTO clients VALUES (?, ?, ?)", [
        (1, "Elena M.", "Aggressive"), (2, "Carlos V.", "Conservative"), (3, "Sofia R.", "Moderate")
    ])
    cursor.executemany("INSERT OR IGNORE INTO assets VALUES (?, ?, ?)", [
        ("AAPL", "Apple Inc.", "Stock"), ("BTC", "Bitcoin", "Crypto"), ("VTI", "Vanguard ETF", "ETF")
    ])
    cursor.execute("SELECT id FROM queries WHERE id = 'base-seed-v1'")
    if cursor.fetchone() is None:
        cursor.executemany("INSERT INTO transactions (client_id, ticker, tx_type, quantity, price_usd) VALUES (?, ?, ?, ?, ?)", [
            (1, "BTC", "BUY", 0.5, 45000.0), (3, "AAPL", "BUY", 20, 180.0)
        ])
        cursor.execute("INSERT INTO queries VALUES ('base-seed-v1', 'seeded', NULL)")

    conn.commit()
    return conn
