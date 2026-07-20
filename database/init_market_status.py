import sqlite3


DB_PATH = "btc_ai.db"


conn = sqlite3.connect(DB_PATH)

cursor = conn.cursor()


cursor.execute("""

CREATE TABLE IF NOT EXISTS market_status (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    price REAL DEFAULT 0,

    trend TEXT DEFAULT 'WAIT',

    signal TEXT DEFAULT 'WAIT',

    position TEXT DEFAULT 'NONE',

    pnl REAL DEFAULT 0,

    stop_loss REAL DEFAULT 0,

    take_profit REAL DEFAULT 0,

    rsi REAL DEFAULT 0,

    macd REAL DEFAULT 0,

    atr REAL DEFAULT 0,

    update_time INTEGER

)

""")


conn.commit()

conn.close()


print("market_status表创建完成")