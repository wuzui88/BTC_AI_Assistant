# okx_ws.py

import websocket
import json
import threading
import time


class OKXFeed:

    def __init__(self):

        self.price = None
        self.bid = None
        self.ask = None

        self.high24h = None
        self.low24h = None
        self.volume24h = None

        self.connected = False


    # WebSocket连接成功

    def on_open(self, ws):

        print("OKX WebSocket连接成功")


        self.connected = True


        subscribe = {

            "op": "subscribe",

            "args": [

                {

                    "channel": "tickers",

                    "instId": "BTC-USDT-SWAP"

                }

            ]

        }


        ws.send(
            json.dumps(subscribe)
        )


        print("OKX订阅 BTC-USDT-SWAP 成功")



    # 接收行情

    def on_message(self, ws, message):

        try:


            # 如果是bytes，转字符串

            if isinstance(message, bytes):

                message = message.decode(
                    "utf-8"
                )


            data = json.loads(message)



            # 忽略订阅确认

            if "data" not in data:

                return



            ticker = data["data"][0]



            self.price = float(
                ticker["last"]
            )


            self.bid = float(
                ticker["bidPx"]
            )


            self.ask = float(
                ticker["askPx"]
            )


            self.high24h = float(
                ticker["high24h"]
            )


            self.low24h = float(
                ticker["low24h"]
            )


            self.volume24h = float(
                ticker["vol24h"]
            )



            print(
                f"OKX BTC: {self.price}"
            )



        except Exception as e:

            print(
                "OKX数据解析错误:",
                e
            )



    # 错误

    def on_error(self, ws, error):

        print(
            "OKX错误:",
            error
        )



    # 关闭

    def on_close(self, ws, close_status_code, close_msg):

        self.connected = False


        print(
            "OKX连接关闭"
        )



    # 启动

    def start(self):


        url = (
            "wss://ws.okx.com:443/"
            "ws/v5/public"
        )


        def run():


            while True:


                try:


                    ws = websocket.WebSocketApp(

                        url,

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
                        "OKX连接异常:",
                        e
                    )



                print(
                    "5秒后重新连接OKX..."
                )


                time.sleep(5)



        thread = threading.Thread(

            target=run,

            daemon=True

        )


        thread.start()