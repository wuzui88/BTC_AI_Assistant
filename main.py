import time
from data_feed.okx_feed import OKXFeed
from data_feed.candle_builder import CandleBuilder
from data_feed.kline_cache import KlineCache
from database.sqlite_db import SQLiteDB
from database.trade_db import TradeDB
from database.market_db import update_market_status
from indicators.technical import TechnicalIndicator
from analysis.market_analysis import MarketAnalysis
from strategy.btc_strategy import BTCStrategy
from risk.risk_manager import RiskManager
from position.position_manager import PositionManager
from trade.paper_trader import PaperTrader
from data_feed.okx_history import OKXHistory
from database.position_db import PositionDB
import threading


db = SQLiteDB()
trade_db = TradeDB()
position_db = PositionDB()

kline_cache = KlineCache(max_size=500)
candle_builder = CandleBuilder()


indicator = TechnicalIndicator()
market_analysis = MarketAnalysis()
strategy = BTCStrategy()


risk_manager = RiskManager(
    balance=20000,
    risk_percent=1,
    leverage=30
)


position_manager = PositionManager()
paper_trader = PaperTrader()
history_api = OKXHistory()


current_price = 0

current_indicators = {}


# 记录止损变化
last_stop_loss = 0

last_print_time = 0

PRINT_INTERVAL = 5



def receive(data):

    global current_price
    global current_indicators
    global last_print_time
    global last_stop_loss


    if data["type"] != "tick":
        return


    current_price = data["price"]


    atr = 0


    if current_indicators:

        atr = current_indicators.get(
            "ATR",
            0
        )



    # ==============================
    # 检查持仓止损
    # ==============================

    close_result = paper_trader.check_position(
        current_price,
        atr
    )

        # ==============================
    # 获取当前持仓状态
    # ==============================

    position_status = paper_trader.get_position_status(
        current_price
    )


    if position_status:



        position_db.update_status(

            position_status

        )


    else:


        position_db.update_status({

            "direction":"NONE",

            "entry":0,

            "current":current_price,

            "pnl":0,

            "size_btc":0,

            "stop_loss":0,

            "take_profit":0,

            "hold_minutes":0,

            "max_profit":0,

            "max_drawdown":0

        })



    position = paper_trader.get_position()



    if position:


        current_stop = position["stop_loss"]


        if current_stop != last_stop_loss:


            if last_stop_loss != 0:

                print()

                print(
                    "止损更新:",
                    current_stop
                )


            last_stop_loss = current_stop




    # ==============================
    # 平仓保存交易记录
    # ==============================

    if close_result:


        print()

        print(
            "模拟平仓:",
            close_result
        )



        if close_result["status"] == "CLOSED":


            threading.Thread(
                target=trade_db.save_trade,
                args=(close_result["record"],),
                daemon=True
            ).start()


            print(
                "交易记录已保存"
            )




    now = time.time()



    if now - last_print_time >= PRINT_INTERVAL:

        position_status = paper_trader.get_position_status(
            current_price
        )

        print()
        print(
            "BTC当前价格:",
            current_price
        )

        if position_status:
            print(
                "当前持仓:",
                position_status
            )
        else:


            print(
                "当前无持仓"
            )

        last_print_time = now


    if position_status:


        position_db.update_status({

            "direction":
                position_status["direction"],


            "entry":
                position_status["entry"],


            "current":
                position_status["current"],


            "pnl":
                position_status["pnl"],


            "size_btc":
                position_status["size_btc"],


            "stop_loss":
                position_status["stop_loss"],


            "take_profit":
                position_status["take_profit"],


            "hold_minutes":
                position_status["hold_minutes"],


            "max_profit":
                position_status["max_profit"],


            "max_drawdown":
                position_status["max_drawdown"]

        })


    else:


        position_db.update_status({

            "direction":"NONE",

            "entry":0,

            "current":0,

            "pnl":0,

            "size_btc":0,

            "stop_loss":0,

            "take_profit":0,

            "hold_minutes":0,

            "max_profit":0,

            "max_drawdown":0

        })




      #  last_print_time = now




    # ==============================
    # 生成5分钟K线
    # ==============================


    candle = candle_builder.update(

        current_price,

        data["time"]

    )



    if candle:



        print()

        print(
            "生成5分钟K线:",
            candle
        )



        kline_cache.add(candle)


        db.save_kline(candle)



        candles = kline_cache.data



        print(
            "K线数量:",
            len(candles)
        )



        indicators = indicator.calculate(
            candles
        )



        current_indicators = indicators



        print()

        print(
            "技术指标:",
            indicators
        )



        market = market_analysis.analyze(

            candles,

            indicators

        )
        print("===================")

        print("MARKET返回内容:")

        print(market)

        print("===================")



        print()

        print(
            "市场分析:",
            market
        )



        # ==============================
        # K线分析后更新Dashboard
        # ==============================


        try:

            position_status = paper_trader.get_position_status(
                current_price
            )


            update_market_status({

                "price": current_price,


                "trend": market.get(
                    "trend",
                    "neutral"
                ),


                "signal": market.get(
                    "signal",
                    "WAIT"
                ),


                "position":
                    position_status["direction"]
                    if position_status
                    else "NONE",


                "pnl":
                    position_status["pnl"]
                    if position_status
                    else 0,


                "stop_loss":
                    position_status["stop_loss"]
                    if position_status
                    else 0,


                "take_profit":
                    position_status["take_profit"]
                    if position_status
                    else 0,


                "rsi": indicators.get(
                    "RSI",
                    0
                ),


                "macd": indicators.get(
                    "MACD",
                    0
                ),


                "atr": indicators.get(
                    "ATR",
                    0
                )

            })


            print(
                "market_status更新完成"
            )


        except Exception as e:

            print(
                "Dashboard实时更新错误:",
                e
            )


            print(
                "market_status更新完成"
            )


        except Exception as e:


            print(
                "market_status写入失败:",
                e
            )

        trade_plan = strategy.generate(

            current_price,

            indicators,

            market

        )



        if paper_trader.get_position():


            if trade_plan["action"] == "ENTER":


                trade_plan["action"] = "HOLD"


                print(
                    "已有持仓，忽略开仓信号"
                )




        print()

        print(
            "交易策略:",
            trade_plan
        )




        # ==============================
        # 开仓
        # ==============================


        if trade_plan["action"] == "ENTER":



            risk = risk_manager.calculate(

                trade_plan["entry"],

                trade_plan["stop_loss"]

            )



            print()

            print(
                "风险计算:",
                risk
            )




            order = position_manager.create_order(

                trade_plan["direction"],

                risk["position_size"],

                risk["leverage"]

            )



            print()

            print(
                "订单参数:",
                order
            )




            result = paper_trader.open_position(

                order,

                trade_plan["entry"],

                trade_plan["stop_loss"],

                trade_plan["take_profit"]

            )



            print()

            print(
                "模拟交易:",
                result
            )



        print()

        print(
            "----------------------"
        )




if __name__ == "__main__":



    print(
        "BTC AI Assistant启动"
    )



    history = db.load_history(300)



    print(

        "本地历史K线:",

        len(history)

    )




    if len(history) < 50:



        print(
            "加载OKX历史K线"
        )



        history = history_api.get_history()



        for candle in history:


            db.save_kline(candle)





    for candle in history:


        kline_cache.add(candle)





    print(

        "历史K线加载完成:",

        len(kline_cache.data)

    )





    position = paper_trader.get_position()



    if position:


        print()

        print(

            "恢复持仓:",

            position

        )



    else:


        print()

        print(

            "当前无持仓"

        )





    print()

    print(

        "启动OKX行情..."

    )





    okx = OKXFeed(receive)



    okx.start()





    while True:



        try:


            time.sleep(1)



        except KeyboardInterrupt:



            print(

                "程序退出"

            )



            break