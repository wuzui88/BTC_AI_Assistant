import json
import websocket
import threading
import time


class BinanceFeed:

    def __init__(self, callback):

        self.callback = callback

        self.url = (
            "wss://fstream.binance.com/stream?"
            "streams=btcusdt@ticker"
        )

        self.running = True


    def on_open(self, ws):

        print("Binance WebSocket连接成功")

        print("Binance URL:", self.url)


    def on_message(self, ws, message):
        print("BINANCE收到原始数据")     
        try:

            print(
                "BINANCE RAW:",
                message[:100]
            )


            data = json.loads(message)


            # stream模式取data
            if "data" in data:

                data = data["data"]


            price = float(
                data["c"]
            )


            market_data = {

                "exchange": "BINANCE",

                "symbol": "BTCUSDT",

                "price": price,

                "time": int(time.time())

            }


            print(
                f"行情 BINANCE {price}"
            )


            self.callback(
                market_data
            )


        except Exception as e:

            print(
                "Binance解析错误:",
                e
            )



    def on_error(self, ws, error):

        print(
            "Binance错误:",
            error
        )



    def on_close(self, ws, *args):

        print(
            "Binance WebSocket关闭"
        )



    def connect(self):

        while self.running:

            try:

                ws = websocket.WebSocketApp(

                    self.url,

                    on_open=self.on_open,

                    on_message=self.on_message,

                    on_error=self.on_error,

                    on_close=self.on_close

                )


                ws.run_forever(

                    ping_interval=20,

                    ping_timeout=10

                )


            except Exception as e:

                print(
                    "Binance连接异常:",
                    e
                )


            print(
                "5秒后重新连接 Binance..."
            )

            time.sleep(5)



    def start(self):

        t = threading.Thread(

            target=self.connect,

            daemon=True

        )

        t.start()