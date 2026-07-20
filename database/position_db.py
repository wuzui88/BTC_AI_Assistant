import sqlite3
import time



class PositionDB:


    def __init__(self, db_path="btc_ai.db"):


        self.conn = sqlite3.connect(

            db_path,

            timeout=30,

            check_same_thread=False

        )
        self.conn.execute(
            "PRAGMA journal_mode=WAL;"
        )

        self.conn.execute("PRAGMA busy_timeout=30000;")
        self.conn.commit()


        self.last_status_update = 0
        self.status_update_interval = 5

        self.create_table()




    # =====================
    # 创建表
    # =====================

    def create_table(self):


        # 当前持仓表
        self.conn.execute("""

        CREATE TABLE IF NOT EXISTS positions(


            id INTEGER PRIMARY KEY AUTOINCREMENT,


            direction TEXT,


            side TEXT,


            entry REAL,


            stop_loss REAL,


            take_profit REAL,


            size_btc REAL,


            contracts INTEGER,


            leverage INTEGER,


            open_time INTEGER


        )

        """)



        # Dashboard实时状态表

        self.conn.execute("""

        CREATE TABLE IF NOT EXISTS position_status(

            id INTEGER PRIMARY KEY AUTOINCREMENT,


            direction TEXT,


            entry REAL,


            current REAL,


            pnl REAL,


            size_btc REAL,


            stop_loss REAL,


            take_profit REAL,


            hold_minutes REAL,


            max_profit REAL,


            max_drawdown REAL,


            update_time INTEGER

        )

        """)



        self.conn.commit()





    # =====================
    # 保存开仓持仓
    # =====================

    def save_position(
        self,
        position
    ):


        self.clear_position()



        self.conn.execute(

        """

        INSERT INTO positions

        (

        direction,

        side,

        entry,

        stop_loss,

        take_profit,

        size_btc,

        contracts,

        leverage,

        open_time

        )

        VALUES(?,?,?,?,?,?,?,?,?)

        """,

        (

        position["direction"],


        position["side"],


        position["entry"],


        position["stop_loss"],


        position["take_profit"],


        position["size_btc"],


        position["contracts"],


        position.get(
            "leverage",
            30
        ),


        int(time.time())

        )


        )


        self.conn.commit()





    # =====================
    # 获取当前持仓
    # =====================

    def get_position(self):


        cursor=self.conn.cursor()


        row=cursor.execute(

        """

        SELECT *

        FROM positions

        LIMIT 1

        """

        ).fetchone()



        if row is None:

            return None



        return {


            "id":row[0],

            "direction":row[1],

            "side":row[2],

            "entry":row[3],

            "stop_loss":row[4],

            "take_profit":row[5],

            "size_btc":row[6],

            "contracts":row[7],

            "leverage":row[8],

            "open_time":row[9]

        }






    # =====================
    # Dashboard读取当前持仓
    # =====================

    def get_dashboard_position(self):


        position = self.get_position()


        if position is None:

            return {

                "position": "NONE",
                "direction": "NONE",
                "entry": 0,
                "current": 0,
                "pnl": 0,
                "size_btc": 0,
                "stop_loss": 0,
                "take_profit": 0

            }


        return {

            "position": position.get("direction", "NONE"),
            "direction": position.get("direction", "NONE"),
            "entry": position.get("entry", 0),
            "current": position.get("entry", 0),
            "pnl": 0,
            "size_btc": position.get("size_btc", 0),
            "stop_loss": position.get("stop_loss", 0),
            "take_profit": position.get("take_profit", 0)

        }



    # =====================
    # 删除持仓
    # =====================

    def clear_position(self):


        self.conn.execute(

        """

        DELETE FROM positions

        """

        )


        self.conn.commit()





    # =====================
    # 更新Dashboard实时持仓
    # =====================

    def update_status(
        self,
        data
    ):

        # P1-3: 限制实时状态写入频率，避免每个tick写SQLite
        now = time.time()

        if now - self.last_status_update < self.status_update_interval:
            return

        self.last_status_update = now

        self.conn.execute(

        """

        INSERT INTO position_status

        (

        direction,

        entry,

        current,

        pnl,

        size_btc,

        stop_loss,

        take_profit,

        hold_minutes,

        max_profit,

        max_drawdown,

        update_time

        )

        VALUES(?,?,?,?,?,?,?,?,?,?,?)

        """,

        (

        data.get(
            "direction",
            "NONE"
        ),


        data.get(
            "entry",
            0
        ),


        data.get(
            "current",
            0
        ),


        data.get(
            "pnl",
            0
        ),


        data.get(
            "size_btc",
            0
        ),


        data.get(
            "stop_loss",
            0
        ),


        data.get(
            "take_profit",
            0
        ),


        data.get(
            "hold_minutes",
            0
        ),


        data.get(
            "max_profit",
            0
        ),


        data.get(
            "max_drawdown",
            0
        ),


        int(time.time())

        )

        )


        self.conn.commit()