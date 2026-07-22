# ============================================================
# paper_trader_v10.2_fix_final.py
#
# BTC AI Assistant V10.2
#
# PaperTrader 模拟交易执行模块
#
# 修复:
#
# 1. 兼容 BTCStrategy V10.2 输出
# 2. 增加 strategy_result -> order 转换
# 3. 增加 ENTER / WAIT 过滤
# 4. 保留 V10.1.9 风控逻辑
# 5. 新增交易AI数据保存
#
# 新增:
#
# signal_data
# indicators
#
# 用于历史交易分析
#
# ============================================================


from database.position_db import PositionDB

import time






class PaperTrader:





    # ========================================================
    # V10.2 风控参数
    #
    # BTC 5分钟永续
    #
    # ========================================================


    BREAK_EVEN_ATR = 0.6


    TRAIL_START_ATR = 1.2


    TRAIL_DISTANCE_ATR = 0.8


    PROFIT_LOCK_ATR = 1.8


    PROFIT_LOCK_DISTANCE_ATR = 0.5







    # ========================================================
    # 方向标准化
    # ========================================================


    def normalize_direction(
        self,
        direction
    ):


        return (


            str(direction).upper()


            if direction is not None


            else None


        )









    # ========================================================
    # 初始化
    # ========================================================


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


                    self.position.get(
                        "direction"
                    )


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






            self.position.setdefault(


                "trailing_status",


                "NONE"


            )





            # ==============================
            # V10.2新增
            #
            # 防止旧仓位读取异常
            #
            # ==============================


            self.position.setdefault(


                "signal_data",


                {}


            )





            self.position.setdefault(


                "indicators",


                {}


            )







        self.history = []









    # ========================================================
    # 策略结果转换
    #
    # BTCStrategy V10.2
    #
    # 输入:
    #
    # {
    #   direction,
    #   action,
    #   entry,
    #   stop_loss,
    #   take_profit
    # }
    #
    # 输出:
    #
    # open_position需要格式
    #
    # ========================================================


    def normalize_order(
        self,
        strategy_result,
        size_btc=0,
        contracts=0,
        leverage=30
    ):



        if not strategy_result:


            return None





        direction = self.normalize_direction(


            strategy_result.get(
                "direction"
            )


        )






        if direction not in [


            "LONG",


            "SHORT"


        ]:



            return None






        side = (



            "buy"


            if direction == "LONG"


            else


            "sell"



        )







        return {



            "posSide":


                direction,



            "side":


                side,



            "size_btc":


                size_btc,



            "contracts":


                contracts,



            "leverage":


                leverage



        }








    # ========================================================
    # 执行策略结果
    #
    # V10.2
    #
    # 增加 indicators传递
    #
    # ========================================================


    def execute_strategy(
        self,
        strategy_result,
        indicators=None,
        size_btc=0,
        contracts=0,
        leverage=30
    ):



        if not strategy_result:



            return {


                "status":


                    "NO_SIGNAL"


            }






        action = strategy_result.get(


            "action",


            "WAIT"


        )






        if action != "ENTER":



            return {



                "status":


                    "WAIT",



                "reason":


                    strategy_result.get(


                        "reason",


                        [


                            "等待确认"


                        ]


                    )


            }






        order = self.normalize_order(


            strategy_result,


            size_btc,


            contracts,


            leverage


        )






        if order is None:



            return {



                "status":


                    "INVALID_ORDER"


            }







        return self.open_position(


            order,



            strategy_result.get(


                "entry"


            ),



            strategy_result.get(


                "stop_loss"


            ),



            strategy_result.get(


                "take_profit"


            ),



            strategy_result,



            indicators



        )

        # ========================================================
    # 开仓
    # ========================================================


    def open_position(
        self,
        order,
        entry,
        stop_loss,
        take_profit,
        strategy_result=None,
        indicators=None
    ):



        if self.position:



            return {


                "status":


                    "EXIST_POSITION",



                "position":


                    self.position


            }






        direction = self.normalize_direction(


            order.get(
                "posSide"
            )


        )







        if direction not in [


            "LONG",


            "SHORT"


        ]:



            return {



                "status":


                    "INVALID_DIRECTION"


            }








        # ====================================================
        # 防止异常止损
        # ====================================================


        if direction == "LONG":



            if stop_loss >= entry:



                stop_loss = entry - 1.5







        elif direction == "SHORT":



            if stop_loss <= entry:



                stop_loss = entry + 1.5










        # ====================================================
        # 创建持仓
        #
        # V10.2新增:
        #
        # signal_data
        # indicators
        #
        # ====================================================



        self.position = {



            "direction":


                direction,



            "side":


                order.get(
                    "side"
                ),



            "entry":


                entry,



            "stop_loss":


                stop_loss,



            "take_profit":


                take_profit,



            "size_btc":


                order.get(
                    "size_btc",
                    0
                ),



            "contracts":


                order.get(
                    "contracts",
                    0
                ),



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


                "NONE",





            # =================================
            # V10.2 AI分析快照
            #
            # =================================


            "signal_data":


                strategy_result
                if strategy_result
                else {},





            "indicators":


                indicators
                if indicators
                else {}



        }








        self.position_db.save_position(


            self.position


        )






        print(


            "[PAPER OPEN]",


            direction,


            "ENTRY:",


            entry,


            "SL:",


            stop_loss,


            "TP:",


            take_profit



        )







        return {



            "status":


                "OPEN_SUCCESS",



            "position":


                self.position



        }









    # ========================================================
    # 检查持仓
    # ========================================================


    def check_position(
        self,
        price,
        atr=0
    ):



        if not self.position:



            return None







        direction = self.normalize_direction(



            self.position.get(
                "direction"
            )


        )






        entry = self.position["entry"]






        size = self.position.get(



            "size_btc",



            0



        )









        # ====================================================
        # 当前盈亏
        # ====================================================


        if direction == "LONG":



            profit = (


                price - entry


            ) * size





        else:



            profit = (


                entry - price


            ) * size







        # ====================================================
        # 最大盈利
        # ====================================================


        if profit > self.position.get(



            "max_profit",



            0



        ):



            self.position["max_profit"] = round(



                profit,



                2



            )








        # ====================================================
        # 最大回撤
        # ====================================================


        if profit < 0:



            drawdown = abs(


                profit


            )




            if drawdown > self.position.get(



                "max_drawdown",



                0



            ):



                self.position["max_drawdown"] = round(



                    drawdown,



                    2



                )









        # ====================================================
        # 价格极值
        # ====================================================


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










        # ====================================================
        # ATR动态风控
        # ====================================================


        if atr and atr > 0:



            hold_seconds = (



                int(time.time())



                -



                self.position["open_time"]



            )






            if hold_seconds >= 180:
                # ====================================================
                # 保本止损
                # ====================================================
            # ====================================================


                if profit >= atr * self.BREAK_EVEN_ATR:



                    if direction == "LONG":



                        new_stop = entry + 15





                        if self.position["stop_loss"] < new_stop:



                            self.position["stop_loss"] = round(


                                new_stop,


                                2


                            )



                            print(


                                "[BREAK EVEN]",


                                self.position["stop_loss"]


                            )







                    else:



                        new_stop = entry - 15





                        if self.position["stop_loss"] > new_stop:



                            self.position["stop_loss"] = round(


                                new_stop,


                                2


                            )



                            print(


                                "[BREAK EVEN]",


                                self.position["stop_loss"]


                            )










                # ====================================================
                # ATR追踪止损
                # ====================================================


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


                                "[ATR TRAIL]",


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


                                "[ATR TRAIL]",


                                self.position["stop_loss"]


                            )









                # ====================================================
                # 利润锁定
                # ====================================================


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









                # ====================================================
                # 更新追踪状态
                # ====================================================


                if profit >= atr * self.PROFIT_LOCK_ATR:



                    self.position["trailing_status"] = (


                        "PROFIT_LOCK"


                    )




                elif profit >= atr * self.TRAIL_START_ATR:



                    self.position["trailing_status"] = (


                        "ATR_TRAILING"


                    )




                elif profit >= atr * self.BREAK_EVEN_ATR:



                    self.position["trailing_status"] = (


                        "BREAK_EVEN"


                    )







                self.position_db.save_position(



                    self.position



                )









        # ====================================================
        # 平仓触发
        # ====================================================


        stop_loss = self.position["stop_loss"]



        take_profit = self.position["take_profit"]







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







    # ========================================================
    # 平仓
    # ========================================================


    def close_position(
        self,
        price,
        reason
    ):



        if self.position is None:



            return None


        position = self.position


        entry = position["entry"]


        size = position.get(



            "size_btc",



            0



        )






        direction = self.normalize_direction(



            position.get(



                "direction"



            )



        )









        # ====================================================
        # 盈亏计算
        # ====================================================


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








        position.setdefault(



            "trailing_status",



            "NONE"



        )






        position["final_stop_loss"] = position.get(



            "stop_loss",



            0



        )






        # ====================================================
        # V10.2 交易记录增强
        # ====================================================


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



                position.get(



                    "contracts",



                    0



                ),




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


                ),





            # ===============================
            # V10.2新增
            #
            # AI策略快照
            #
            # ===============================


            "signal_data":


                position.get(


                    "signal_data",


                    {}


                ),





            "indicators":


                position.get(


                    "indicators",


                    {}


                )



        }









        # ====================================================
        # 数据库同步
        # ====================================================


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








        print(



            "[PAPER CLOSE]",



            direction,



            "EXIT:",



            price,



            "PNL:",



            round(



                pnl,



                2



            ),



            "原因:",



            reason



        )









        # ====================================================
        # 清理
        # ====================================================


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









    # ========================================================
    # 当前持仓
    # ========================================================


    def get_position(
        self
    ):


        return self.position











    # ========================================================
    # 实时持仓状态
    # ========================================================


    def get_position_status(
        self,
        price
    ):


        if self.position is None:



            return None






        entry = self.position["entry"]






        size = self.position.get(



            "size_btc",



            0



        )






        direction = self.normalize_direction(



            self.position.get(



                "direction"



            )



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



                self.position.get(



                    "stop_loss"



                ),





            "take_profit":



                self.position.get(



                    "take_profit"



                ),





            "hold_minutes":



                round(



                    hold_time / 60,



                    1



                ),





            "size_btc":



                size



        }









    # ========================================================
    # 历史交易
    # ========================================================


    def get_history(
        self
    ):


        return self.history