from database.position_db import PositionDB
import time



class PaperTrader:


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


        # 恢复持仓

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





        self.position = {


            "direction":
                self.normalize_direction(
                    order["posSide"]
                ),


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



            # 盈利峰值

            "max_profit":
                0,



            # 最大亏损

            "max_drawdown":
                0,



            "highest_price":
                entry,



            "lowest_price":
                entry

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



        # =====================
        # 当前盈亏
        # =====================


        if direction == "LONG":


            profit = (

                price - entry

            ) * size



        else:


            profit = (

                entry - price

            ) * size





        # =====================
        # 最大盈利记录
        # =====================


        if profit > self.position.get(
            "max_profit",
            0
        ):


            self.position["max_profit"] = round(

                profit,

                2

            )




        # =====================
        # 最大回撤记录
        # =====================


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





        # =====================
        # 记录价格极值
        # =====================


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
        # 新版移动止损
        # =====================


        if atr and atr > 0:


            hold_seconds = (

                int(time.time())

                -

                self.position["open_time"]

            )



            # 开仓3分钟后才允许调整止损

            allow_trailing = (

                hold_seconds >= 180

            )



            if allow_trailing:



                # -----------------
                # 0.8 ATR 保本
                # -----------------


                if profit >= atr * 0.8:



                    if direction == "LONG":


                        if self.position["stop_loss"] < entry:


                            self.position["stop_loss"] = round(

                                entry,

                                2

                            )


                            print(

                                "保本止损启动:",

                                entry

                            )



                    else:


                        if self.position["stop_loss"] > entry:


                            self.position["stop_loss"] = round(

                                entry,

                                2

                            )


                            print(

                                "保本止损启动:",

                                entry

                            )





                # -----------------
                # 1.5 ATR 动态追踪
                # -----------------


                if profit >= atr * 1.5:



                    if direction == "LONG":


                        new_stop = (

                            self.position["highest_price"]

                            -

                            atr * 1.2

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

                            atr * 1.2

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





                # -----------------
                # 2.5 ATR 锁利润
                # -----------------


                if profit >= atr * 2.5:



                    if direction == "LONG":


                        new_stop = (

                            self.position["highest_price"]

                            -

                            atr * 0.8

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

                            atr * 0.8

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



                self.position_db.save_position(

                    self.position

                )






        stop_loss = self.position["stop_loss"]


        take_profit = self.position["take_profit"]




        # =====================
        # 多单检查
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





        # =====================
        # 空单检查
        # =====================


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
        # 计算盈亏
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

                now

                -

                position["open_time"]

            )

            /

            60,

            1

        )





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

                )

        }







        # 清除数据库持仓


        self.position_db.clear_position()





        # 清空内存


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
    # 获取当前持仓
    # =========================


    def get_position(self):


        return self.position







    # =========================
    # 实时持仓状态
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

                price-entry

            ) * size



        else:


            pnl = (

                entry-price

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