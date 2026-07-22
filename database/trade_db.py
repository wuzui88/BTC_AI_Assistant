import sqlite3
import time



class TradeDB:


    def __init__(self, db_path="btc_ai.db"):


        self.conn = sqlite3.connect(

            db_path,

            check_same_thread=False

        )


        self.create_table()

        self.upgrade_table()





    # =====================
    # 创建交易表
    # =====================

    def create_table(self):


        sql = """

        CREATE TABLE IF NOT EXISTS trades (

            id INTEGER PRIMARY KEY AUTOINCREMENT,


            direction TEXT,


            entry REAL,


            exit REAL,


            size_btc REAL,


            contracts INTEGER,


            pnl REAL,


            reason TEXT,


            open_time INTEGER,


            close_time INTEGER,


            hold_minutes REAL,


            max_profit REAL,


            max_drawdown REAL

        )

        """


        self.conn.execute(sql)

        self.conn.commit()





    # =====================
    # 数据库升级
    # =====================

    def upgrade_table(self):


        cursor = self.conn.cursor()


        cursor.execute(
            "PRAGMA table_info(trades)"
        )


        columns = [

            row[1]

            for row in cursor.fetchall()

        ]



        new_columns = {


            "hold_minutes":

            "REAL",


            "max_profit":

            "REAL",


            "max_drawdown":

            "REAL"

        }



        for name, dtype in new_columns.items():


            if name not in columns:


                self.conn.execute(

                    f"""

                    ALTER TABLE trades

                    ADD COLUMN {name} {dtype}

                    """

                )



        self.conn.commit()







    # =====================
    # 保存交易
    # =====================

    def save_trade(
        self,
        trade
    ):


        return False
     



    # =====================
    # 查询全部交易
    # =====================

    def get_all_trades(self):


        cursor = self.conn.cursor()


        cursor.execute(

            """

            SELECT *

            FROM trades

            ORDER BY id DESC

            """

        )


        return cursor.fetchall()







    # =====================
    # 查询最近交易
    # =====================

    def get_latest_trades(
        self,
        limit=20
    ):


        cursor = self.conn.cursor()


        cursor.execute(

            """

            SELECT *

            FROM trades

            ORDER BY id DESC

            LIMIT ?

            """,

            (
                limit,
            )

        )


        return cursor.fetchall()