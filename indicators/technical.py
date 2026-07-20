class TechnicalIndicator:


    def calculate(self, candles):


        result = {

            "EMA20": None,
            "EMA50": None,
            "RSI": None,
            "MACD": None,
            "ATR": None

        }



        # 数据保护

        if candles is None or len(candles) < 2:

            return result



        closes = []

        highs = []

        lows = []



        for c in candles:


            try:

                closes.append(
                    float(c["close"])
                )

                highs.append(
                    float(c["high"])
                )

                lows.append(
                    float(c["low"])
                )


            except:

                continue



        if len(closes) < 2:

            return result



        # EMA

        result["EMA20"] = self.ema(
            closes,
            20
        )


        result["EMA50"] = self.ema(
            closes,
            50
        )



        # RSI

        result["RSI"] = self.rsi(
            closes,
            14
        )



        # MACD

        ema12 = self.ema(
            closes,
            12
        )

        ema26 = self.ema(
            closes,
            26
        )


        if (
            ema12 is not None
            and
            ema26 is not None
        ):

            result["MACD"] = round(
                ema12 - ema26,
                2
            )



        # ATR

        result["ATR"] = self.atr(
            highs,
            lows,
            closes,
            14
        )


        return result






    # =====================
    # EMA
    # =====================

    def ema(
        self,
        data,
        period
    ):


        if len(data) < period:

            return None



        ema = sum(
            data[:period]
        ) / period



        k = 2 / (period + 1)



        for price in data[period:]:


            ema = (

                price * k

                +

                ema * (1-k)

            )



        return round(
            ema,
            2
        )







    # =====================
    # RSI
    # =====================

    def rsi(
        self,
        closes,
        period
    ):


        if len(closes) <= period:

            return None



        gains = 0

        losses = 0



        for i in range(
            1,
            period + 1
        ):


            diff = (
                closes[i]
                -
                closes[i-1]
            )


            if diff >= 0:

                gains += diff

            else:

                losses -= diff



        if losses == 0:

            return 100



        rs = gains / losses



        return round(

            100 -

            (
                100 /
                (1 + rs)
            ),

            2

        )







    # =====================
    # ATR
    # =====================

    def atr(
        self,
        highs,
        lows,
        closes,
        period
    ):


        if len(closes) <= period:

            return None



        trs = []



        for i in range(
            1,
            len(closes)
        ):


            tr = max(

                highs[i]
                -
                lows[i],


                abs(
                    highs[i]
                    -
                    closes[i-1]
                ),


                abs(
                    lows[i]
                    -
                    closes[i-1]
                )

            )


            trs.append(tr)



        if len(trs) < period:

            return None



        atr = sum(
            trs[-period:]
        ) / period



        return round(
            atr,
            2
        )