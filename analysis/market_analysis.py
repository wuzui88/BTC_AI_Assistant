class MarketAnalysis:


    def analyze(
        self,
        candles,
        indicators
    ):


        # =====================
        # 数据保护
        # =====================

        if candles is None or len(candles) == 0:


            return {


                "trend":
                    "neutral",


                "market_mode":
                    "UNKNOWN",


                "score":
                    0,


                "signal":
                    "WAIT",


                "confidence":
                    0,


                "reason":
                    [
                        "没有K线数据"
                    ],


                "warning":
                    [
                        "等待行情"
                    ]

            }



        if indicators is None:

            indicators = {}




        score = 0


        reason = []


        warning = []




        # =====================
        # 获取指标
        # =====================


        ema20 = indicators.get(
            "EMA20"
        )


        ema50 = indicators.get(
            "EMA50"
        )


        rsi = indicators.get(
            "RSI"
        )


        macd = indicators.get(
            "MACD"
        )


        atr = indicators.get(
            "ATR"
        )



        price = candles[-1]["close"]




        # =====================
        # ATR波动判断
        # =====================


        market_mode = "TREND"



        if atr is not None and price > 0:


            atr_ratio = atr / price



            # BTC 5分钟
            # ATR低于0.08%
            # 认为震荡

            if atr_ratio < 0.0005:


                market_mode = "RANGE"


                warning.append(

                    "ATR过低，市场震荡"

                )





        # =====================
        # EMA趋势判断
        # =====================


        ema_trend = 0



        if (
            ema20 is not None
            and
            ema50 is not None
        ):



            ema_diff = (

                ema20 - ema50

            ) / ema50



            if ema_diff > 0.0015:


                ema_trend = 1


                score += 30


                reason.append(

                    "EMA多头排列"

                )



            elif ema_diff < -0.0015:


                ema_trend = -1


                score -= 30


                reason.append(

                    "EMA空头排列"

                )



            else:


                warning.append(

                    "EMA距离不足，趋势弱"

                )





        # =====================
        # RSI分析
        # =====================


        if rsi is not None:



            if 50 <= rsi < 60:


                score += 5


                reason.append(

                    "RSI中性"

                )



            elif 65 <= rsi < 75:


                score += 5


                warning.append(

                    "RSI偏高"

                )



            elif rsi >= 75:


                score -= 10


                warning.append(

                    "RSI超买"

                )



            elif 35 <= rsi < 50:


                score -= 10


                reason.append(

                    "RSI偏弱"

                )



            elif rsi < 35:


                score += 5


                warning.append(

                    "RSI超卖"

                )
                # =====================
        # MACD分析
        # =====================


        macd_trend = 0



        if macd is not None:



            if macd > 0:


                macd_trend = 1


                score += 20


                reason.append(

                    "MACD多头确认"

                )



            else:


                macd_trend = -1


                score -= 20


                reason.append(

                    "MACD空头确认"

                )





        # =====================
        # 价格偏离EMA20
        # =====================


        if ema20 is not None:



            deviation = (

                price - ema20

            ) / ema20




            if deviation > 0.012:



                score -= 15


                warning.append(

                    "价格远离EMA20，防止追涨"

                )




            elif deviation < -0.012:



                warning.append(

                    "价格弱于EMA20"

                )






        # =====================
        # 综合趋势
        # =====================


        trend_point = (

            ema_trend

            +

            macd_trend

        )




        if trend_point >= 2:


            trend = "bullish"



        elif trend_point <= -2:


            trend = "bearish"



        else:


            trend = "neutral"






        # =====================
        # RANGE震荡修正
        # =====================


        if market_mode == "RANGE":


            # 震荡行情降低趋势权重

            if trend != "neutral":


                warning.append(

                    "震荡行情，趋势可靠性降低"

                )


            # =====================
            # RANGE震荡反转信号
            # =====================

            if (
                rsi is not None
                and
                rsi < 40
                and
                ema20 is not None
                and
                price <= ema20
                and
                macd is not None
                and
                macd > -50
            ):

                signal = "WAIT_REVERSAL_LONG"

                reason.append(
                    "震荡超卖反弹机会"
                )


            elif (
                rsi is not None
                and
                rsi > 60
                and
                ema20 is not None
                and
                price >= ema20
                and
                macd is not None
                and
                macd < 50
            ):

                signal = "WAIT_REVERSAL_SHORT"

                reason.append(
                    "震荡超买回落机会"
                )




        # =====================
        # 交易信号
        # =====================


        signal = "WAIT"





        # =====================
        # 趋势模式
        # =====================


        if market_mode == "TREND":



            # 多头趋势


            if trend == "bullish":



                risk_warning = [

                    x for x in warning

                    if x not in [

                        "RSI超卖"

                    ]

                ]



                if (

                    score >= 70

                    and

                    len(risk_warning) == 0

                ):



                    signal = "BUY"



                elif score >= 45:



                    signal = "WAIT_LONG"






            # 空头趋势


            elif trend == "bearish":



                risk_warning = [

                    x for x in warning

                    if x not in [

                        "RSI超卖"

                    ]

                ]



                if (

                    score <= -70

                    and

                    len(risk_warning) == 0

                ):



                    signal = "SELL"



                elif score <= -45:



                    signal = "WAIT_SHORT"

                

        # =====================
        # TREND弱趋势机会增强 V3
        # =====================

        if market_mode == "TREND" and signal == "WAIT":

            # 初级多头趋势确认
            if (
                ema20 is not None
                and ema50 is not None
                and ema20 > ema50
                and macd is not None
                and macd > 0
                and rsi is not None
                and rsi >= 45
                and score >= 15
            ):

                signal = "WAIT_LONG"

                reason.append(
                    "趋势初期多头机会"
                )


            # 初级空头趋势确认
            elif (
                ema20 is not None
                and ema50 is not None
                and ema20 < ema50
                and macd is not None
                and macd < 0
                and rsi is not None
                and rsi <= 55
                and score <= -15
            ):

                signal = "WAIT_SHORT"

                reason.append(
                    "趋势初期空头机会"
                )


        # =====================
        # 趋势初期补充信号 V8
        # 防止RSI中性抵消MACD趋势
        # =====================

        if market_mode == "TREND" and signal == "WAIT":

            if (
                ema20 is not None
                and ema50 is not None
                and macd is not None
                and atr is not None
                and ema20 < ema50
                and macd < 0
                and atr / price > 0.0005
            ):

                signal = "WAIT_SHORT"

                reason.append(
                    "趋势初期空头增强"
                )


            elif (
                ema20 is not None
                and ema50 is not None
                and macd is not None
                and atr is not None
                and ema20 > ema50
                and macd > 0
                and atr / price > 0.0005
            ):

                signal = "WAIT_LONG"

                reason.append(
                    "趋势初期多头增强"
                )




        # =====================
        # 趋势反转增强 V9
        # 解决过滤过严导致无交易
        # =====================

        if signal == "WAIT" and market_mode == "TREND":

            # 多头反转确认
            if (
                ema20 is not None
                and ema50 is not None
                and macd is not None
                and rsi is not None
                and price > ema20
                and macd > 0
                and rsi >= 50
                and ema20 >= ema50 * 0.999
            ):
                signal = "WAIT_REVERSAL_LONG"
                reason.append("趋势反转多头机会")

            # 空头反转确认
            elif (
                ema20 is not None
                and ema50 is not None
                and macd is not None
                and rsi is not None
                and price < ema20
                and macd < 0
                and rsi <= 50
                and ema20 <= ema50 * 1.001
            ):
                signal = "WAIT_REVERSAL_SHORT"
                reason.append("趋势反转空头机会")


        # =====================
        # 最终返回
        # =====================

        confidence = score

        return {

            "trend": trend,

            "market_mode": market_mode,

            "score": score,

            "signal": signal,

            "confidence": confidence,

            "reason": reason,

            "warning": warning

        }
