import sqlite3
import time
from database.sqlite_db import get_connection


DB_PATH="btc_ai.db"



def update_market_status(data):

    conn=get_connection(DB_PATH)

    cursor=conn.cursor()


    cursor.execute("""

    INSERT INTO market_status

    (

    price,
    trend,
    signal,
    position,
    pnl,
    stop_loss,
    take_profit,
    rsi,
    macd,
    atr,
    update_time

    )

    VALUES(?,?,?,?,?,?,?,?,?,?,?)

    """,

    (

    data.get("price",0),

    data.get("trend","neutral"),

    data.get("signal","NONE"),

    data.get("position","NONE"),

    data.get("pnl",0),

    data.get("stop_loss",0),

    data.get("take_profit",0),

    data.get("rsi",0),

    data.get("macd",0),

    data.get("atr",0),

    int(time.time())

    ))


    conn.commit()

    # P1-3: 限制实时状态表大小，保留最近1000条
    try:
        cursor.execute(
            """
            DELETE FROM market_status
            WHERE id NOT IN (
                SELECT id FROM market_status
                ORDER BY id DESC
                LIMIT 1000
            )
            """
        )
        conn.commit()
    except Exception:
        pass

    conn.close()