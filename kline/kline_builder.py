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

        price = tick["price"]

        ts = tick["time"]


        candle_time = (
            ts // self.interval
        ) * self.interval



        if self.current is None:

            self.current = Candle(
                candle_time,
                price
            )


        elif candle_time == self.current.timestamp:

            self.current.update(
                price
            )


        else:

            self.history.append(
                self.current.to_dict()
            )


            print(
                "生成K线:",
                self.current.to_dict()
            )


            self.current = Candle(
                candle_time,
                price
            )