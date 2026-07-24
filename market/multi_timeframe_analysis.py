# ============================================================
# multi_timeframe_analysis.py
#
# BTC AI Assistant V10.3
#
# Multi Timeframe Market Analyzer
#
# 功能:
#
# 1H:
#   主趋势判断
#
# 15M:
#   趋势结构判断
#
# 5M:
#   入场确认
#
# 输出:
#
# {
#   trend,
#   market_mode,
#   entry_signal,
#   score,
#   confidence,
#   reason,
#   warning
# }
#
# ============================================================



class MultiTimeframeAnalyzer:



    def __init__(self):

        self.name = "MTFAnalyzer_V10.3"




    # ========================================================
    # 主入口
    # ========================================================


    def analyze(
        self,
        timeframe_data
    ):


        result = {


            "trend":

                "neutral",


            "market_mode":

                "RANGE",


            "entry_signal":

                "WAIT",


            "score":

                0,


            "confidence":

                0,


            "reason":

                [],


            "warning":

                []

        }




        if not timeframe_data:


            result["warning"].append(

                "无多周期数据"

            )


            return result





        h1_data = timeframe_data.get(
            "1H",
            []
        )

        m15_data = timeframe_data.get(
            "15M",
            []
        )

        m5_data = timeframe_data.get(
            "5M",
            []
        )


        h1 = self.analyze_timeframe(
            h1_data
        ) if len(h1_data) >= 20 else {
            "trend":"neutral",
            "score":0,
            "reason":["1H数据不足"],
            "warning":["1H周期不足"]
        }


        m15 = self.analyze_timeframe(
            m15_data
        ) if len(m15_data) >= 20 else {
            "trend":"neutral",
            "score":0,
            "reason":["15M数据不足"],
            "warning":["15M周期不足"]
        }


        m5 = self.analyze_timeframe(
            m5_data
        ) if len(m5_data) >= 20 else {
            "trend":"neutral",
            "score":0,
            "reason":["5M数据不足"],
            "warning":["5M周期不足"]
        }




        result = self.combine(
            h1,
            m15,
            m5
        )


        result["higher_trend"] = h1.get(
            "trend",
            "unknown"
        )

        result["mid_trend"] = m15.get(
            "trend",
            "unknown"
        )

        result["lower_trend"] = m5.get(
            "trend",
            "unknown"
        )


        result["mtf_score"] = (
            h1.get("score",0)
            +
            m15.get("score",0)
            +
            m5.get("score",0)
        )


        return result

        result["higher_trend"] = h1.get(
            "trend",
            "unknown"
        )

        result["mid_trend"] = m15.get(
            "trend",
            "unknown"
        )

        result["lower_trend"] = m5.get(
            "trend",
            "unknown"
        )


        result["mtf_score"] = (
            h1.get("score",0)
            +
            m15.get("score",0)
            +
            m5.get("score",0)
        )


        return result







    # ========================================================
    # 单周期分析
    # ========================================================


    def analyze_timeframe(
        self,
        data
    ):


        # V10.3 FIX:
        # MTFBuilder传入的是K线列表，不是指标字典。
        # 原逻辑直接data.get("EMA20")会得到默认0，
        # 导致1H/15M/5M全部unknown。
        if isinstance(data, list):

            if len(data) < 20:
                return {
                    "trend": "unknown",
                    "score": 0,
                    "reason": ["周期K线不足"]
                }

            closes = [
                float(x.get("close", 0))
                for x in data
            ]

            def ema(values, period):
                if len(values) < period:
                    return values[-1]

                k = 2 / (period + 1)
                value = sum(values[:period]) / period

                for price in values[period:]:
                    value = price * k + value * (1-k)

                return value


            ema20 = ema(closes, 20)
            ema50 = ema(closes, 50)

            macd = ema(closes, 12) - ema(closes, 26)

            # 简化RSI计算
            gains = []
            losses = []

            for i in range(1, len(closes)):
                diff = closes[i] - closes[i-1]
                if diff >= 0:
                    gains.append(diff)
                    losses.append(0)
                else:
                    gains.append(0)
                    losses.append(abs(diff))

            avg_gain = sum(gains[-14:]) / 14
            avg_loss = sum(losses[-14:]) / 14

            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))

            data = {
                "EMA20": ema20,
                "EMA50": ema50,
                "MACD": macd,
                "RSI": rsi
            }


        score = 0


        reason = []



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




        trend = "neutral"




        # EMA


        if ema20 > ema50:


            score += 40


        elif ema20 < ema50:


            score -= 40





        # MACD


        if macd > 0:


            score += 30


        elif macd < 0:


            score -= 30






        # RSI


        if rsi > 50:


            score += 10


        elif rsi < 50:


            score -= 10






        if score >= 40:


            trend = "bullish"


            reason.append(

                "周期多头结构"

            )



        elif score <= -40:


            trend = "bearish"


            reason.append(

                "周期空头结构"

            )



        else:


            trend = "neutral"


            reason.append(

                "周期方向不明确"

            )





        return {


            "trend":

                trend,


            "score":

                score,


            "reason":

                reason

        }








    # ========================================================
    # 多周期融合
    # ========================================================


    def get_alignment(self, h1, m15, m5):

        trends = [
            h1.get("trend"),
            m15.get("trend"),
            m5.get("trend")
        ]

        if all(t == "bullish" for t in trends):
            return "BULLISH"

        if all(t == "bearish" for t in trends):
            return "BEARISH"

        return "MIXED"


    def combine(
        self,
        h1,
        m15,
        m5
    ):



        score = 0


        reasons = []


        warnings = []




        # ====================================================
        # 1H 权重 50%
        # ====================================================


        score += int(

            h1["score"]

            *

            0.5

        )


        reasons.extend(

            h1["reason"]

        )




        # ====================================================
        # 15M 权重 30%
        # ====================================================


        score += int(

            m15["score"]

            *

            0.3

        )


        reasons.extend(

            m15["reason"]

        )





        # ====================================================
        # 5M 权重 20%
        # ====================================================


        score += int(

            m5["score"]

            *

            0.2

        )


        reasons.extend(

            m5["reason"]

        )






        score = max(

            -100,

            min(

                100,

                score

            )

        )





        # ====================================================
        # 大周期趋势
        # ====================================================


        if h1["trend"] == "bullish":


            trend = "bullish"



        elif h1["trend"] == "bearish":


            trend = "bearish"



        else:


            trend = "neutral"






        # ====================================================
        # 市场模式
        # ====================================================


        market_mode = "TREND"



        if (

            h1["trend"]

            ==

            "neutral"

            and

            m15["trend"]

            ==

            "neutral"

        ):


            market_mode = "RANGE"



            warnings.append(

                "高低周期方向不明确"

            )






        # ====================================================
        # 回调识别
        # ====================================================


        if (

            h1["trend"]

            ==

            "bearish"

            and

            m15["trend"]

            ==

            "bullish"

        ):


            trend = "bearish_pullback"



            reasons.append(

                "空头趋势中的15M反弹"

            )





        elif (

            h1["trend"]

            ==

            "bullish"

            and

            m15["trend"]

            ==

            "bearish"

        ):


            trend = "bullish_pullback"



            reasons.append(

                "多头趋势中的15M回调"

            )






        # ====================================================
        # 入场信号
        # ====================================================


        entry_signal = "WAIT"




        if (

            trend in [

                "bearish",

                "bearish_pullback"

            ]

            and

            m5["trend"]

            ==

            "bearish"

        ):


            entry_signal = "SHORT_READY"


            reasons.append(

                "5M空头确认"

            )






        elif (

            trend in [

                "bullish",

                "bullish_pullback"

            ]

            and

            m5["trend"]

            ==

            "bullish"

        ):


            entry_signal = "LONG_READY"


            reasons.append(

                "5M多头确认"

            )







        confidence = abs(score)



        confidence = min(

            confidence,

            100

        )





        return {


            "trend":

                trend,


            "market_mode":

                market_mode,


            "entry_signal":

                entry_signal,


            "score":

                score,


            "confidence":

                confidence,


            "reason":

                reasons,


            "warning":

                warnings,

            "higher_trend":
                h1.get("trend", "neutral"),

            "mid_trend":
                m15.get("trend", "neutral"),

            "lower_trend":
                m5.get("trend", "neutral"),

            "mtf_score":
                score,

            "mtf_alignment":
                self.get_alignment(h1, m15, m5),

            "timeframes":

            {

                "1H":

                    h1,


                "15M":

                    m15,


                "5M":

                    m5

            }

        }





# ============================================================
# 单例
# ============================================================


mtf_analyzer = MultiTimeframeAnalyzer()