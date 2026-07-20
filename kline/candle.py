class Candle:


    def __init__(
        self,
        timestamp,
        price
    ):

        self.timestamp = timestamp

        self.open = price
        self.high = price
        self.low = price
        self.close = price

        self.volume = 0



    def update(
        self,
        price
    ):

        self.close = price

        if price > self.high:
            self.high = price


        if price < self.low:
            self.low = price



    def to_dict(self):

        return {

            "time":self.timestamp,

            "open":self.open,

            "high":self.high,

            "low":self.low,

            "close":self.close

        }