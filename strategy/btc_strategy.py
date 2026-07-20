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
            "signal"
        )


        trend = market_analysis.get(
            "trend"
        )


        score = market_analysis.get(
            "score",
            0
        )


        market_mode = market_analysis.get(
            "market_mode",
            "TREND"
        )



        ema20 = indicators.get(
            "EMA20"
        )


        ema50 = indicators.get(
            "EMA50"
        )


        atr = indicators.get(
            "ATR"
        )



        rsi = indicators.get(
            "RSI"
        )



        macd = indicators.get(
            "MACD"
        )



        if atr is None or atr <= 0:

            return result




        # =====================
        # 价格距离EMA过滤
        # 防止追高
        # =====================


        if ema20:


            deviation = (

                price - ema20

            ) / ema20



            # 高于EMA20超过1.2%
            # 不追多

            if deviation > 0.012:


                result["reason"].append(

                    "价格偏离EMA20过高"

                )


                return result



        # =====================
        # 多单
        # =====================


        if signal == "BUY":



            # 趋势保护

            if trend != "bullish":


                result["reason"].append(

                    "趋势未确认"

                )


                return result



            confidence = 0



            if score >= 70:

                confidence += 40



            if ema20 and ema50 and ema20 > ema50:

                confidence += 25



            if macd and macd > 0:

                confidence += 20



            if rsi and 45 <= rsi <= 65:

                confidence +=15



            # 必须达到置信度

            if confidence < 70:


                result["reason"].append(

                    "多头置信度不足"

                )


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

                    round(
                        price,
                        2
                    ),



                "stop_loss":

                    round(
                        stop_loss,
                        2
                    ),



                "take_profit":

                    round(
                        take_profit,
                        2
                    ),



                "risk_reward":

                    1.9,



                "confidence":

                    confidence,



                "reason":

                    [

                        "EMA多头确认",

                        "MACD多头确认",

                        "趋势评分满足",

                        "允许做多"

                    ]

            })
        
        # =====================
        # 空单
        # =====================


        elif signal == "SELL":



            if trend != "bearish":


                result["reason"].append(

                    "空头趋势未确认"

                )


                return result



            confidence = 0



            if score <= -70:

                confidence += 40



            if ema20 and ema50 and ema20 < ema50:

                confidence +=25



            if macd and macd < 0:

                confidence +=20



            if rsi and 35 <= rsi <=55:

                confidence +=15



            if confidence <70:


                result["reason"].append(

                    "空头置信度不足"

                )


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

                    round(
                        price,
                        2
                    ),



                "stop_loss":

                    round(
                        stop_loss,
                        2
                    ),



                "take_profit":

                    round(
                        take_profit,
                        2
                    ),



                "risk_reward":

                    1.9,



                "confidence":

                    confidence,



                "reason":

                    [

                        "EMA空头确认",

                        "MACD空头确认",

                        "趋势评分满足",

                        "允许做空"

                    ]

            })






        # =====================
        # 等待回调做多
        # =====================


        elif signal == "WAIT_LONG":


            # 趋势初期多头：允许回踩确认后直接执行

            confidence = 0

            # 趋势初期多头增加确认：价格不能跌破EMA20
            if ema20 and price < ema20:
                result["reason"].append(
                    "价格弱于EMA20，等待多头确认"
                )
                return result


            if score >= 25:
                confidence += 35


            if ema20 and ema50 and ema20 > ema50:
                confidence += 25


            if macd is not None and macd > 0:
                confidence += 20


            if rsi is not None and 40 <= rsi <= 65:
                confidence += 15



            if confidence >= 75:


                result.update({

                    "direction":
                        "LONG",

                    "action":
                        "ENTER",

                    "entry":
                        round(price,2),

                    "stop_loss":
                        round(price - atr * 1.8,2),

                    "take_profit":
                        round(price + atr * 3.2,2),

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
                            "等待价格回踩"
                        ]

                })










        # =====================
        # 等待反弹做空
        # =====================


        elif signal == "WAIT_SHORT":


            # 趋势初期空头：允许反弹确认后直接执行

            confidence = 0

            # 趋势初期空头增加确认：价格不能站上EMA20
            if ema20 and price > ema20:
                result["reason"].append(
                    "价格站上EMA20，等待空头确认"
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
                        round(price + atr * 1.8,2),

                    "take_profit":
                        round(price - atr * 3.2,2),

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
        # 震荡超卖反弹做多
        # =====================


        elif signal == "WAIT_REVERSAL_LONG":


            confidence = 0


            if market_mode == "RANGE":
                confidence += 30


            if rsi is not None and rsi < 35:
                confidence += 30


            if macd is not None and macd > -10:
                confidence += 20


            if ema20 and price <= ema20:
                confidence += 15



            if confidence >= 60:


                result.update({


                    "direction":
                        "LONG",


                    "action":
                        "ENTER",


                    "entry":
                        round(price,2),


                    "stop_loss":
                        round(price - atr * 1.5,2),


                    "take_profit":
                        round(price + atr * 2.5,2),


                    "risk_reward":
                        1.7,


                    "confidence":
                        confidence,


                    "reason":
                        [
                            "震荡超卖反弹",
                            "允许做多"
                        ]

                })



        # =====================
        # 震荡超买回落做空
        # =====================


        elif signal == "WAIT_REVERSAL_SHORT":


            confidence = 0


            if market_mode == "RANGE":
                confidence += 30


            if rsi is not None and rsi > 65:
                confidence += 30


            if macd is not None and macd < 10:
                confidence += 20


            if ema20 and price >= ema20:
                confidence += 15



            if confidence >= 60:


                result.update({


                    "direction":
                        "SHORT",


                    "action":
                        "ENTER",


                    "entry":
                        round(price,2),


                    "stop_loss":
                        round(price + atr * 1.5,2),


                    "take_profit":
                        round(price - atr * 2.5,2),


                    "risk_reward":
                        1.7,


                    "confidence":
                        confidence,


                    "reason":
                        [
                            "震荡超买回落",
                            "允许做空"
                        ]

                })







        # =====================
        # 反转趋势V6
        # =====================

        elif signal == "WAIT_REVERSAL_LONG":

            confidence = 0

            if macd is not None and macd > 0:
                confidence += 25

            if rsi is not None and rsi >= 50:
                confidence += 20

            if ema20 and price >= ema20:
                confidence += 20

            if atr:
                confidence += 15

            if confidence >= 60:
                result.update({
                    "direction": "LONG",
                    "action": "ENTER",
                    "entry": round(price, 2),
                    "stop_loss": round(price - atr * 1.5, 2),
                    "take_profit": round(price + atr * 2.5, 2),
                    "risk_reward": 1.7,
                    "confidence": confidence,
                    "reason": [
                        "趋势反转多头",
                        "MACD恢复",
                        "允许做多"
                    ],
                    "position_ratio": 0.5
                })


        elif signal == "WAIT_REVERSAL_SHORT":

            confidence = 0

            if macd is not None and macd < 0:
                confidence += 25

            if rsi is not None and rsi <= 50:
                confidence += 20

            if ema20 and price <= ema20:
                confidence += 20

            if atr:
                confidence += 15

            if confidence >= 60:
                result.update({
                    "direction": "SHORT",
                    "action": "ENTER",
                    "entry": round(price, 2),
                    "stop_loss": round(price + atr * 1.5, 2),
                    "take_profit": round(price - atr * 2.5, 2),
                    "risk_reward": 1.7,
                    "confidence": confidence,
                    "reason": [
                        "趋势反转空头",
                        "MACD转弱",
                        "允许做空"
                    ],
                    "position_ratio": 0.5
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

