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
    #
    # V10.2
    #
    # 优化:
    #
    # 1. 保留原positions
    # 2. 保留原trades
    # 3. 增加AI信号字段
    # 4. 增加风控事件表
    #
    # =================================================


    def create_table(self):


        # =========================
        # 当前持仓
        # =========================


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


            lowest_price REAL DEFAULT 0,


            final_stop_loss REAL DEFAULT 0,


            trailing_status TEXT DEFAULT 'NONE'

        )
        """)





        # =========================
        # 实时状态
        # =========================


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





        # =========================
        # 历史交易
        #
        # V10.2升级
        #
        # 增加:
        #
        # AI决策数据
        #
        # 技术指标快照
        #
        # =========================


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


            trailing_status TEXT DEFAULT 'NONE',



            signal TEXT,


            trend TEXT,


            market_mode TEXT,


            score REAL,


            confidence REAL,



            EMA20 REAL,


            EMA50 REAL,


            RSI REAL,


            MACD REAL,


            VWAP REAL,


            ATR REAL,


            VOLUME_RATIO REAL


        )
        """)





        # =========================
        # 风控事件
        #
        # V10.2新增
        #
        # =========================


        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS risk_events(


            id INTEGER PRIMARY KEY AUTOINCREMENT,


            trade_id INTEGER,


            event TEXT,


            price REAL,


            old_stop REAL,


            new_stop REAL,


            create_time INTEGER


        )
        """)





        self.conn.commit()

        # =================================================
    # 数据库字段迁移
    #
    # V10.2
    #
    # 自动兼容旧 btc_ai.db
    #
    # 不删除历史数据
    #
    # =================================================


    def migrate_database(self):


        tables = {


            # =====================
            # positions迁移
            # =====================

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


            },



            # =====================
            # trades历史交易迁移
            #
            # V10.2新增
            #
            # =====================


            "trades": {


                "signal":
                    "TEXT",


                "trend":
                    "TEXT",


                "market_mode":
                    "TEXT",


                "score":
                    "REAL",


                "confidence":
                    "REAL",



                "EMA20":
                    "REAL",


                "EMA50":
                    "REAL",


                "RSI":
                    "REAL",


                "MACD":
                    "REAL",


                "VWAP":
                    "REAL",


                "ATR":
                    "REAL",


                "VOLUME_RATIO":
                    "REAL"


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





            for name, dtype in fields.items():


                if name not in exists:


                    print(

                        f"数据库迁移增加字段: {table}.{name}"

                    )


                    self.conn.execute(

                        f"""

                        ALTER TABLE {table}

                        ADD COLUMN {name} {dtype}

                        """

                    )




        self.conn.commit()







    # =================================================
    # 保存持仓
    #
    # 保留V10.1.9接口
    #
    # =================================================


    def save_position(
        self,
        position
    ):


        position_id = position.get(
            "id"
        )



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


                lowest_price=?,


                final_stop_loss=?,


                trailing_status=?


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



                position.get(
                    "final_stop_loss",
                    position.get(
                        "stop_loss",
                        0
                    )
                ),



                position.get(
                    "trailing_status",
                    "NONE"
                ),



                position_id


            ))



            self.conn.commit()



            return position_id




        # =====================
        # 防止重复OPEN仓
        # =====================


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




        # =====================
        # 新建持仓
        # =====================


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
    # 保存风控事件
    #
    # V10.2新增
    #
    # BREAK_EVEN
    # ATR_TRAIL
    # PROFIT_LOCK
    #
    # =================================================


    def save_risk_event(
        self,
        trade_id,
        event,
        price,
        old_stop,
        new_stop
    ):


        try:


            self.conn.execute("""
            INSERT INTO risk_events(

                trade_id,

                event,

                price,

                old_stop,

                new_stop,

                create_time

            )

            VALUES(?,?,?,?,?,?)

            """, (


                trade_id,


                event,


                price,


                old_stop,


                new_stop,


                int(time.time())


            ))



            self.conn.commit()



            return True



        except Exception as e:


            print(

                "保存风控事件失败:",

                e

            )


            return False







    # =================================================
    # 平仓
    #
    # V10.2升级
    #
    # 增加:
    #
    # AI信号记录
    # 技术指标快照
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



        now = int(time.time())




        # =====================
        # 更新当前仓位
        # =====================


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


            now,


            reason,


            pnl,


            max_profit,


            max_drawdown,


            highest_price,


            lowest_price,


            position.get(
                "final_stop_loss",
                position.get(
                    "stop_loss",
                    0
                )
            ),


            position.get(
                "trailing_status",
                "NONE"
            ),


            position_id


        ))





        # =====================
        # 写入交易历史
        # =====================


        signal_data = position.get(
            "signal_data",
            {}
        )



        indicator_data = position.get(
            "indicators",
            {}
        )




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

            trailing_status,


            signal,

            trend,

            market_mode,

            score,

            confidence,


            EMA20,

            EMA50,

            RSI,

            MACD,

            VWAP,

            ATR,

            VOLUME_RATIO


        )


        VALUES(

            ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?

        )


        """, (


            position.get(
                "direction",
                "NONE"
            ),


            position.get(
                "entry",
                0
            ),


            exit_price,


            position.get(
                "size_btc",
                0
            ),


            position.get(
                "contracts",
                0
            ),


            pnl,


            reason,


            position.get(
                "open_time",
                0
            ),


            now,


            round(

                (

                    now -

                    position.get(
                        "open_time",
                        now
                    )

                ) / 60,

                1

            ),


            max_profit,


            max_drawdown,


            highest_price,


            lowest_price,


            position.get(
                "final_stop_loss",
                position.get(
                    "stop_loss",
                    0
                )
            ),


            position.get(
                "trailing_status",
                "NONE"
            ),




            signal_data.get(
                "signal",
                ""
            ),


            signal_data.get(
                "trend",
                ""
            ),


            signal_data.get(
                "market_mode",
                ""
            ),


            signal_data.get(
                "score",
                0
            ),


            signal_data.get(
                "confidence",
                0
            ),




            indicator_data.get(
                "EMA20",
                0
            ),


            indicator_data.get(
                "EMA50",
                0
            ),


            indicator_data.get(
                "RSI",
                0
            ),


            indicator_data.get(
                "MACD",
                0
            ),


            indicator_data.get(
                "VWAP",
                0
            ),


            indicator_data.get(
                "ATR",
                0
            ),


            indicator_data.get(
                "VOLUME_RATIO",
                0
            )


        ))



        self.conn.commit()



        return True

        # =================================================
    # 兼容旧代码
    #
    # 原DELETE逻辑
    #
    # V10.2
    #
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
    #
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
    # 历史交易查询
    #
    # V10.2新增
    #
    # =================================================


    def get_trade_history(
        self,
        limit=100
    ):


        rows = self.conn.execute("""
        SELECT *

        FROM trades

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
    #
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
    # V10.2
    #
    # 增加异常保护
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





            # =========================
            # 清理历史状态
            # 保留最近10000条
            # =========================


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
    # 查询风险事件
    #
    # V10.2新增
    #
    # =================================================


    def get_risk_events(
        self,
        trade_id=None,
        limit=100
    ):


        if trade_id:


            rows = self.conn.execute("""
            SELECT *

            FROM risk_events

            WHERE trade_id=?

            ORDER BY id DESC

            LIMIT ?

            """, (

                trade_id,

                limit

            )).fetchall()



        else:


            rows = self.conn.execute("""
            SELECT *

            FROM risk_events

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
    # 关闭数据库
    #
    # =================================================


    def close(self):


        try:


            self.conn.close()



        except Exception:


            pass

