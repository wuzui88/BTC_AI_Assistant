class BTCStrategy:

    def generate(
        self,
        price,
        indicators,
        market_analysis
    ):

        result = {
            "direction": "NONE",
            "action": "WAIT",
            "entry": None,
            "stop_loss": None,
            "take_profit": None,
            "risk_reward": None,
            "confidence": 0,
            "reason": []
        }


        # =====================
        # 数据保护
        # =====================

        if price is None:
            return result


        if indicators is None:
            indicators = {}


        if market_analysis is None:
            return result



        signal = market_analysis.get(
            "signal",
            "WAIT"
        )

        trend = market_analysis.get(
            "trend",
            "neutral"
        )

        score = market_analysis.get(
            "score",
            0
        )

        market_mode = market_analysis.get(
            "market_mode",
            "TREND"
        )



        ema20 = indicators.get("EMA20")

        ema50 = indicators.get("EMA50")

        rsi = indicators.get("RSI")

        macd = indicators.get("MACD")

        atr = indicators.get("ATR")

        vwap = indicators.get("VWAP")

        volume_ratio = indicators.get(
            "VOLUME_RATIO"
        )



        if atr is None or atr <= 0:

            return result



        # =====================
        # V10.1.7 智能风控过滤
        # =====================


        # 极端RSI保护
        # 防止：
        # RSI 16 BUY
        # RSI 85 SELL


        if rsi is not None:


            if (
                signal in [
                    "BUY",
                    "WAIT_LONG",
                    "WAIT_REVERSAL_LONG"
                ]
                and
                rsi < 22
            ):

                result["reason"].append(
                    "RSI极端超卖，等待企稳"
                )

                result["action"] = (
                    "WAIT_REVERSAL"
                )

                return result



            if (
                signal in [
                    "SELL",
                    "WAIT_SHORT",
                    "WAIT_REVERSAL_SHORT"
                ]
                and
                rsi > 78
            ):

                result["reason"].append(
                    "RSI极端超买，等待回落"
                )

                result["action"] = (
                    "WAIT_REVERSAL"
                )

                return result




        # =====================
        # VWAP过滤
        # =====================


        if vwap:


            distance = abs(
                price - vwap
            ) / vwap



            if distance > 0.025:


                result["reason"].append(
                    "价格严重偏离VWAP"
                )

                return result



            elif distance > 0.012:


                score -= 10

                result["reason"].append(
                    "VWAP偏离降低评分"
                )




        # =====================
        # 成交量保护
        # =====================


        if volume_ratio is not None:


            if volume_ratio < 0.4:


                result["reason"].append(
                    "成交量不足"
                )

                return result



            elif volume_ratio < 0.8:


                score -= 10





        # =====================
        # V10.1.9 WAIT_CONFIRM强化过滤
        # =====================

        if signal in [
            "WAIT_LONG",
            "WAIT_SHORT"
        ]:

            if volume_ratio is not None and volume_ratio < 0.8:

                result["reason"].append(
                    "等待确认：成交量不足"
                )

                result["confidence"] = score

                return result


            if rsi is not None:

                if signal == "WAIT_LONG" and rsi > 62:

                    result["reason"].append(
                        "等待确认：多头RSI偏高"
                    )

                    result["confidence"] = score

                    return result


                if signal == "WAIT_SHORT" and rsi < 38:

                    result["reason"].append(
                        "等待确认：空头RSI偏低"
                    )

                    result["confidence"] = score

                    return result


        # =====================
        # WAIT信号处理
        # =====================


        if signal in [
            "WAIT",
            "WAIT_LONG",
            "WAIT_SHORT"
        ]:


            result["confidence"] = score


            result["action"] = (
                "WAIT_CONFIRM"
            )


            result["reason"].append(
                "等待方向确认"
            )


            # 注意：
            # WAIT_LONG不直接过滤
            # 后续继续判断


        # =====================
        # EMA距离保护
        # =====================


        if ema20:


            deviation = (
                price - ema20
            ) / ema20



            # 多头追涨保护

            if (
                deviation > 0.015
                and
                signal in [
                    "BUY",
                    "WAIT_LONG"
                ]
            ):


                result["reason"].append(
                    "价格远离EMA20，禁止追多"
                )

                return result



            # 空头追杀保护

            if (
                deviation < -0.015
                and
                signal in [
                    "SELL",
                    "WAIT_SHORT"
                ]
            ):


                result["reason"].append(
                    "价格远离EMA20，禁止追空"
                )

                return result

                # =====================
        # BUY 多单核心逻辑
        # =====================

        if signal == "BUY":

            if trend != "bullish":

                result["reason"].append(
                    "趋势未确认"
                )

                return result


            confidence = 0


            # 趋势评分

            if score >= 70:

                confidence += 35


            # EMA趋势

            if (
                ema20
                and
                ema50
                and
                ema20 > ema50
            ):

                confidence += 25


            # MACD

            if macd is not None and macd > 0:

                confidence += 20


            # RSI正常区间

            if (
                rsi is not None
                and
                40 <= rsi <= 68
            ):

                confidence += 15


            # 成交量确认

            if (
                volume_ratio is not None
                and
                volume_ratio >= 1
            ):

                confidence += 5



            if confidence < 75:


                result["reason"].append(
                    "多头确认不足"
                )

                result["confidence"] = confidence

                return result



            stop_loss = (

                price

                -

                atr * 1.8

            )


            take_profit = (

                price

                +

                atr * 3.5

            )



            result.update({

                "direction":
                    "LONG",

                "action":
                    "ENTER",

                "entry":
                    round(price,2),

                "stop_loss":
                    round(stop_loss,2),

                "take_profit":
                    round(take_profit,2),

                "risk_reward":
                    2.0,

                "confidence":
                    confidence,

                "reason":
                    [
                        "趋势多头确认",
                        "EMA多头",
                        "MACD多头",
                        "允许做多"
                    ]

            })





        # =====================
        # SELL 空单核心逻辑
        # =====================

        elif signal == "SELL":


            if trend != "bearish":


                result["reason"].append(
                    "空头趋势未确认"
                )


                return result



            confidence = 0



            if score <= -70:

                confidence += 35



            if (
                ema20
                and
                ema50
                and
                ema20 < ema50
            ):

                confidence +=25



            if macd is not None and macd < 0:

                confidence +=20



            if (
                rsi is not None
                and
                32 <= rsi <= 60
            ):

                confidence +=15



            if (
                volume_ratio is not None
                and
                volume_ratio >=1
            ):

                confidence +=5





            if confidence <75:


                result["reason"].append(
                    "空头确认不足"
                )

                result["confidence"] = confidence

                return result





            stop_loss = (

                price

                +

                atr * 1.8

            )


            take_profit = (

                price

                -

                atr * 3.5

            )



            result.update({

                "direction":
                    "SHORT",

                "action":
                    "ENTER",

                "entry":
                    round(price,2),

                "stop_loss":
                    round(stop_loss,2),

                "take_profit":
                    round(take_profit,2),

                "risk_reward":
                    2.0,

                "confidence":
                    confidence,

                "reason":
                    [
                        "趋势空头确认",
                        "EMA空头",
                        "MACD空头",
                        "允许做空"
                    ]

            })





        # =====================
        # WAIT_LONG 回踩做多
        # =====================

        elif signal == "WAIT_LONG":


            confidence = 0



            # 必须保持EMA结构

            if (
                ema20
                and
                price < ema20
            ):

                result["reason"].append(
                    "价格跌破EMA20，等待恢复"
                )

                return result





            if score >=25:

                confidence +=35



            if (
                ema20
                and
                ema50
                and
                ema20 > ema50
            ):

                confidence +=25



            if macd is not None and macd >0:

                confidence +=20



            if (
                rsi is not None
                and
                45 <= rsi <=60
            ):

                confidence +=15




            if confidence >=85:


                result.update({

                    "direction":
                        "LONG",

                    "action":
                        "ENTER",

                    "entry":
                        round(price,2),

                    "stop_loss":
                        round(
                            price-atr*1.8,
                            2
                        ),

                    "take_profit":
                        round(
                            price+atr*3.2,
                            2
                        ),

                    "risk_reward":
                        1.8,

                    "confidence":
                        confidence,

                    "reason":
                        [
                            "趋势初期多头",
                            "回踩确认",
                            "允许做多"
                        ]

                })


            else:


                result.update({

                    "direction":
                        "NONE",

                    "action":
                        "WAIT_PULLBACK",

                    "confidence":
                        confidence,

                    "reason":
                        [
                            "趋势偏多",
                            "等待回踩"
                        ]

                })

                # =====================
        # WAIT_SHORT
        # 趋势初期空头
        # =====================

        elif signal == "WAIT_SHORT":

            confidence = 0


            if ema20 and price > ema20:

                result["reason"].append(
                    "价格站上EMA20，空头无效"
                )

                return result



            if score <= -25:

                confidence += 35



            if ema20 and ema50 and ema20 < ema50:

                confidence += 25



            if macd is not None and macd < 0:

                confidence += 20



            if rsi is not None and 35 <= rsi <= 60:

                confidence += 15




            if confidence >= 75:


                result.update({

                    "direction":
                        "SHORT",


                    "action":
                        "ENTER",


                    "entry":
                        round(price,2),


                    "stop_loss":
                        round(
                            price + atr * 1.8,
                            2
                        ),


                    "take_profit":
                        round(
                            price - atr * 3.2,
                            2
                        ),


                    "risk_reward":
                        1.8,


                    "confidence":
                        confidence,


                    "reason":
                        [
                            "趋势初期空头",
                            "反弹确认",
                            "允许做空"
                        ]

                })


            else:


                result.update({

                    "direction":
                        "NONE",


                    "action":
                        "WAIT_REBOUND",


                    "confidence":
                        confidence,


                    "reason":
                        [
                            "趋势偏空",
                            "等待反弹"
                        ]

                })





        # =====================
        # WAIT_REVERSAL_LONG
        # 震荡/趋势反转多
        # =====================


        elif signal == "WAIT_REVERSAL_LONG":


            confidence = 0



            if market_mode == "RANGE":

                confidence += 25



            if rsi is not None and rsi < 35:

                confidence += 30



            if macd is not None and macd > -10:

                confidence += 20



            if ema20 and price <= ema20:

                confidence += 15



            if atr:

                confidence += 10




            if confidence >= 60:


                result.update({

                    "direction":
                        "LONG",


                    "action":
                        "ENTER",


                    "entry":
                        round(price,2),


                    "stop_loss":
                        round(
                            price - atr * 1.5,
                            2
                        ),


                    "take_profit":
                        round(
                            price + atr * 2.5,
                            2
                        ),


                    "risk_reward":
                        1.7,


                    "confidence":
                        confidence,


                    "position_ratio":
                        0.5,


                    "reason":
                        [
                            "反转多头机会",
                            "超卖修复",
                            "允许做多"
                        ]

                })




        # =====================
        # WAIT_REVERSAL_SHORT
        # 震荡/趋势反转空
        # =====================


        elif signal == "WAIT_REVERSAL_SHORT":


            confidence = 0




            if market_mode == "RANGE":

                confidence += 25



            if rsi is not None and rsi > 65:

                confidence += 30



            if macd is not None and macd < 10:

                confidence += 20



            if ema20 and price >= ema20:

                confidence += 15



            if atr:

                confidence += 10




            if confidence >= 60:


                result.update({

                    "direction":
                        "SHORT",


                    "action":
                        "ENTER",


                    "entry":
                        round(price,2),


                    "stop_loss":
                        round(
                            price + atr * 1.5,
                            2
                        ),


                    "take_profit":
                        round(
                            price - atr * 2.5,
                            2
                        ),


                    "risk_reward":
                        1.7,


                    "confidence":
                        confidence,


                    "position_ratio":
                        0.5,


                    "reason":
                        [
                            "反转空头机会",
                            "超买回落",
                            "允许做空"
                        ]

                })





        # =====================
        # 其他情况
        # =====================


        else:


            result.update({

                "confidence":
                    score,


                "reason":
                    [
                        "交易信号不足"
                    ]

            })




        return result

        