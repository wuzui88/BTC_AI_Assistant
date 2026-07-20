import time



class CandleBuilder:


    def __init__(self):


        # 当前正在形成的K线

        self.current = None


        # 5分钟

        self.interval = 300000




    def update(
            self,
            price,
            timestamp=None,
            volume=0
    ):


        try:

            price = float(price)

            volume = float(volume)


        except:

            return None



        if price <= 0:

            return None



        if timestamp is None:

            timestamp = int(
                time.time() * 1000
            )



        candle_time = (

            timestamp // self.interval

        ) * self.interval




        # =========================
        # 第一根K线
        # =========================

        if self.current is None:


            self.current = {


                "time":

                    candle_time,


                "open":

                    price,


                "high":

                    price,


                "low":

                    price,


                "close":

                    price,


                "volume":

                    volume

            }


            return None





        # =========================
        # 时间异常保护
        # =========================

        if candle_time < self.current["time"]:


            return None






        # =========================
        # 同一个5分钟
        # =========================

        if candle_time == self.current["time"]:



            self.current["high"] = max(

                self.current["high"],

                price

            )



            self.current["low"] = min(

                self.current["low"],

                price

            )



            self.current["close"] = price



            # 累计成交量

            self.current["volume"] += volume



            return None







        # =========================
        # 新5分钟
        # =========================


        finished = self.current.copy()



        self.current = {


            "time":

                candle_time,


            "open":

                price,


            "high":

                price,


            "low":

                price,


            "close":

                price,


            "volume":

                volume

        }




        return finished