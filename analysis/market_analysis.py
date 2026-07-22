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
                "trend": "neutral",
                "market_mode": "UNKNOWN",
                "score": 0,
                "signal": "WAIT",
                "confidence": 0,
                "reason": [
                    "没有K线数据"
                ],
                "warning": [
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

        volume_ratio = indicators.get(
            "VOLUME_RATIO",
            0
        )

        vwap = indicators.get(
            "VWAP"
        )


        price = candles[-1]["close"]


        # =====================
        # 初始化
        # =====================

        signal = "WAIT"

        market_mode = "TREND"



        # =====================
        # ATR市场模式
        # =====================

        if atr is not None and price > 0:

            atr_ratio = atr / price


            if atr_ratio < 0.0005:

                market_mode = "RANGE"

                warning.append(
                    "ATR过低，市场震荡"
                )



        # =====================
        # EMA趋势判断
        #
        # V10.1.7
        # 提高趋势确认要求
        # =====================

        ema_trend = 0


        if ema20 is not None and ema50 is not None:


            ema_diff = (
                ema20 - ema50
            ) / ema50



            # 提高到0.12%

            if ema_diff > 0.0012:

                ema_trend = 1

                score += 30

                reason.append(
                    "EMA多头排列"
                )


            elif ema_diff < -0.0012:

                ema_trend = -1

                score -= 30

                reason.append(
                    "EMA空头排列"
                )


            else:

                warning.append(
                    "EMA趋势不足"
                )



        # =====================
        # RSI分析
        #
        # V10.1.7核心修改
        # 防止RSI16追多
        # =====================


        extreme_rsi = False


        if rsi is not None:


            if rsi >= 75:

                score -= 15

                warning.append(
                    "RSI超买"
                )


            elif 60 <= rsi < 75:

                score += 5

                warning.append(
                    "RSI偏高"
                )


            elif 45 <= rsi < 60:

                score += 5

                reason.append(
                    "RSI正常"
                )


            elif 30 <= rsi < 45:

                score -= 5

                reason.append(
                    "RSI偏弱"
                )


            elif rsi < 30:

                extreme_rsi = True

                score += 0

                warning.append(
                    "RSI极端超卖"
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
        # 成交量分析
        #
        # V10.1.7
        # 增加开仓过滤
        # =====================


        if volume_ratio is not None:


            if volume_ratio >= 2:


                score += 20


                reason.append(
                    "成交量明显放大"
                )


            elif volume_ratio >= 0.8:


                score += 10


                reason.append(
                    "成交量正常"
                )


            else:


                warning.append(
                    "成交量不足"
                )



        # =====================
        # VWAP分析
        #
        # 保留评分模式
        # =====================


        if vwap is not None and price > 0:


            if price > vwap:


                score += 5


                reason.append(
                    "价格位于VWAP上方"
                )


            else:


                score -= 5


                reason.append(
                    "价格位于VWAP下方"
                )



        # =====================
        # EMA20偏离保护
        #
        # 防止追涨
        # =====================


        ema_deviation = 0


        if ema20 is not None:


            ema_deviation = (

                price - ema20

            ) / ema20



            if ema_deviation > 0.012:


                score -= 15


                warning.append(
                    "价格偏离EMA20"
                )


            elif ema_deviation < -0.012:


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



        # V10.1.9.1 趋势状态增强
        # 增加 bullish_pullback / bearish_rebound

        if (
            ema20 is not None
            and
            ema50 is not None
            and
            macd is not None
        ):

            if (
                ema20 > ema50
                and
                macd > 0
                and
                price < ema20
                and
                price > ema50 - (atr or 0) * 0.5
            ):

                trend = "bullish_pullback"

                reason.append(
                    "上涨趋势回踩EMA确认"
                )

            elif (
                ema20 < ema50
                and
                macd < 0
                and
                price > ema20
                and
                price < ema50 + (atr or 0) * 0.5
            ):

                trend = "bearish_rebound"

                reason.append(
                    "下降趋势反弹确认"
                )

            elif trend_point >= 2:

                trend = "bullish"

            elif trend_point <= -2:

                trend = "bearish"

            else:

                trend = "neutral"

        else:

            trend = "neutral"



        # =====================
        # V10.1.7 极端RSI保护
        #
        # RSI <30 不允许BUY
        # =====================


        if extreme_rsi:


            warning.append(
                "等待RSI修复确认"
            )



        # =====================
        # RANGE震荡模式
        # =====================


        if market_mode == "RANGE":


            if (
                rsi is not None
                and
                rsi < 35
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
                rsi > 65
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
        # TREND趋势模式
        # =====================


        if (
            market_mode == "TREND"
            and
            signal == "WAIT"
        ):



            # =====================
            # 多头趋势
            # =====================


            if trend in [
                "bullish",
                "bullish_pullback"
            ]:


                risk_warning = [

                    x for x in warning

                    if x not in [

                        "RSI极端超卖"

                    ]

                ]


                # V10.1.7
                # BUY提高门槛


                if (
                    score >= 75
                    and
                    not extreme_rsi
                    and
                    rsi is not None
                    and
                    rsi > 35
                    and
                    volume_ratio >= 0.8
                    and
                    len(risk_warning) == 0
                ):


                    signal = "BUY"


                    reason.append(
                        "多头趋势确认"
                    )



                elif score >= 55:


                    signal = "WAIT_LONG"


                elif score >= 40:


                    signal = "WAIT_CONFIRM"


                    reason.append(
                        "等待多头确认"
                    )




            # =====================
            # 空头趋势
            # =====================


            elif trend == "bearish":


                risk_warning = [

                    x for x in warning

                    if x not in [

                        "RSI极端超卖"

                    ]

                ]


                if (
                    score <= -75
                    and
                    rsi is not None
                    and
                    rsi < 65
                    and
                    volume_ratio >= 0.8
                    and
                    len(risk_warning) == 0
                ):


                    signal = "SELL"


                    reason.append(
                        "空头趋势确认"
                    )



                elif score <= -45:


                    signal = "WAIT_SHORT"


                    reason.append(
                        "等待空头确认"
                    )

                # =====================
        # 趋势初期增强
        #
        # V10.1.7
        # 保留V8逻辑
        # =====================


        if (
            market_mode == "TREND"
            and
            signal == "WAIT"
        ):


            # 初期多头


            if (
                ema20 is not None
                and
                ema50 is not None
                and
                macd is not None
                and
                rsi is not None
                and
                ema20 > ema50
                and
                macd > 0
                and
                rsi >= 45
                and
                score >= 20
            ):


                signal = "WAIT_LONG"


                reason.append(
                    "趋势初期多头机会"
                )



            # 初期空头


            elif (
                ema20 is not None
                and
                ema50 is not None
                and
                macd is not None
                and
                rsi is not None
                and
                ema20 < ema50
                and
                macd < 0
                and
                rsi <= 55
                and
                score <= -20
            ):


                signal = "WAIT_SHORT"


                reason.append(
                    "趋势初期空头机会"
                )



        # =====================
        # WAIT_LONG增强确认
        #
        # 防止假多
        # =====================


        if signal == "WAIT_LONG":


            if extreme_rsi:


                signal = "WAIT"


                reason.append(
                    "RSI极端，等待修复"
                )


            elif (
                volume_ratio is not None
                and
                volume_ratio < 0.5
            ):


                signal = "WAIT"


                reason.append(
                    "成交量不足"
                )



        # =====================
        # WAIT_SHORT增强确认
        # =====================


        if signal == "WAIT_SHORT":


            if (
                volume_ratio is not None
                and
                volume_ratio < 0.5
            ):


                signal = "WAIT"


                reason.append(
                    "成交量不足"
                )



        # =====================
        # 趋势反转机会
        #
        # V10.1.7 合并版
        #
        # 删除重复覆盖
        # =====================


        if (
            signal == "WAIT"
            and
            market_mode == "TREND"
        ):



            # 多头反转


            if (
                ema20 is not None
                and
                ema50 is not None
                and
                macd is not None
                and
                rsi is not None
                and
                price > ema20
                and
                macd > 0
                and
                rsi >= 50
                and
                ema20 >= ema50 * 0.999
            ):


                signal = "WAIT_REVERSAL_LONG"


                reason.append(
                    "趋势反转多头机会"
                )



            # 空头反转


            elif (
                ema20 is not None
                and
                ema50 is not None
                and
                macd is not None
                and
                rsi is not None
                and
                price < ema20
                and
                macd < 0
                and
                rsi <= 50
                and
                ema20 <= ema50 * 1.001
            ):


                signal = "WAIT_REVERSAL_SHORT"


                reason.append(
                    "趋势反转空头机会"
                )



        # =====================
        # 最终保护
        #
        # V10.1.7
        # 禁止极端RSI开仓信号
        # =====================


        if extreme_rsi:


            if signal in [
                "BUY",
                "SELL"
            ]:


                signal = "WAIT"


                reason.append(
                    "极端RSI取消开仓"
                )



        # =====================
        # confidence
        # =====================


        confidence = max(
            0,
            min(
                abs(score),
                100
            )
        )


        # V10.1.9.1 趋势状态置信度修正
        if trend in [
            "bullish_pullback",
            "bearish_rebound"
        ]:

            confidence = min(
                confidence + 10,
                100
            )



        return {


            "trend":

                trend,


            "market_mode":

                market_mode,


            "score":

                score,


            "signal":

                signal,


            "confidence":

                confidence,


            "reason":

                reason,


            "warning":

                warning

        }
