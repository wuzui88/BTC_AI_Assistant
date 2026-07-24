# ============================================================
# scoring_engine.py
#
# BTC AI Assistant V10.3.2 FINAL
#
# Multi Timeframe Scoring Engine
#
# Compatible:
#
# V10.2 evaluate(data)
#
# Upgrade:
#
# 1. 保留旧接口
# 2. 增加MTF支持
# 3. 增加趋势保护
# 4. 增加反弹识别
# 5. 优化信号过滤
#
# ============================================================





class ScoringEngine:



    def __init__(self):


        self.name = "ScoringEngine_V10.3.2"







    # ========================================================
    # 主入口
    #
    # 兼容:
    #
    # scoring_engine.evaluate(data)
    #
    # ========================================================


    def evaluate(
        self,
        data
    ):



        result = {


            "trend":

                "neutral",


            "market_mode":

                "TREND",


            "score":

                0,


            "confidence":

                0,


            "signal":

                "WAIT",


            "reason":

                [],


            "warning":

                []

        }





        if data is None:


            result["warning"].append(

                "无指标数据"

            )


            return result







        # ====================================================
        # 基础指标评分
        #
        # ====================================================


        indicator_score = self.calculate_indicator_score(

            data,

            result

        )






        # ====================================================
        # MTF评分
        #
        # 如果不存在MTF
        #
        # 自动兼容旧版本
        #
        # ====================================================


        mtf_score = self.calculate_mtf_score(

            data,

            result

        )








        # ====================================================
        # 综合评分
        #
        # MTF 60%
        # 指标 40%
        #
        # ====================================================


        if "MTF" in data:


            final_score = int(


                mtf_score * 0.6

                +

                indicator_score * 0.4


            )


        else:


            final_score = indicator_score







        # 限制范围


        final_score = max(

            -100,

            min(

                100,

                final_score

            )

        )





        result["score"] = final_score





        result["confidence"] = abs(

            final_score

        )







        # ====================================================
        # 趋势判断
        #
        # ====================================================


        result["trend"] = self.detect_trend(

            final_score,

            result

        )







        # ====================================================
        # 信号生成
        #
        # ====================================================
        result["signal"] = self.apply_mtf_filter(
            result,
            data
)

        result["signal"] = self.generate_signal(

            result

        )

        result["signal"] = self.apply_mtf_guard(
            result,
            data
        )







        # ====================================================
        # 市场模式
        #
        # ====================================================


        result["market_mode"] = self.detect_market_mode(

            data,

            result

        )





        return result











    # ========================================================
    # 技术指标评分
    #
    # ========================================================
    def apply_mtf_filter(
        self,
        result,
        data
    ):


        mtf = data.get(
            "MTF",
            {}
        )


        h1 = mtf.get(
            "1H",
            {}
        )


        m15 = mtf.get(
            "15M",
            {}
        )



        h1_trend = h1.get(
            "trend",
            "neutral"
        )


        m15_trend = m15.get(
            "trend",
            "neutral"
        )



        signal = result["signal"]


        return signal


    def apply_mtf_guard(
        self,
        result,
        data
    ):


        mtf = data.get(
            "MTF",
            {}
        )


        h1 = mtf.get(
            "1H",
            {}
        )


        m15 = mtf.get(
            "15M",
            {}
        )


        m5 = mtf.get(
            "5M",
            {}
        )



        h1_trend = h1.get(
            "trend",
            "neutral"
        )


        m15_trend = m15.get(
            "trend",
            "neutral"
        )


        m5_trend = m5.get(
            "trend",
            "neutral"
        )



        signal = result["signal"]



        # ====================================================
        # 三周期一致多头
        # ====================================================

        if (

            h1_trend == "bullish"

            and

            m15_trend == "bullish"

            and

            m5_trend == "bullish"

        ):


            result["reason"].append(
                "MTF三周期一致多头"
            )



        # ====================================================
        # 三周期一致空头
        # ====================================================

        if (

            h1_trend == "bearish"

            and

            m15_trend == "bearish"

            and

            m5_trend == "bearish"

        ):


            result["reason"].append(
                "MTF三周期一致空头"
            )



        # ====================================================
        # 高周期空头压制
        # 禁止追多
        # ====================================================

        if (

            h1_trend == "bearish"

            and

            m15_trend == "bearish"

        ):


            if m5_trend == "bearish":


                if "MTF三周期一致空头" not in result["reason"]:


                    result["reason"].append(
                        "MTF三周期一致空头"
                    )


            elif m5_trend == "bullish":


                result["warning"].append(
                    "高周期空头压制"
                )


                if signal == "BUY":

                    return "WAIT_LONG"
                        


        # ====================================================
        # 高周期多头
        # ====================================================


        if (

            h1_trend == "bullish"

            and

            m15_trend == "bullish"

        ):


            # 三周期一致

            if m5_trend == "bullish":


                if "MTF三周期一致多头" not in result["reason"]:


                    result["reason"].append(
                        "MTF三周期一致多头"
                    )


            # 5分钟反向

            elif m5_trend == "bearish":


                result["warning"].append(
                    "高周期多头支撑"
                )


                if signal == "SELL":

                    return "WAIT_SHORT"


        return signal

    def calculate_indicator_score(
        self,
        data,
        result
    ):



        score = 0






        price = data.get(

            "price",

            0

        )



        ema20 = data.get(

            "EMA20",

            0

        )



        ema50 = data.get(

            "EMA50",

            0

        )



        macd = data.get(

            "MACD",

            0

        )



        rsi = data.get(

            "RSI",

            50

        )



        vwap = data.get(

            "VWAP",

            0

        )



        volume = data.get(

            "VOLUME_RATIO",

            1

        )








        # ====================================================
        # EMA
        # ====================================================


        if ema20 and ema50:



            if ema20 > ema50:


                score += 20


                result["reason"].append(

                    "EMA多头排列"

                )



            elif ema20 < ema50:


                score -= 20


                result["reason"].append(

                    "EMA空头排列"

                )







        # ====================================================
        # 价格与EMA20
        # ====================================================


        if price and ema20:



            if price > ema20:


                score += 10


                result["reason"].append(

                    "价格站上EMA20"

                )



            else:


                score -= 10


                result["warning"].append(

                    "价格弱于EMA20"

                )







        # ====================================================
        # MACD
        # ====================================================


        if macd > 0:


            score += 15


            result["reason"].append(

                "MACD多头确认"

            )



        elif macd < 0:


            score -= 15


            result["reason"].append(

                "MACD空头确认"

            )







        # ====================================================
        # RSI
        # ====================================================


        # ====================================================
        # RSI
        #
        # V10.3.2 修正
        #
        # ====================================================


        if 40 <= rsi <= 60:


            score +=10


            result["reason"].append(

                "RSI回调区域"

            )



        elif 30 <= rsi < 40:


            score -=5


            result["warning"].append(

                "RSI偏弱"

            )



        elif rsi < 30:


            score -=10


            result["warning"].append(

                "RSI超卖"

            )



        elif rsi > 70:


            score -=10


            result["warning"].append(

                "RSI偏高"

            )


        # ====================================================
        # VWAP
        # ====================================================


        if price and vwap:



            if price > vwap:


                score += 10


                result["reason"].append(

                    "价格位于VWAP上方"

                )



            else:


                score -= 10


                result["reason"].append(

                    "价格位于VWAP下方"

                )







        # ====================================================
        # Volume
        # ====================================================


        if volume >= 1.2:


            score +=15


            result["reason"].append(

                "成交量明显放大"

            )



        elif volume >=0.8:


            score +=5


            result["reason"].append(

                "成交量正常"

            )



        elif volume >=0.5:


            score -=5


            result["warning"].append(

                "成交量偏低"

            )



        else:


            score -=15


            result["warning"].append(

                "成交量极低"

            )



        return score

        # ========================================================
    # MTF 多周期评分
    #
    # V10.3.2
    #
    # 权重:
    #
    # 1H  = 50%
    # 15M = 30%
    # 5M  = 20%
    #
    # ========================================================


    def calculate_mtf_score(
        self,
        data,
        result
    ):


        mtf = data.get(

            "MTF",

            None

        )



        # ====================================================
        # 兼容旧版本
        #
        # 没有MTF时
        #
        # ====================================================


        if not mtf:



            return self.get_simple_trend_score(

                data

            )







        score = 0





        weights = {


            "1H":

                0.5,


            "15M":

                0.3,


            "5M":

                0.2

        }







        for timeframe, weight in weights.items():


            timeframe_data = mtf.get(

                timeframe,

                {}

            )


            trend = timeframe_data.get(

                "trend",

                "neutral"

            )


            timeframe_score = timeframe_data.get(

                "score",

                0

            )



            # 优先使用多周期自身评分

            if timeframe_score:


                score += (

                    timeframe_score

                    *

                    weight

                )



            else:


                if trend == "bullish":


                    score += (

                        100

                        *

                        weight

                    )


                elif trend == "bearish":


                    score -= (

                        100

                        *

                        weight

                    )





        return int(score)









    # ========================================================
    # 简单趋势评分
    #
    # V10.2兼容
    #
    # ========================================================


    def get_simple_trend_score(
        self,
        data
    ):



        score = 0





        ema20 = data.get(

            "EMA20",

            0

        )


        ema50 = data.get(

            "EMA50",

            0

        )


        macd = data.get(

            "MACD",

            0

        )



        price = data.get(

            "price",

            0

        )


        vwap = data.get(

            "VWAP",

            0

        )







        if ema20 and ema50:



            if ema20 > ema50:


                score += 30


            else:


                score -= 30







        if macd > 0:


            score += 20



        elif macd < 0:


            score -= 20







        if price and vwap:



            if price > vwap:


                score += 20


            else:


                score -= 20







        return score











    # ========================================================
    # 趋势识别
    #
    # ========================================================


    def detect_trend(
        self,
        score,
        result
    ):



        mtf = result.get(

            "mtf",

            {}

        )



        if score >= 50:


            return "bullish"





        elif score <= -50:


            return "bearish"






        return "neutral"

        # ========================================================
    # 信号生成
    #
    # ========================================================


    def generate_signal(
        self,
        result
    ):



        score = result.get(

            "score",

            0

        )



        trend = result.get(

            "trend",

            "neutral"

        )






        # ====================================================
        # 强多
        # ====================================================


        if trend == "bullish":



            if score >= 70:


                result["reason"].append(

                    "多头趋势确认"

                )


                return "BUY"




            else:


                result["reason"].append(

                    "等待多头确认"

                )


                return "WAIT_LONG"








        # ====================================================
        # 强空
        # ====================================================


        elif trend == "bearish":




            if score <= -70:


                result["reason"].append(

                    "空头趋势确认"

                )


                return "SELL"




            else:


                result["reason"].append(

                    "等待空头确认"

                )


                return "WAIT_SHORT"








        # ====================================================
        # 中性
        # ====================================================


        else:



            result["reason"].append(

                "趋势不明确"

            )


            return "WAIT"









    # ========================================================
    # 市场模式识别
    #
    # V10.3.2
    #
    # ========================================================


    def detect_market_mode(
        self,
        data,
        result
    ):



        atr_percent = data.get(

            "ATR_PERCENT",

            0

        )



        volume = data.get(

            "VOLUME_RATIO",

            0

        )



        score = result.get(

            "score",

            0

        )








        # ====================================================
        # 波动不足
        # ====================================================


        if atr_percent < 0.0005:



            result["warning"].append(

                "ATR波动不足"

            )


            return "RANGE"







        # ====================================================
        # 爆量突破
        # ====================================================


        if volume > 2:




            result["reason"].append(

                "成交量突破"

            )



            return "BREAKOUT"








        # ====================================================
        # 趋势市场
        # ====================================================


        if abs(score) >= 40:


            return "TREND"






        return "RANGE"
# ============================================================
# 单例
# ============================================================


scoring_engine = ScoringEngine()