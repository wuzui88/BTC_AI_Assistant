class TechnicalIndicator:


    def calculate(
        self,
        candles
    ):


        result = {


            "EMA20": None,

            "EMA50": None,

            "RSI": None,

            "MACD": None,

            "ATR": None,


            # V10 新增

            "VWAP": None,

            "VOLUME_RATIO": None,

            "ATR_PERCENT": None

        }




        if (
            candles is None
            or
            len(candles) < 2
        ):

            return result





        closes = []

        highs = []

        lows = []

        volumes = []





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


                volumes.append(

                    float(
                        c.get(
                            "volume",
                            0
                        )
                    )

                )



            except:


                continue






        if len(closes) < 2:

            return result





        # =====================
        # EMA
        # =====================


        result["EMA20"] = self.ema(

            closes,

            20

        )



        result["EMA50"] = self.ema(

            closes,

            50

        )







        # =====================
        # RSI
        # =====================


        result["RSI"] = self.rsi(

            closes,

            14

        )








        # =====================
        # MACD
        # =====================


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








        # =====================
        # ATR
        # =====================


        result["ATR"] = self.atr(

            highs,

            lows,

            closes,

            14

        )







        # =====================
        # VWAP
        # =====================


        result["VWAP"] = self.vwap(

            candles

        )







        # =====================
        # Volume Ratio
        # =====================


        result["VOLUME_RATIO"] = self.volume_ratio(

            volumes,

            20

        )







        # =====================
        # ATR Percent
        # =====================


        if (

            result["ATR"]

            and

            closes[-1] > 0

        ):


            result["ATR_PERCENT"] = round(

                result["ATR"]

                /

                closes[-1],

                6

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





        k = 2 / (

            period + 1

        )





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









    # =====================
    # VWAP
    # =====================


    def vwap(

        self,

        candles

    ):



        total_volume = 0

        total_value = 0





        for c in candles:



            try:



                volume = float(

                    c.get(

                        "volume",

                        0

                    )

                )



                price = (

                    float(c["high"])

                    +

                    float(c["low"])

                    +

                    float(c["close"])

                ) / 3





                total_volume += volume


                total_value += (

                    price

                    *

                    volume

                )




            except:


                continue






        if total_volume == 0:

            return None





        return round(

            total_value

            /

            total_volume,

            2

        )









    # =====================
    # Volume Ratio
    # =====================


    def volume_ratio(
        self,
        volumes,
        period
    ):


        if len(volumes) < period + 2:

            return None



        # 使用已经完成K线
        current = volumes[-2]



        avg = sum(
            volumes[-period-2:-2]
        ) / period



        if avg == 0:

            return None



        return round(
            current / avg,
            2
        )