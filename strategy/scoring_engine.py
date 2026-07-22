# ============================================================
# scoring_engine_v10.2.py
#
# BTC AI Assistant V10.2
#
# 统一评分引擎
#
# 目标:
# 1. 与 market_analysis.py 输出统一
# 2. 与 test_scoring.py 使用同一模型
# 3. 支持多空评分
# 4. 不直接执行交易
#
# 输出:
#
# {
#   trend,
#   market_mode,
#   score,
#   signal,
#   confidence,
#   reason,
#   warning
# }
#
# ============================================================


class ScoringEngine:


    def __init__(self):

        self.max_score = 100



    # ========================================================
    # 主入口
    # ========================================================


    def evaluate(
        self,
        indicators
    ):


        score = 0


        reasons = []


        warnings = []



        # ====================================================
        # 数据读取
        # ====================================================


        price = float(

            indicators.get(
                "price",
                0
            )

        )


        ema20 = float(

            indicators.get(
                "EMA20",
                0
            )

        )


        ema50 = float(

            indicators.get(
                "EMA50",
                0
            )

        )


        rsi = float(

            indicators.get(
                "RSI",
                50
            )

        )


        macd = float(

            indicators.get(
                "MACD",
                0
            )

        )


        vwap = float(

            indicators.get(
                "VWAP",
                0
            )

        )


        volume_ratio = float(

            indicators.get(
                "VOLUME_RATIO",
                1
            )

        )


        atr_percent = float(

            indicators.get(
                "ATR_PERCENT",
                0
            )

        )




        # ====================================================
        # 市场模式
        # ====================================================


        market_mode = "TREND"



        if atr_percent < 0.0005:


            market_mode = "RANGE"


            warnings.append(

                "ATR过低，市场震荡"

            )



        # ====================================================
        # EMA趋势评分
        # ====================================================


        ema_trend = 0



        if ema20 > ema50:


            ema_trend = 1


            diff = (

                ema20 - ema50

            ) / ema50



            if diff >= 0.0012:


                score += 30


                reasons.append(

                    "EMA多头排列"

                )


            else:


                score += 20


                reasons.append(

                    "EMA弱多头"

                )



        elif ema20 < ema50:


            ema_trend = -1


            diff = (

                ema50 - ema20

            ) / ema50



            if diff >= 0.0012:


                score -= 30


                reasons.append(

                    "EMA空头排列"

                )


            else:


                score -= 20


                reasons.append(

                    "EMA弱空头"

                )



        else:


            warnings.append(

                "EMA趋势不足"

            )



        # ====================================================
        # EMA20价格位置
        # ====================================================


        if price > ema20:


            score += 5


            reasons.append(

                "价格站上EMA20"

            )


        elif price < ema20:


            score -= 10


            warnings.append(

                "价格弱于EMA20"

            )

                # ====================================================
        # MACD趋势评分
        # ====================================================


        macd_trend = 0



        if macd > 0:


            macd_trend = 1


            score += 20


            reasons.append(

                "MACD多头确认"

            )


        elif macd < 0:


            macd_trend = -1


            score -= 20


            reasons.append(

                "MACD空头确认"

            )


        else:


            warnings.append(

                "MACD无方向"

            )



        # ====================================================
        # RSI评分
        #
        # 避免极端追单
        # ====================================================


        extreme_rsi = False



        if rsi >= 75:


            score -= 15


            warnings.append(

                "RSI超买"

            )



        elif 60 <= rsi < 75:


            score += 5


            warnings.append(

                "RSI偏高"

            )



        elif 45 <= rsi < 60:


            score += 10


            reasons.append(

                "RSI正常"

            )



        elif 35 <= rsi < 45:


            score += 5


            reasons.append(

                "RSI回调区域"

            )



        elif 30 <= rsi < 35:


            score -= 5


            warnings.append(

                "RSI偏弱"

            )



        elif rsi < 30:


            extreme_rsi = True


            warnings.append(

                "RSI极端超卖"

            )



        # ====================================================
        # VWAP评分
        # ====================================================


        if vwap > 0:


            if price > vwap:


                score += 5


                reasons.append(

                    "价格位于VWAP上方"

                )


            else:


                score -= 10


                reasons.append(

                    "价格位于VWAP下方"

                )



        # ====================================================
        # 成交量评分
        # ====================================================


        if volume_ratio >= 1.5:


            score += 15


            reasons.append(

                "成交量明显放大"

            )



        elif volume_ratio >= 0.8:


            score += 10


            reasons.append(

                "成交量正常"

            )



        elif volume_ratio < 0.5:


            score -= 15


            warnings.append(

                "成交量不足"

            )



        else:


            score -= 5


            warnings.append(

                "成交量偏低"

            )



        # ====================================================
        # ATR风险过滤
        # ====================================================


        if atr_percent > 0.004:


            score -= 10


            warnings.append(

                "波动过大"

            )



        # ====================================================
        # 趋势判断
        # ====================================================


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



        # ====================================================
        # 分数限制
        #
        # 保留多空方向
        # ====================================================


        score = max(

            -100,

            min(

                100,

                score

            )

        )

        # ====================================================
        # 信号生成
        #
        # 与 market_analysis.py 统一
        # ====================================================


        signal = "WAIT"



        # ====================================================
        # 多头信号
        # ====================================================


        if trend == "bullish":


            # 强确认多头


            if (

                score >= 75

                and

                not extreme_rsi

                and

                volume_ratio >= 0.8

            ):


                signal = "BUY"


                reasons.append(

                    "多头趋势确认"

                )



            # 等待确认


            elif score >= 45:


                signal = "WAIT_LONG"


                reasons.append(

                    "等待多头确认"

                )



        # ====================================================
        # 空头信号
        # ====================================================


        elif trend == "bearish":



            if (

                score <= -75

                and

                rsi < 70

                and

                volume_ratio >= 0.8

            ):


                signal = "SELL"


                reasons.append(

                    "空头趋势确认"

                )



            elif score <= -45:


                signal = "WAIT_SHORT"


                reasons.append(

                    "等待空头确认"

                )



        # ====================================================
        # 中性市场
        # ====================================================


        else:


            if score >= 40:


                signal = "WAIT_LONG"



                reasons.append(

                    "趋势未完全确认"

                )



            elif score <= -40:


                signal = "WAIT_SHORT"



                reasons.append(

                    "趋势未完全确认"

                )



        # ====================================================
        # 最终交易保护
        # ====================================================


        if extreme_rsi:


            if signal in [

                "BUY",

                "SELL"

            ]:


                signal = "WAIT"


                reasons.append(

                    "极端RSI取消交易"

                )



        if volume_ratio < 0.5:


            if signal in [

                "BUY",

                "SELL"

            ]:


                signal = "WAIT"


                reasons.append(

                    "成交量不足取消交易"

                )



        # ====================================================
        # confidence
        # ====================================================


        confidence = abs(

            score

        )



        confidence = min(

            100,

            confidence

        )



        # ====================================================
        # 返回统一格式
        # ====================================================


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

                reasons,


            "warning":

                warnings

        }





# ============================================================
# 单例
# ============================================================


scoring_engine = ScoringEngine()