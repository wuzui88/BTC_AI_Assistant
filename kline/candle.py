class Candle:


    def __init__(
            self,
            timestamp,
            price,
            volume=0
    ):


        self.timestamp = timestamp


        # OHLC
        self.open = price
        self.high = price
        self.low = price
        self.close = price


        # 成交量
        self.volume = float(volume)



    def update(
            self,
            price,
            volume=0
    ):


        price = float(price)
        volume = float(volume)


        # 更新收盘价
        self.close = price


        # 更新最高价
        if price > self.high:

            self.high = price


        # 更新最低价
        if price < self.low:

            self.low = price


        # 累计成交量
        self.volume += volume



    def to_dict(self):


        return {

            "time": self.timestamp,

            "open": self.open,

            "high": self.high,

            "low": self.low,

            "close": self.close,

            "volume": self.volume

        }