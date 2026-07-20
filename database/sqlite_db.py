import sqlite3
import os
import time


# =========================
# 数据库路径
# =========================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DB_PATH = os.path.join(
    BASE_DIR,
    "btc_ai.db"
)



# =========================
# 统一数据库连接
# =========================

def get_connection(db_path=DB_PATH):

    conn = sqlite3.connect(
        db_path,
        timeout=30,
        check_same_thread=False
    )

    conn.execute(
        "PRAGMA journal_mode=WAL;"
    )

    conn.execute(
        "PRAGMA busy_timeout=30000;"
    )

    return conn



# =========================
# SQLite数据库类
# =========================

class SQLiteDB:


    def __init__(
        self,
        db_path=DB_PATH
    ):

        self.db_path = db_path

        self.conn = get_connection(
            db_path
        )

        self.create_tables()



    # =====================
    # 创建数据表
    # =====================

    def create_tables(self):

        cursor = self.conn.cursor()


        # K线表

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS candles
            (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                timestamp INTEGER,

                open REAL,

                high REAL,

                low REAL,

                close REAL,

                volume REAL

            )
            """
        )


        # 市场状态表

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS market_status
            (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                price REAL,

                trend TEXT,

                signal TEXT,

                rsi REAL,

                macd REAL,

                atr REAL,

                update_time INTEGER

            )
            """
        )


        # 持仓表

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS positions
            (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                direction TEXT,

                side TEXT,

                entry REAL,

                current REAL,

                pnl REAL,

                stop_loss REAL,

                take_profit REAL,

                size_btc REAL,

                contracts INTEGER,

                leverage INTEGER,

                hold_minutes REAL,

                max_profit REAL,

                max_drawdown REAL,

                open_time INTEGER

            )
            """
        )


        self.conn.commit()



    # =====================
    # 执行SQL
    # =====================

    def execute(
        self,
        sql,
        params=()
    ):

        cursor = self.conn.cursor()

        cursor.execute(
            sql,
            params
        )

        self.conn.commit()

        return cursor



    # =====================
    # 查询一条
    # =====================

    def fetchone(
        self,
        sql,
        params=()
    ):

        cursor = self.conn.cursor()

        cursor.execute(
            sql,
            params
        )

        return cursor.fetchone()



    # =====================
    # 查询多条
    # =====================

    def fetchall(
        self,
        sql,
        params=()
    ):

        cursor = self.conn.cursor()

        cursor.execute(
            sql,
            params
        )

        return cursor.fetchall()



    # =================================================
    # 保存K线
    # 兼容:
    #
    # timestamp/open/high/low/close/volume
    #
    # time/open/high/low/close
    #
    # OKX:
    # ts/o/h/l/c/v
    # =================================================

    def save_kline(
        self,
        candle
    ):


        timestamp = (

            candle.get("timestamp")

            or candle.get("time")

            or candle.get("ts")

            or int(time.time())

        )


        open_price = (

            candle.get("open")

            or candle.get("o")

        )


        high_price = (

            candle.get("high")

            or candle.get("h")

        )


        low_price = (

            candle.get("low")

            or candle.get("l")

        )


        close_price = (

            candle.get("close")

            or candle.get("c")

        )


        volume = (

            candle.get("volume")

            or candle.get("v")

            or 0

        )


        if close_price is None:

            return



        self.execute(

            """
            INSERT INTO candles
            (

                timestamp,

                open,

                high,

                low,

                close,

                volume

            )

            VALUES(?,?,?,?,?,?)

            """,

            (

                int(timestamp),

                float(open_price),

                float(high_price),

                float(low_price),

                float(close_price),

                float(volume)

            )

        )



    # =================================================
    # 加载历史K线
    # =================================================

    def load_history(
        self,
        limit=300
    ):


        rows = self.fetchall(

            """
            SELECT

                timestamp,

                open,

                high,

                low,

                close,

                volume


            FROM candles


            ORDER BY timestamp DESC


            LIMIT ?

            """,

            (
                limit,
            )

        )


        rows.reverse()


        history = []


        for row in rows:


            history.append(

                {

                    "timestamp": row[0],

                    "open": row[1],

                    "high": row[2],

                    "low": row[3],

                    "close": row[4],

                    "volume": row[5]

                }

            )


        return history



    # =================================================
    # 获取最新价格
    # =================================================

    def get_latest_price(self):


        row = self.fetchone(

            """
            SELECT close

            FROM candles

            ORDER BY timestamp DESC

            LIMIT 1

            """

        )


        if row:

            return row[0]


        return 0



    # =====================
    # 关闭连接
    # =====================

    def close(self):

        if self.conn:

            self.conn.close()



# =========================
# 初始化数据库
# =========================

def init_database():

    db = SQLiteDB()

    db.close()



if __name__ == "__main__":

    init_database()

    print(
        "数据库初始化完成:",
        DB_PATH
    )