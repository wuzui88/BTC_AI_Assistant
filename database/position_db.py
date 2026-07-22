import sqlite3
import time


class PositionDB:


    def __init__(
        self,
        db_path="btc_ai.db"
    ):

        self.conn = sqlite3.connect(
            db_path,
            timeout=30,
            check_same_thread=False
        )


        self.conn.row_factory = sqlite3.Row


        self.conn.execute(
            "PRAGMA journal_mode=WAL;"
        )


        self.conn.execute(
            "PRAGMA busy_timeout=30000;"
        )



        self.last_status_update = 0


        self.status_update_interval = 5



        self.create_table()


        self.migrate_database()







    # =================================================
    # 创建数据表
    # =================================================


    def create_table(self):


        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS positions(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            direction TEXT,

            side TEXT,

            entry REAL,

            exit REAL,

            stop_loss REAL,

            take_profit REAL,

            size_btc REAL,

            contracts INTEGER,

            leverage INTEGER,


            status TEXT DEFAULT 'OPEN',


            open_time INTEGER,

            close_time INTEGER,


            close_reason TEXT,


            pnl REAL DEFAULT 0,


            max_profit REAL DEFAULT 0,


            max_drawdown REAL DEFAULT 0,


            highest_price REAL DEFAULT 0,


            lowest_price REAL DEFAULT 0

        )
        """)




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


            max_profit REAL DEFAULT 0,


            max_drawdown REAL DEFAULT 0,


            highest_price REAL DEFAULT 0,


            lowest_price REAL DEFAULT 0,


            update_time INTEGER


        )
        """)




        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS trades(
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
            max_profit REAL DEFAULT 0,
            max_drawdown REAL DEFAULT 0,
            highest_price REAL DEFAULT 0,
            lowest_price REAL DEFAULT 0,
            final_stop_loss REAL DEFAULT 0,
            trailing_status TEXT DEFAULT 'NONE'
        )
        """)

        self.conn.commit()







    # =================================================
    # 数据库字段迁移
    #
    # V10.1.7
    #
    # 修复旧数据库没有新增字段问题
    #
    # =================================================


    def migrate_database(self):


        # =========================
        # positions表迁移
        # =========================

        tables = {

            "positions": {

                "exit":
                    "REAL",

                "status":
                    "TEXT DEFAULT 'OPEN'",

                "close_time":
                    "INTEGER",

                "close_reason":
                    "TEXT",

                "pnl":
                    "REAL DEFAULT 0",

                "max_profit":
                    "REAL DEFAULT 0",

                "max_drawdown":
                    "REAL DEFAULT 0",

                "highest_price":
                    "REAL DEFAULT 0",

                "lowest_price":
                    "REAL DEFAULT 0",

                "final_stop_loss":
                    "REAL DEFAULT 0",

                "trailing_status":
                    "TEXT DEFAULT 'NONE'"

            },


            # =====================
            # position_status迁移
            # =====================

            "position_status": {


                "highest_price":
                    "REAL DEFAULT 0",


                "lowest_price":
                    "REAL DEFAULT 0"


            }

        }




        for table, fields in tables.items():


            columns = self.conn.execute(

                f"PRAGMA table_info({table})"

            ).fetchall()



            exists = {

                row["name"]

                for row in columns

            }



            for name, typ in fields.items():


                if name not in exists:


                    print(

                        f"数据库迁移增加字段: {table}.{name}"

                    )


                    self.conn.execute(

                        f"""
                        ALTER TABLE {table}
                        ADD COLUMN {name} {typ}
                        """

                    )



        self.conn.commit()







    # =================================================
    # 保存持仓
    # =================================================


    def save_position(
        self,
        position
    ):



        position_id = position.get(
            "id"
        )





        # -----------------------------
        # 已存在仓位 更新
        # -----------------------------


        if position_id:



            self.conn.execute("""
            UPDATE positions SET


                direction=?,


                side=?,


                entry=?,


                stop_loss=?,


                take_profit=?,


                size_btc=?,


                contracts=?,


                leverage=?,


                max_profit=?,


                max_drawdown=?,


                highest_price=?,


                lowest_price=?


            WHERE id=?

            """, (



                position.get(
                    "direction"
                ),



                position.get(
                    "side",
                    position.get(
                        "direction"
                    )
                ),



                position.get(
                    "entry",
                    0
                ),



                position.get(
                    "stop_loss",
                    0
                ),



                position.get(
                    "take_profit",
                    0
                ),



                position.get(
                    "size_btc",
                    0
                ),



                position.get(
                    "contracts",
                    0
                ),



                position.get(
                    "leverage",
                    30
                ),



                position.get(
                    "max_profit",
                    0
                ),



                position.get(
                    "max_drawdown",
                    0
                ),



                position.get(
                    "highest_price",
                    0
                ),



                position.get(
                    "lowest_price",
                    0
                ),



                position_id


            ))



            self.conn.commit()



            return position_id







        # -----------------------------
        # 查找重复OPEN仓
        # -----------------------------


        row = self.conn.execute("""
        SELECT id

        FROM positions

        WHERE status='OPEN'

        AND direction=?

        AND entry=?

        ORDER BY id DESC

        LIMIT 1

        """, (



            position.get(
                "direction"
            ),



            position.get(
                "entry",
                0
            )


        )).fetchone()





        if row:


            position["id"] = row["id"]


            return self.save_position(
                position
            )







        # -----------------------------
        # 新建持仓
        # -----------------------------


        cursor = self.conn.execute("""
        INSERT INTO positions(

            direction,

            side,

            entry,

            stop_loss,

            take_profit,

            size_btc,

            contracts,

            leverage,

            status,

            open_time,

            highest_price,

            lowest_price


        )


        VALUES(?,?,?,?,?,?,?,?,?,?,?,?)

        """, (



            position.get(
                "direction"
            ),



            position.get(
                "side",
                position.get(
                    "direction"
                )
            ),



            position.get(
                "entry",
                0
            ),



            position.get(
                "stop_loss",
                0
            ),



            position.get(
                "take_profit",
                0
            ),



            position.get(
                "size_btc",
                0
            ),



            position.get(
                "contracts",
                0
            ),



            position.get(
                "leverage",
                30
            ),



            "OPEN",



            int(time.time()),



            position.get(
                "highest_price",
                position.get(
                    "entry",
                    0
                )
            ),



            position.get(
                "lowest_price",
                position.get(
                    "entry",
                    0
                )

            )


        ))





        self.conn.commit()



        position["id"] = cursor.lastrowid



        return cursor.lastrowid

        # =================================================
    # 获取当前OPEN持仓
    # =================================================

    def get_position(self):


        row = self.conn.execute("""
        SELECT *

        FROM positions

        WHERE status='OPEN'

        ORDER BY id DESC

        LIMIT 1

        """).fetchone()


        return dict(row) if row else None



    def get_open_position(self):

        return self.get_position()



    # =================================================
    # 平仓
    #
    # V10.1.7
    #
    # 不删除历史
    # 更新状态
    #
    # 同步:
    # max_profit
    # max_drawdown
    # highest_price
    # lowest_price
    #
    # =================================================

    def close_position(
        self,
        position,
        exit_price,
        reason,
        pnl,
        max_profit=0,
        max_drawdown=0
    ):


        position_id = position.get(
            "id"
        )


        if not position_id:

            return False



        if max_profit == 0:

            max_profit = position.get(
                "max_profit",
                0
            )



        if max_drawdown == 0:

            max_drawdown = position.get(
                "max_drawdown",
                0
            )



        highest_price = position.get(
            "highest_price",
            0
        )



        lowest_price = position.get(
            "lowest_price",
            0
        )



        self.conn.execute("""
        UPDATE positions SET


            exit=?,


            status='CLOSED',


            close_time=?,


            close_reason=?,


            pnl=?,


            max_profit=?,


            max_drawdown=?,


            highest_price=?,


            lowest_price=?,


            final_stop_loss=?,


            trailing_status=?


        WHERE id=?


        """, (


            exit_price,


            int(time.time()),


            reason,


            pnl,


            max_profit,


            max_drawdown,


            highest_price,


            lowest_price,


            position.get("final_stop_loss", position.get("stop_loss", 0)),


            position.get("trailing_status", "NONE"),


            position_id


        ))



        self.conn.execute("""
        INSERT INTO trades(
            direction,
            entry,
            exit,
            size_btc,
            contracts,
            pnl,
            reason,
            open_time,
            close_time,
            hold_minutes,
            max_profit,
            max_drawdown,
            highest_price,
            lowest_price,
            final_stop_loss,
            trailing_status
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            position.get("direction", "NONE"),
            position.get("entry", 0),
            exit_price,
            position.get("size_btc", 0),
            position.get("contracts", 0),
            pnl,
            reason,
            position.get("open_time", 0),
            int(time.time()),
            round((int(time.time())-position.get("open_time", int(time.time())))/60,1),
            max_profit,
            max_drawdown,
            highest_price,
            lowest_price,
            position.get("final_stop_loss", position.get("stop_loss",0)),
            position.get("trailing_status", "NONE")
        ))


        self.conn.commit()


        return True





    # =================================================
    # 兼容旧代码
    #
    # 原DELETE逻辑
    #
    # V10.1.7
    # 改为关闭历史
    #
    # =================================================


    def clear_position(self):


        position = self.get_position()



        if position:


            return self.close_position(


                position,


                position.get(
                    "entry",
                    0
                ),


                "MANUAL_CLOSE",


                position.get(
                    "pnl",
                    0
                ),


                position.get(
                    "max_profit",
                    0
                ),


                position.get(
                    "max_drawdown",
                    0
                )


            )


        return False





    # =================================================
    # 历史持仓
    # =================================================


    def get_position_history(
        self,
        limit=100
    ):


        rows = self.conn.execute("""
        SELECT *

        FROM positions

        ORDER BY id DESC

        LIMIT ?

        """, (

            limit,

        )).fetchall()



        return [

            dict(row)

            for row in rows

        ]





    # =================================================
    # Dashboard当前持仓
    # =================================================


    def get_dashboard_position(self):


        position = self.get_position()



        if not position:


            return {


                "position":
                    "NONE",


                "direction":
                    "NONE",


                "entry":
                    0,


                "current":
                    0,


                "pnl":
                    0,


                "size_btc":
                    0,


                "stop_loss":
                    0,


                "take_profit":
                    0,


                "max_profit":
                    0,


                "max_drawdown":
                    0,


                "highest_price":
                    0,


                "lowest_price":
                    0


            }





        return {


            "position":

                position.get(
                    "direction"
                ),



            "direction":

                position.get(
                    "direction"
                ),



            "entry":

                position.get(
                    "entry",
                    0
                ),



            "current":

                position.get(
                    "entry",
                    0
                ),



            "pnl":

                position.get(
                    "pnl",
                    0
                ),



            "size_btc":

                position.get(
                    "size_btc",
                    0
                ),



            "stop_loss":

                position.get(
                    "stop_loss",
                    0
                ),



            "take_profit":

                position.get(
                    "take_profit",
                    0
                ),



            "max_profit":

                position.get(
                    "max_profit",
                    0
                ),



            "max_drawdown":

                position.get(
                    "max_drawdown",
                    0
                ),



            "highest_price":

                position.get(
                    "highest_price",
                    0
                ),



            "lowest_price":

                position.get(
                    "lowest_price",
                    0
                )

        }

        # =================================================
    # 实时持仓状态
    #
    # V10.1.7
    #
    # 增加:
    #
    # highest_price
    # lowest_price
    #
    # 防止数据库异常影响行情循环
    #
    # =================================================


    def update_status(
        self,
        data
    ):


        now = time.time()



        if (

            now -

            self.last_status_update

            <

            self.status_update_interval

        ):


            return




        self.last_status_update = now




        try:


            self.conn.execute("""
            INSERT INTO position_status(

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

                highest_price,

                lowest_price,

                update_time

            )


            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)

            """, (



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



                data.get(
                    "highest_price",
                    0
                ),



                data.get(
                    "lowest_price",
                    0
                ),



                int(time.time())


            ))
            # 每小时清理一次

            if int(time.time()) % 3600 < 5:

                self.conn.execute("""
                DELETE FROM position_status
                WHERE id NOT IN (
                    SELECT id
                    FROM position_status
                    ORDER BY id DESC
                    LIMIT 10000
                )
                """)

        
            self.conn.commit()




        except Exception as e:


            print(

                "position_status更新失败:",

                e

            )






    # =================================================
    # 关闭数据库
    # =================================================


    def close(self):


        try:

            self.conn.close()


        except Exception:


            pass