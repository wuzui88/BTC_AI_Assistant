class Candle:


    def __init__(
            self,
            timestamp,
            price,
            volume=0
    ):


        self.timestamp = timestamp


        # ====================================================
        # OHLC
        # ====================================================

        price = float(price)

        self.open = price
        self.high = price
        self.low = price
        self.close = price



        # ====================================================
        # 成交量
        #
        # V10.3.7
        #
        # 统一标准:
        #
        # volume = BTC数量
        #
        # 禁止:
        # contract 张数
        #
        # ====================================================


        self.volume = float(volume)

        self.volume_unit = "BTC"




    # ====================================================
    # 更新K线
    # ====================================================


    def update(
            self,
            price,
            volume=0
    ):


        price = float(price)

        volume = float(volume)



        # ====================================================
        # 更新收盘价
        # ====================================================

        self.close = price



        # ====================================================
        # 更新最高价
        # ====================================================

        if price > self.high:

            self.high = price



        # ====================================================
        # 更新最低价
        # ====================================================

        if price < self.low:

            self.low = price



        # ====================================================
        # 累计成交量
        #
        # 注意:
        # 这里要求传入已经转换后的 BTC volume
        #
        # ====================================================

        self.volume += volume





    # ====================================================
    # 转换字典
    # ====================================================


    def to_dict(self):


        return {


            "time":

                self.timestamp,


            "open":

                self.open,


            "high":

                self.high,


            "low":

                self.low,


            "close":

                self.close,


            # 成交量(BTC)

            "volume":

                self.volume,


            "volume_unit":

                self.volume_unit

        }