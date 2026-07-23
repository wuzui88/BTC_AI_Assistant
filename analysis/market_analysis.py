# ============================================================
# market_analysis_v10.3.1.py
#
# BTC AI Assistant V10.3
#
# Multi Timeframe Market Analysis
#
# Upgrade:
#
# V10.3.1
#
# 1. 接入 multi_timeframe_analysis
# 2. 支持 1H / 15M / 5M 多周期分析
# 3. 保留 V10.2 接口兼容
# 4. 增加高周期趋势保护
# 5. 增加 MTF 状态输出
#
# ============================================================


from market.multi_timeframe_analysis import (
    mtf_analyzer
)





class MarketAnalysis:



    def __init__(
        self
    ):


        self.name = (

            "MarketAnalysis_V10.3.1"

        )


        self.max_score = 100







    # ========================================================
    # 主入口
    #
    # 兼容旧调用:
    #
    # analyze(
    #     candles,
    #     indicators
    # )
    #
    # 新:
    #
    # analyze(
    #     candles,
    #     indicators,
    #     timeframe_data
    # )
    #
    # ========================================================


    def analyze(
        self,
        candles,
        indicators,
        timeframe_data=None
    ):



        result = {


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

                [],


            "warning":

                [],



            # ===============================
            # V10.3 新增
            # ===============================


            "higher_trend":

                "unknown",


            "mid_trend":

                "unknown",


            "lower_trend":

                "unknown",


            "mtf_score":

                0,


            "entry_signal":

                "WAIT",


            "mtf_alignment":

                "NONE"


        }







        if not candles:



            result["warning"].append(

                "K线数据为空"

            )


            return result







        if not indicators:



            result["warning"].append(

                "指标数据为空"

            )


            return result







        # ====================================================
        # 当前周期数据
        #
        # 默认5分钟
        #
        # ====================================================


        price = float(

            indicators.get(

                "price",

                candles[-1].get(

                    "close",

                    0

                )

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



        macd = float(

            indicators.get(

                "MACD",

                0

            )

        )



        rsi = float(

            indicators.get(

                "RSI",

                50

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
        # V10.3 多周期分析
        #
        # ====================================================


        mtf_result = self.analyze_multi_timeframe(

            timeframe_data

        )



        result.update(

            mtf_result

        )







        # ====================================================
        # 市场模式
        # ====================================================


        if atr_percent < 0.0005:


            result["market_mode"] = "RANGE"


            result["warning"].append(

                "ATR过低，震荡市场"

            )



        else:


            result["market_mode"] = "TREND"







        # ====================================================
        # 单周期基础评分
        # ====================================================


        score_data = self.calculate_score(

            price,

            ema20,

            ema50,

            macd,

            rsi,

            vwap,

            volume_ratio,

            result

        )


        result["score"] = score_data["score"]


        result["reason"].extend(

            score_data["reason"]

        )


        result["warning"].extend(

            score_data["warning"]

        )

                # ====================================================
        # MTF融合评分
        #
        # V10.3.1
        #
        # 权重:
        #
        # 1H  50%
        # 15M 30%
        # 5M  20%
        #
        # ====================================================


        mtf_score = result.get(

            "mtf_score",

            0

        )


        base_score = result["score"]



        final_score = int(

            base_score * 0.7

            +

            mtf_score * 0.3

        )



        final_score = max(

            -100,

            min(

                100,

                final_score

            )

        )



        result["score"] = final_score







        # ====================================================
        # 趋势判断
        #
        # MTF优先
        #
        # ====================================================


        result["trend"] = self.detect_trend(

            final_score,

            result

        )







        # ====================================================
        # MTF方向保护
        #
        # 防止逆大周期交易
        #
        # ====================================================


        mtf_alignment = result.get(

            "mtf_alignment",

            "NONE"

        )



        if mtf_alignment == "BEARISH_PRESSURE":


            if result["score"] > 0:


                result["warning"].append(

                    "高周期空头压制"

                )


                result["signal"] = "WAIT"



                result["entry_signal"] = (

                    "WAIT_LONG"

                )



                return self.finalize(

                    result

                )







        elif mtf_alignment == "BULLISH_PRESSURE":


            if result["score"] < 0:


                result["warning"].append(

                    "高周期多头支撑"

                )


                result["signal"] = "WAIT"



                result["entry_signal"] = (

                    "WAIT_SHORT"

                )


                return self.finalize(

                    result

                )







        # ====================================================
        # 信号生成
        #
        # ====================================================


        if result["trend"] in [

            "bullish",

            "bullish_pullback"

        ]:



            if (

                result["score"] >= 75

                and

                volume_ratio >= 0.8

                and

                rsi > 35

            ):


                result["signal"] = "BUY"


                result["entry_signal"] = (

                    "LONG_READY"

                )


                result["reason"].append(

                    "多周期多头确认"

                )




            elif result["score"] >= 45:


                result["signal"] = "WAIT_LONG"


                result["entry_signal"] = (

                    "WAIT_LONG"

                )


                result["reason"].append(

                    "等待多头确认"

                )







        elif result["trend"] in [

            "bearish",

            "bearish_rebound"

        ]:



            if (

                result["score"] <= -75

                and

                volume_ratio >= 0.8

                and

                rsi < 70

            ):


                result["signal"] = "SELL"


                result["entry_signal"] = (

                    "SHORT_READY"

                )


                result["reason"].append(

                    "多周期空头确认"

                )





            elif result["score"] <= -45:


                result["signal"] = "WAIT_SHORT"


                result["entry_signal"] = (

                    "WAIT_SHORT"

                )


                result["reason"].append(

                    "等待空头确认"

                )







        else:



            result["signal"] = "WAIT"


            result["entry_signal"] = (

                "WAIT"

            )


            result["reason"].append(

                "趋势未确认"

            )







        return self.finalize(

            result

        )











    # ========================================================
    # 多周期分析
    #
    # V10.3.1
    #
    # ========================================================


    def analyze_multi_timeframe(
        self,
        timeframe_data
    ):



        result = {


            "higher_trend":

                "unknown",


            "mid_trend":

                "unknown",


            "lower_trend":

                "unknown",


            "mtf_score":

                0,


            "mtf_alignment":

                "NONE"

        }




        if not timeframe_data:


            return result







        try:


            mtf = mtf_analyzer.analyze(

                timeframe_data

            )


        except Exception:


            return result







        result["higher_trend"] = mtf.get(

            "1H",

            "unknown"

        )



        result["mid_trend"] = mtf.get(

            "15M",

            "unknown"

        )



        result["lower_trend"] = mtf.get(

            "5M",

            "unknown"

        )








        score = 0





        # 1H权重最高


        if result["higher_trend"] == "bullish":


            score += 50



        elif result["higher_trend"] == "bearish":


            score -= 50







        # 15M


        if result["mid_trend"] == "bullish":


            score += 30



        elif result["mid_trend"] == "bearish":


            score -= 30







        # 5M


        if result["lower_trend"] == "bullish":


            score += 20



        elif result["lower_trend"] == "bearish":


            score -= 20







        result["mtf_score"] = score







        # ====================================================
        # 周期一致性
        # ====================================================


        trends = [


            result["higher_trend"],


            result["mid_trend"],


            result["lower_trend"]


        ]






        bullish_count = trends.count(

            "bullish"

        )


        bearish_count = trends.count(

            "bearish"

        )







        if bullish_count >= 2:


            result["mtf_alignment"] = (

                "BULLISH_PRESSURE"

            )



        elif bearish_count >= 2:


            result["mtf_alignment"] = (

                "BEARISH_PRESSURE"

            )



        else:


            result["mtf_alignment"] = (

                "MIXED"

            )


        return result

        # ========================================================
    # 基础技术评分
    #
    # V10.3.1
    #
    # ========================================================


    def calculate_score(
        self,
        price,
        ema20,
        ema50,
        macd,
        rsi,
        vwap,
        volume_ratio,
        result
    ):



        score = 0


        reason = []


        warning = []





        # ====================================================
        # EMA趋势
        # ====================================================


        if ema20 and ema50:



            if ema20 > ema50:


                score += 30


                reason.append(

                    "EMA多头排列"

                )



            elif ema20 < ema50:


                score -= 30


                reason.append(

                    "EMA空头排列"

                )



            else:


                warning.append(

                    "EMA趋势不足"

                )







        # ====================================================
        # MACD
        # ====================================================


        if macd > 0:


            score += 20


            reason.append(

                "MACD多头确认"

            )



        elif macd < 0:


            score -= 20


            reason.append(

                "MACD空头确认"

            )







        # ====================================================
        # RSI
        # ====================================================


        if rsi < 35:


            score -= 5


            reason.append(

                "RSI偏弱"

            )



        elif rsi > 65:


            score += 5


            reason.append(

                "RSI偏强"

            )



        else:


            reason.append(

                "RSI中性"

            )







        # ====================================================
        # VWAP
        # ====================================================


        if vwap and price:



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







        # ====================================================
        # 成交量
        # ====================================================


        if volume_ratio >= 1:


            score += 10


            reason.append(

                "成交量正常"

            )



        elif volume_ratio < 0.5:


            score -= 10


            warning.append(

                "成交量不足"

            )



        else:


            warning.append(

                "成交量一般"

            )







        return {


            "score":

                score,


            "reason":

                reason,


            "warning":

                warning

        }









    # ========================================================
    # 趋势识别
    #
    # ========================================================


    def detect_trend(
        self,
        score,
        result
    ):



        higher = result.get(

            "higher_trend",

            "unknown"

        )


        mid = result.get(

            "mid_trend",

            "unknown"

        )


        lower = result.get(

            "lower_trend",

            "unknown"

        )






        # ====================================================
        # 高周期优先
        # ====================================================


        if higher == "bearish":



            if lower == "bullish":


                return (

                    "bearish_rebound"

                )



            return (

                "bearish"

            )







        if higher == "bullish":



            if lower == "bearish":


                return (

                    "bullish_pullback"

                )



            return (

                "bullish"

            )







        # ====================================================
        # 没有MTF时兼容旧逻辑
        # ====================================================


        if score >= 40:


            return "bullish"




        elif score <= -40:


            return "bearish"




        return "neutral"









    # ========================================================
    # 最终整理输出
    #
    # ========================================================


    def finalize(
        self,
        result
    ):



        score = result.get(

            "score",

            0

        )





        # confidence

        confidence = abs(

            score

        )



        confidence = min(

            confidence,

            100

        )



        result["confidence"] = confidence







        # ====================================================
        # 信号安全限制
        # ====================================================


        if result["signal"] == "BUY":



            if confidence < 60:


                result["signal"] = "WAIT"


                result["entry_signal"] = (

                    "WAIT"

                )


                result["reason"].append(

                    "信心不足"

                )







        elif result["signal"] == "SELL":



            if confidence < 60:


                result["signal"] = "WAIT"


                result["entry_signal"] = (

                    "WAIT"

                )


                result["reason"].append(

                    "信心不足"

                )







        return result











# ============================================================
# 单例
# ============================================================


market_analysis = MarketAnalysis()





# ============================================================
# 文件结束
#
# BTC AI Assistant V10.3.1
#
# ============================================================

