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


        # 成交量
        volume = float(
            tick.get(
                "size",
                0
            )
        )


        ts = int(
            tick["time"]
        )



        candle_time = (

            ts // self.interval

        ) * self.interval



        # 第一根K线

        if self.current is None:


            self.current = Candle(

                candle_time,

                price,

                volume

            )


        # 同一个周期

        elif candle_time == self.current.timestamp:


            self.current.update(

                price,

                volume

            )


        # 新周期

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