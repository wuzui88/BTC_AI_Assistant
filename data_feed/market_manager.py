class MarketManager:


    def __init__(self):

        self.okx_price = None

        self.binance_price = None



    def update(self, data):


        exchange = data["exchange"]

        price = data["price"]



        if exchange == "OKX":

            self.okx_price = price



        elif exchange == "BINANCE":

            self.binance_price = price



        self.show()



    def show(self):


        if self.okx_price and self.binance_price:


            diff = (
                self.binance_price
                -
                self.okx_price
            )


            print(
                "\n================"
            )

            print(
                "OKX:",
                self.okx_price
            )


            print(
                "BINANCE:",
                self.binance_price
            )


            print(
                "价差:",
                round(diff,2)
            )

            print(
                "================\n"
            )