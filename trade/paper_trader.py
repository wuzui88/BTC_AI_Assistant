from database.position_db import PositionDB
import time


class PaperTrader:


    # =========================
    # V10.1.9 风控参数
    # =========================
    BREAK_EVEN_ATR = 0.6
    TRAIL_START_ATR = 1.2
    TRAIL_DISTANCE_ATR = 1.0
    PROFIT_LOCK_ATR = 2.0
    PROFIT_LOCK_DISTANCE_ATR = 0.7


    def normalize_direction(
        self,
        direction
    ):

        return (
            str(direction).upper()
            if direction is not None
            else None
        )


    def __init__(
        self,
        position_db=None
    ):

        self.position_db = (
            position_db
            if position_db
            else PositionDB()
        )


        self.position = (
            self.position_db.get_position()
        )


        if self.position:

            self.position["direction"] = (
                self.normalize_direction(
                    self.position.get("direction")
                )
            )


            self.position.setdefault(
                "max_profit",
                0
            )

            self.position.setdefault(
                "max_drawdown",
                0
            )

            self.position.setdefault(
                "highest_price",
                self.position.get(
                    "entry",
                    0
                )
            )

            self.position.setdefault(
                "lowest_price",
                self.position.get(
                    "entry",
                    0
                )
            )

            self.position.setdefault(
                "open_time",
                int(time.time())
            )


        self.history = []



    # =========================
    # 开仓
    # =========================


    def open_position(
        self,
        order,
        entry,
        stop_loss,
        take_profit
    ):


        if self.position:

            return {

                "status":
                    "EXIST_POSITION",

                "position":
                    self.position
            }



        direction = self.normalize_direction(
            order["posSide"]
        )


        # =====================
        # 防止异常止损
        # =====================

        if direction == "LONG":

            if stop_loss >= entry:

                stop_loss = entry - 1.5


        elif direction == "SHORT":

            if stop_loss <= entry:

                stop_loss = entry + 1.5




        self.position = {


            "direction":
                direction,


            "side":
                order["side"],


            "entry":
                entry,


            "stop_loss":
                stop_loss,


            "take_profit":
                take_profit,


            "size_btc":
                order["size_btc"],


            "contracts":
                order["contracts"],


            "leverage":
                order.get(
                    "leverage",
                    30
                ),


            "open_time":
                int(time.time()),


            "max_profit":
                0,


            "max_drawdown":
                0,


            "highest_price":
                entry,


            "lowest_price":
                entry,


            "trailing_status":
                "NONE"

        }



        self.position_db.save_position(
            self.position
        )


        return {

            "status":
                "OPEN_SUCCESS",

            "position":
                self.position

        }




    # =========================
    # 检查持仓
    # =========================


    def check_position(
        self,
        price,
        atr=0
    ):


        if not self.position:

            return None



        direction = self.normalize_direction(
            self.position["direction"]
        )


        entry = self.position["entry"]


        size = self.position["size_btc"]



        # 当前盈亏

        if direction == "LONG":

            profit = (
                price - entry
            ) * size


        else:

            profit = (
                entry - price
            ) * size





        # 最大盈利

        if profit > self.position.get(
            "max_profit",
            0
        ):

            self.position["max_profit"] = round(
                profit,
                2
            )



        # 最大回撤

        if profit < 0:

            drawdown = abs(profit)


            if drawdown > self.position.get(
                "max_drawdown",
                0
            ):

                self.position["max_drawdown"] = round(
                    drawdown,
                    2
                )




        # 价格极值

        if direction == "LONG":


            if price > self.position.get(
                "highest_price",
                entry
            ):

                self.position["highest_price"] = price



        else:


            if price < self.position.get(
                "lowest_price",
                entry
            ):

                self.position["lowest_price"] = price





        # =====================
        # ATR移动止损
        # =====================


        if atr and atr > 0:


            hold_seconds = (
                int(time.time())
                -
                self.position["open_time"]
            )


            if hold_seconds >= 180:



                # 保本

                if profit >= atr * self.BREAK_EVEN_ATR:


                    if direction == "LONG":

                        if self.position["stop_loss"] < entry:

                            self.position["stop_loss"] = round(
                                entry + 10 if direction == "LONG" else entry - 10,
                                2
                            )

                            print(
                                "保本止损启动:",
                                entry
                            )


                    else:


                        if self.position["stop_loss"] > entry:

                            self.position["stop_loss"] = round(
                                entry + 10 if direction == "LONG" else entry - 10,
                                2
                            )

                            print(
                                "保本止损启动:",
                                entry
                            )



                # 1.5ATR追踪

                if profit >= atr * self.TRAIL_START_ATR:


                    if direction == "LONG":


                        new_stop = (
                            self.position["highest_price"]
                            -
                            atr * self.TRAIL_DISTANCE_ATR
                        )


                        if new_stop > self.position["stop_loss"]:

                            self.position["stop_loss"] = round(
                                new_stop,
                                2
                            )


                            print(
                                "移动止损更新:",
                                self.position["stop_loss"]
                            )



                    else:


                        new_stop = (
                            self.position["lowest_price"]
                            +
                            atr * self.TRAIL_DISTANCE_ATR
                        )


                        if new_stop < self.position["stop_loss"]:

                            self.position["stop_loss"] = round(
                                new_stop,
                                2
                            )


                            print(
                                "移动止损更新:",
                                self.position["stop_loss"]
                            )

            
        # =====================
        # 2.5 ATR利润锁定
        # =====================


                if profit >= atr * self.PROFIT_LOCK_ATR:


                    if direction == "LONG":


                        new_stop = (
                            self.position["highest_price"]
                            -
                            atr * self.PROFIT_LOCK_DISTANCE_ATR
                        )


                        if new_stop > self.position["stop_loss"]:


                            self.position["stop_loss"] = round(
                                new_stop,
                                2
                            )


                            print(
                                "利润锁定:",
                                self.position["stop_loss"]
                            )


                    else:


                        new_stop = (
                            self.position["lowest_price"]
                            +
                            atr * self.PROFIT_LOCK_DISTANCE_ATR
                        )


                        if new_stop < self.position["stop_loss"]:


                            self.position["stop_loss"] = round(
                                new_stop,
                                2
                            )


                            print(
                                "利润锁定:",
                                self.position["stop_loss"]
                            )



                if profit >= atr * self.PROFIT_LOCK_ATR:

                    self.position["trailing_status"] = "PROFIT_LOCK"

                elif profit >= atr * self.TRAIL_START_ATR:

                    self.position["trailing_status"] = "ATR_TRAILING"

                elif profit >= atr * self.BREAK_EVEN_ATR:

                    self.position["trailing_status"] = "BREAK_EVEN"

                self.position_db.save_position(
                    self.position
                )





        stop_loss = self.position["stop_loss"]

        take_profit = self.position["take_profit"]




        # =====================
        # 平仓检测
        # =====================


        if direction == "LONG":


            if price <= stop_loss:

                return self.close_position(
                    price,
                    "TRAIL_STOP"
                )


            if price >= take_profit:

                return self.close_position(
                    price,
                    "TAKE_PROFIT"
                )



        elif direction == "SHORT":


            if price >= stop_loss:

                return self.close_position(
                    price,
                    "TRAIL_STOP"
                )


            if price <= take_profit:

                return self.close_position(
                    price,
                    "TAKE_PROFIT"
                )



        return None




    # =========================
    # 平仓
    # =========================


    def close_position(
        self,
        price,
        reason
    ):


        if self.position is None:

            return None



        position = self.position


        entry = position["entry"]

        size = position["size_btc"]


        direction = self.normalize_direction(
            position.get("direction")
        )




        # =====================
        # 盈亏计算
        # =====================


        if direction == "LONG":

            pnl = (
                price - entry
            ) * size


        elif direction == "SHORT":

            pnl = (
                entry - price
            ) * size


        else:

            pnl = 0




        now = int(time.time())


        hold_minutes = round(
            (
                now -
                position["open_time"]
            )
            /
            60,
            1
        )




        # =====================
        # 同步最终止损状态
        # =====================

        position.setdefault("trailing_status", "NONE")

        position["final_stop_loss"] = position.get(
            "stop_loss",
            0
        )


        # =====================
        # 最终交易记录
        # =====================


        record = {


            "direction":

                direction,


            "entry":

                entry,


            "exit":

                price,


            "size_btc":

                size,


            "contracts":

                position["contracts"],


            "pnl":

                round(
                    pnl,
                    2
                ),


            "reason":

                reason,


            "open_time":

                position["open_time"],


            "close_time":

                now,


            "hold_minutes":

                hold_minutes,


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
                    entry
                ),


            "lowest_price":

                position.get(
                    "lowest_price",
                    entry
                ),


            "final_stop_loss":

                position.get(
                    "stop_loss"
                ),


            "trailing_status":

                position.get(
                    "trailing_status",
                    "NONE"
                )

        }




        # =====================
        # 数据库同步
        #
        # V10.1.7修复
        #
        # 同步:
        # max_profit
        # max_drawdown
        #
        # 防止数据库出现0
        # =====================


        try:


            self.position_db.close_position(

                position,

                price,

                reason,

                round(
                    pnl,
                    2
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


        except Exception as e:


            print(
                "更新持仓历史失败:",
                e
            )




        # =====================
        # 清理内存
        # =====================


        self.position = None



        self.history.append(
            record
        )



        return {


            "status":

                "CLOSED",


            "record":

                record

        }





    # =========================
    # 当前持仓
    # =========================


    def get_position(self):

        return self.position





    # =========================
    # 实时状态
    # =========================


    def get_position_status(
        self,
        price
    ):


        if self.position is None:

            return None



        entry = self.position["entry"]

        size = self.position["size_btc"]



        direction = self.normalize_direction(
            self.position["direction"]
        )



        if direction == "LONG":

            pnl = (
                price - entry
            ) * size


        else:

            pnl = (
                entry - price
            ) * size



        hold_time = (
            int(time.time())
            -
            self.position["open_time"]
        )




        return {


            "direction":

                direction,


            "entry":

                entry,


            "current":

                price,


            "pnl":

                round(
                    pnl,
                    2
                ),


            "max_profit":

                round(
                    self.position.get(
                        "max_profit",
                        0
                    ),
                    2
                ),


            "max_drawdown":

                round(
                    self.position.get(
                        "max_drawdown",
                        0
                    ),
                    2
                ),


            "highest_price":

                self.position.get(
                    "highest_price"
                ),


            "lowest_price":

                self.position.get(
                    "lowest_price"
                ),


            "trailing_status":

                self.position.get(
                    "trailing_status",
                    "NONE"
                ),


            "stop_loss":

                self.position["stop_loss"],


            "take_profit":

                self.position["take_profit"],


            "hold_minutes":

                round(
                    hold_time / 60,
                    1
                ),


            "size_btc":

                size

        }





    # =========================
    # 历史交易
    # =========================


    def get_history(self):

        return self.history

