# ============================================================
# btc_strategy_v10.2.2.py
#
# BTC AI Assistant V10.2.2
#
# Strategy Engine
#
# Upgrade:
#
# V10.2.2
#
# 1. 优化成交量过滤
# 2. 增加趋势评分系统
# 3. 优化 bearish_rebound 空头逻辑
# 4. 增加最小风险收益过滤
# 5. 修复策略层和执行层止损冲突
# 6. 强化BTC 5分钟永续适配
# 7. 保留V10.2接口兼容
#
# ============================================================


from config.strategy_config import STRATEGY_CONFIG





class BTCStrategy:



    def __init__(
        self
    ):


        self.name = "BTCStrategy_V10.4.1_Optimized"





    # ============================================================
    # 兼容旧调用接口
    #
    # 支持:
    #
    # generate(
    #     market,
    #     indicators
    # )
    #
    # 老版本:
    #
    # generate(
    #     price,
    #     indicators,
    #     market
    # )
    #
    # ============================================================


    def generate(
        self,
        market,
        indicators,
        *args,
        **kwargs
    ):



        if isinstance(
            market,
            (
                int,
                float
            )
        ):



            price = market



            if len(args) > 0 and isinstance(
                args[0],
                dict
            ):


                market = args[0]



            else:


                market = {


                    "trend":

                        "neutral",


                    "score":

                        0,


                    "confidence":

                        0

                }




            if isinstance(
                indicators,
                dict
            ):


                indicators["price"] = price






        return self.generate_signal(

            market,

            indicators

        )







    # ============================================================
    # 核心信号生成
    #
    # V10.2.2
    #
    # ============================================================


    def generate_signal(
        self,
        market,
        indicators
    ):



        signal = {


            "direction":

                "NONE",


            "action":

                "WAIT",


            "entry":

                None,


            "stop_loss":

                None,


            "take_profit":

                None,


            "risk_reward":

                None,


            "confidence":

                0,


            "score":

                0,


            "reason":

                [],



            "market_data":

                {},



            "indicators":

                {}

        }






        if market is None:


            signal["reason"].append(

                "市场数据为空"

            )


            return signal






        if indicators is None:


            signal["reason"].append(

                "指标数据为空"

            )


            return signal






        # 保存上下文

        signal["market_data"] = market.copy()


        signal["indicators"] = indicators.copy()







        trend = market.get(

            "trend",

            "neutral"

        )



        market_score = market.get(

            "score",

            0

        )



        confidence = market.get(

            "confidence",

            0

        )


        # V10.4.1 MTF冲突保护
        mtf_alignment = market.get("mtf_alignment", "")
        higher_trend = market.get("higher_trend", "")
        mid_trend = market.get("mid_trend", "")
        lower_trend = market.get("lower_trend", "")

        # V10.4.1 MTF信息仅用于最终入场过滤
        # 不在此处引用direction，避免信号尚未生成导致NameError



        price = indicators.get(

            "price"

        )



        atr = indicators.get(

            "ATR"

        )






        if price is None or atr is None:


            signal["reason"].append(

                "缺少价格或ATR"

            )


            return signal








        # =====================================================
        # 计算交易评分
        #
        # 不再完全依赖market score
        #
        # =====================================================


        trade_score = self.calculate_trade_score(

            trend,

            market_score,

            confidence,

            indicators

        )



        signal["score"] = trade_score








        # =====================================================
        # LONG
        # =====================================================


        if trend in [
            "bullish",
            "bullish_pullback"
        ]:



            if trade_score < STRATEGY_CONFIG.get(

                "ENTRY_SCORE",

                60

            ):



                signal["reason"].append(

                    "多头评分不足"

                )


                return signal







            check = self.check_entry_filter(

                "LONG",

                market,

                indicators

            )



            if not check["allow"]:


                signal["reason"].extend(

                    check["reason"]

                )


                return signal







            signal["direction"] = "LONG"


            signal["action"] = "ENTER"



            signal["entry"] = price



            signal["stop_loss"] = self.calculate_stop_loss(

                "LONG",

                price,

                atr

            )



            signal["take_profit"] = self.calculate_take_profit(

                "LONG",

                price,

                atr

            )



            signal["risk_reward"] = self.calculate_risk_reward(

                price,

                signal["stop_loss"],

                signal["take_profit"]

            )



            signal["confidence"] = confidence



            signal["reason"].append(

                "多头趋势确认"

            )



            return signal

        # =====================================================
# SHORT判断
# =====================================================


        if trend in [

            "bearish",

            "bearish_rebound"

        ]:



            if trade_score > -STRATEGY_CONFIG.get(

                "ENTRY_SCORE",

                60

            ):



                signal["reason"].append(

                    "空头评分不足"

                )


                return signal








            check = self.check_entry_filter(

                "SHORT",

                market,

                indicators

            )



            if not check["allow"]:


                signal["reason"].extend(

                    check["reason"]

                )


                return signal








            signal["direction"] = "SHORT"


            signal["action"] = "ENTER"



            signal["entry"] = price



            signal["stop_loss"] = self.calculate_stop_loss(

                "SHORT",

                price,

                atr

            )



            signal["take_profit"] = self.calculate_take_profit(

                "SHORT",

                price,

                atr

            )



            signal["risk_reward"] = self.calculate_risk_reward(

                price,

                signal["stop_loss"],

                signal["take_profit"]

            )



            signal["confidence"] = confidence



            signal["reason"].append(

                "空头趋势确认"

            )


            return signal







        signal["reason"].append(

            "等待确认"

        )


        return signal








    # ============================================================
    # 交易评分系统
    #
    # V10.2.2
    #
    # 综合:
    #
    # 趋势
    # EMA
    # MACD
    # VWAP
    # RSI
    # 成交量
    #
    # ============================================================


    def calculate_trade_score(
        self,
        trend,
        market_score,
        confidence,
        indicators
    ):



        score = 0



        ema20 = indicators.get(

            "EMA20",

            0

        )


        ema50 = indicators.get(

            "EMA50",

            0

        )


        macd = indicators.get(

            "MACD",

            0

        )


        price = indicators.get(

            "price",

            0

        )


        vwap = indicators.get(

            "VWAP",

            0

        )


        rsi = indicators.get(

            "RSI",

            50

        )


        volume = indicators.get(

            "VOLUME_RATIO",

            0

        )






        # ====================================================
        # 趋势方向
        # ====================================================


        if trend in [
            "bullish",
            "bullish_pullback"
        ]:


            score += 30



        elif trend in [

            "bearish",

            "bearish_rebound"

        ]:


            score -= 30







        # ====================================================
        # EMA趋势
        # ====================================================


        if ema20 and ema50:



            if ema20 > ema50:


                score += 20



            elif ema20 < ema50:


                score -= 20







        # ====================================================
        # MACD
        # ====================================================


        if macd > 0:


            score += 15



        elif macd < 0:


            score -= 15







        # ====================================================
        # VWAP
        # ====================================================


        if vwap and price:



            if price > vwap:


                score += 10



            else:


                score -= 10







        # ====================================================
        # RSI
        # ====================================================


        if 40 <= rsi <= 65:


            score += 10



        elif rsi > 75:


            score -= 10



        elif rsi < 25:


            score -= 10







        # ====================================================
        # 成交量
        # ====================================================


        if volume >= 0.8:


            score += 10



        elif volume < 0.25:


            score -= 10






        # ====================================================
        # confidence修正
        # ====================================================


        if confidence >= 70:


            score += 10



        elif confidence < 50:


            score -= 10







        return score











    # ============================================================
    # 成交量过滤
    #
    # V10.2.2
    #
    # 不再硬性禁止全部低量
    #
    # ============================================================


    def check_volume(
        self,
        volume_ratio
    ):



        if volume_ratio is None:


            return False





        if volume_ratio < STRATEGY_CONFIG.get(

            "MIN_VOLUME_RATIO_BLOCK",

            0.20

        ):


            return False





        return True


        # ============================================================
    # V10.2.2 入场过滤
    #
    # ============================================================


    def check_entry_filter(
        self,
        direction,
        market,
        indicators
    ):



        result = {


            "allow":

                True,


            "reason":

                []

        }





        confidence = market.get(

            "confidence",

            0

        )


        trend = market.get(

            "trend",

            "neutral"

        )



        price = indicators.get(

            "price",

            0

        )


        volume_ratio = indicators.get(

            "VOLUME_RATIO",

            0

        )


        rsi = indicators.get(

            "RSI",

            50

        )


        ema20 = indicators.get(

            "EMA20",

            0

        )


        ema50 = indicators.get(

            "EMA50",

            0

        )


        vwap = indicators.get(

            "VWAP",

            0

        )





        # ====================================================
        # confidence
        # ====================================================


        if confidence < STRATEGY_CONFIG.get(

            "MIN_CONFIDENCE",

            50

        ):



            result["allow"] = False


            result["reason"].append(

                "信心不足"

            )







        # ====================================================
        # 成交量
        #
        # V10.2.2:
        #
        # 极低成交量禁止
        #
        # 普通低量允许
        #
        # ====================================================


        if volume_ratio < STRATEGY_CONFIG.get(

            "MIN_VOLUME_RATIO_BLOCK",

            0.20

        ):



            result["allow"] = False


            result["reason"].append(

                "成交量极低"

            )







        # ====================================================
        # SHORT过滤
        # ====================================================


        if direction == "SHORT":




            # RSI超低禁止追空


            if rsi <= STRATEGY_CONFIG.get(

                "RSI_OVERSOLD",

                15

            ):



                result["allow"] = False


                result["reason"].append(

                    "RSI超卖禁止追空"

                )







            # VWAP过滤


            if vwap and price > vwap:



                result["reason"].append(

                     "价格低于VWAP,等待回踩确认"

                )







            # bearish_rebound优化


            if trend == "bearish_rebound":



                # 允许反弹空

                # 但是需要:
                #
                # RSI转弱
                # MACD负值
                # EMA空头



                macd = indicators.get(

                    "MACD",

                    0

                )



                if not (

                    ema20 < ema50

                    and

                    macd < 0

                    and

                    rsi < 75

                ):



                    result["allow"] = False


                    result["reason"].append(

                        "反弹空条件不足"

                    )



                else:



                    result["reason"].append(

                        "反弹空确认"

                    )










        # ====================================================
        # LONG过滤
        # ====================================================


        elif direction == "LONG":





            if rsi >= STRATEGY_CONFIG.get(

                "RSI_OVERBUY",

                85

            ):



                result["allow"] = False


                result["reason"].append(

                    "RSI超买禁止追多"

                )







            if vwap and price < vwap:



                result["allow"] = False


                result["reason"].append(

                    "价格低于VWAP"

                )







        # ====================================================
        # EMA趋势强度
        # ====================================================


        atr = indicators.get(

            "ATR",

            0

        )



        if ema20 and ema50 and atr:



            distance = abs(

                ema20 - ema50

            )



            if distance < atr * 0.2:



                result["allow"] = False


                result["reason"].append(

                    "趋势强度不足"

                )







        return result










    # ============================================================
    # 交易条件检查
    #
    # 保留兼容
    #
    # ============================================================


    def check_trade_condition(
        self,
        market,
        indicators
    ):



        result = {


            "allow":

                False,


            "reason":

                []

        }






        if market is None:



            result["reason"].append(

                "无市场数据"

            )


            return result







        if indicators is None:



            result["reason"].append(

                "无指标数据"

            )


            return result








        confidence = market.get(

            "confidence",

            0

        )



        if confidence < STRATEGY_CONFIG.get(

            "MIN_CONFIDENCE",

            50

        ):



            result["reason"].append(

                "信心不足"

            )


            return result







        result["allow"] = True



        result["reason"].append(

            "交易条件满足"

        )



        return result

        # ============================================================
    # 开仓参数生成
    #
    # ============================================================


    def build_order(
        self,
        direction,
        price,
        atr,
        balance
    ):



        order = {


            "direction":

                direction,


            "entry":

                price,


            "stop_loss":

                None,


            "take_profit":

                None,


            "size_btc":

                0,


            "risk_reward":

                0

        }





        if direction not in [

            "LONG",

            "SHORT"

        ]:


            return order






        order["stop_loss"] = self.calculate_stop_loss(

            direction,

            price,

            atr

        )



        order["take_profit"] = self.calculate_take_profit(

            direction,

            price,

            atr

        )





        order["risk_reward"] = self.calculate_risk_reward(

            price,

            order["stop_loss"],

            order["take_profit"]

        )







        # ====================================================
        # RR过滤
        #
        # V10.2.2
        #
        # ====================================================


        if order["risk_reward"] < STRATEGY_CONFIG.get(

            "MIN_RISK_REWARD",

            1.5

        ):


            return {

                "direction":

                    "NONE",

                "entry":

                    None,

                "stop_loss":

                    None,

                "take_profit":

                    None,

                "size_btc":

                    0,

                "risk_reward":

                    order["risk_reward"]

            }







        order["size_btc"] = self.calculate_position_size(

            balance,

            price,

            STRATEGY_CONFIG.get(

                "DEFAULT_LEVERAGE",

                30

            )

        )




        return order







    # ============================================================
    # 止损计算
    # ============================================================


    def calculate_stop_loss(
        self,
        direction,
        entry,
        atr
    ):


        if direction == "LONG":


            return round(

                entry

                -

                atr *
                STRATEGY_CONFIG.get(

                    "STOP_ATR_MULTIPLE",

                    1.8

                ),

                2

            )




        elif direction == "SHORT":


            return round(

                entry

                +

                atr *
                STRATEGY_CONFIG.get(

                    "STOP_ATR_MULTIPLE",

                    1.8

                ),

                2

            )



        return None







    # ============================================================
    # 止盈计算
    # ============================================================


    def calculate_take_profit(
        self,
        direction,
        entry,
        atr
    ):



        if direction == "LONG":


            return round(

                entry

                +

                atr *
                STRATEGY_CONFIG.get(

                    "TAKE_PROFIT_ATR_MULTIPLE",

                    3.2

                ),

                2

            )





        elif direction == "SHORT":


            return round(

                entry

                -

                atr *
                STRATEGY_CONFIG.get(

                    "TAKE_PROFIT_ATR_MULTIPLE",

                    3.2

                ),

                2

            )



        return None







    # ============================================================
    # 仓位计算
    #
    # V10.2.2
    #
    # 风险模型
    #
    # ============================================================


    def calculate_position_size(
        self,
        balance,
        price,
        leverage
    ):



        if balance <= 0 or price <= 0:


            return 0






        risk_percent = STRATEGY_CONFIG.get(

            "MAX_POSITION_RISK",

            0.01

        )



        risk_amount = balance * risk_percent





        return round(

            (

                risk_amount

                /

                price

            )

            *

            leverage,

            4

        )







    # ============================================================
    # 风险收益比
    # ============================================================


    def calculate_risk_reward(
        self,
        entry,
        stop_loss,
        take_profit
    ):



        risk = abs(

            entry

            -

            stop_loss

        )



        reward = abs(

            take_profit

            -

            entry

        )



        if risk <= 0:


            return 0





        return round(

            reward / risk,

            2

        )







    # ============================================================
    # 完整交易决策
    #
    # ============================================================


    def generate_trade_signal(
        self,
        market,
        indicators,
        balance=0
    ):



        result = self.generate_signal(

            market,

            indicators

        )





        if result["action"] != "ENTER":


            return result





        order = self.build_order(

            result["direction"],

            result["entry"],

            indicators.get(

                "ATR"

            ),

            balance

        )



        result.update(

            order

        )



        if result.get(

            "direction"

        ) == "NONE":


            result["action"] = "WAIT"


            result["reason"].append(

                "风险收益比不足"

            )



        return result







    # ============================================================
    # 持仓管理
    #
    # 注意:
    #
    # V10.2.2
    #
    # 移动止损交给PaperTrader
    #
    # ============================================================


    def manage_position(
        self,
        position,
        price,
        atr
    ):



        return {


            "action":

                "HOLD",


            "stop_loss":

                position.get(

                    "stop_loss"

                )

                if position

                else None,


            "reason":

                [

                    "执行层管理移动止损"

                ]

        }








    # ============================================================
    # 单例
    # ============================================================


btc_strategy = BTCStrategy()





# ============================================================
# 文件结束
#
# BTC AI Assistant V10.2.2
#
# strategy/btc_strategy_v10.2.2.py
#
# ============================================================
    