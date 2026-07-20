# market.py


class MarketManager:


    def __init__(self, okx, binance):

        self.okx = okx
        self.binance = binance



    def get_price(self):


        # 主行情 OKX

        if self.okx.price:

            return {

                "price":
                self.okx.price,

                "source":
                "OKX"

            }



        # 备用 Binance

        if self.binance.price:

            return {

                "price":
                self.binance.price,

                "source":
                "Binance"

            }



        return None