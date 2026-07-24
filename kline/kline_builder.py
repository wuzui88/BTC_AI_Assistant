from .candle import Candle



class KlineBuilder:



    def __init__(
            self,
            interval=300
    ):


        self.interval = interval

        self.current = None

        self.history = []





    def update(
            self,
            tick
    ):



        price = float(
            tick["price"]
        )



        # ====================================================
        # 成交量
        #
        # V10.3.7
        #
        # 统一:
        #
        # volume = BTC数量
        #
        # 不再直接读取 size
        #
        # ====================================================


        volume = float(

            tick.get(

                "volume",

                0

            )

        )

        print(
            "DEBUG KlineBuilder收到:",
            tick
        )



        ts = int(
            tick["time"]
        )




        candle_time = (

            ts // self.interval

        ) * self.interval





        # ====================================================
        # 第一根K线
        # ====================================================


        if self.current is None:



            self.current = Candle(

                candle_time,

                price,

                volume

            )





        # ====================================================
        # 同周期更新
        # ====================================================


        elif candle_time == self.current.timestamp:



            self.current.update(

                price,

                volume

            )





        # ====================================================
        # 新周期
        # ====================================================


        else:



            finished = self.current.to_dict()



            self.history.append(

                finished

            )



            print(

                "生成K线:",

                finished

            )



            self.current = Candle(

                candle_time,

                price,

                volume

            )







    def get_history(
            self
    ):


        return self.history





    def get_latest(
            self
    ):



        if self.current:


            return self.current.to_dict()



        return None