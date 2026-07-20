from database.sqlite_db import get_connection


DB_PATH = "btc_ai.db"



# =================================
# 获取最新持仓状态
# =================================

def get_position_status():


    conn = get_connection(DB_PATH)


    cursor = conn.cursor()



    row = cursor.execute(

        """

        SELECT

        direction,
        entry,
        current,
        pnl,
        size_btc,
        stop_loss,
        take_profit,
        hold_minutes,
        max_profit,
        max_drawdown

        FROM position_status

        ORDER BY id DESC

        LIMIT 1

        """

    ).fetchone()



    conn.close()



    if not row:


        return {


            "position":"NONE",

            "entry":0,

            "current":0,

            "pnl":0,

            "size_btc":0,

            "stop_loss":0,

            "take_profit":0,

            "hold_minutes":0,

            "max_profit":0,

            "max_drawdown":0

        }



    return {


        "position":row[0],

        "entry":row[1],

        "current":row[2],

        "pnl":row[3],

        "size_btc":row[4],

        "stop_loss":row[5],

        "take_profit":row[6],

        "hold_minutes":row[7],

        "max_profit":row[8],

        "max_drawdown":row[9]

    }





# =================================
# 获取Dashboard全部数据
# =================================

def get_dashboard_data():


    conn = sqlite3.connect(

        DB_PATH,
        timeout=30

    )


    cursor = conn.cursor()



    row = cursor.execute(

        """

        SELECT


        price,

        trend,

        signal,

        rsi,

        macd,

        atr


        FROM market_status


        ORDER BY id DESC


        LIMIT 1


        """

    ).fetchone()



    conn.close()




    # 没有行情数据

    if not row:


        market = {


            "price":0,

            "trend":"neutral",

            "signal":"NONE",

            "rsi":0,

            "macd":0,

            "atr":0

        }


    else:


        market = {


            "price":row[0],

            "trend":row[1],

            "signal":row[2],

            "rsi":row[3],

            "macd":row[4],

            "atr":row[5]

        }



    # 获取持仓

    position = get_position_status()




    # 合并返回Dashboard


    return {


        "price":

            market["price"],



        "trend":

            market["trend"],



        "signal":

            market["signal"],



        "position":

            position["position"],



        "entry":

            position["entry"],



        "current":

            position["current"],



        "pnl":

            position["pnl"],



        "size_btc":

            position["size_btc"],



        "stop_loss":

            position["stop_loss"],



        "take_profit":

            position["take_profit"],



        "hold_minutes":

            position["hold_minutes"],



        "max_profit":

            position["max_profit"],



        "max_drawdown":

            position["max_drawdown"],



        "rsi":

            market["rsi"],



        "macd":

            market["macd"],



        "atr":

            market["atr"]

    }