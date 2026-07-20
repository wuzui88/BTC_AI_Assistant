import websocket
import json
import time
import threading



class OKXFeed:


    def __init__(self, callback):

        self.callback = callback


        self.url = (
            "wss://ws.okx.com:8443/ws/v5/public"
        )


        self.ws = None


        # 重连控制

        self.reconnect_count = 0

        self.running = True


        # 错误防刷屏

        self.last_error_time = 0





    def start(self):


        thread = threading.Thread(

            target=self.connect

        )


        thread.daemon = True


        thread.start()





    def stop(self):


        self.running = False


        if self.ws:

            try:

                self.ws.close()

            except:

                pass







    def connect(self):


        while self.running:


            try:


                print(
                    "正在连接OKX WebSocket..."
                )


                self.ws = websocket.WebSocketApp(


                    self.url,


                    on_open=self.on_open,


                    on_message=self.on_message,


                    on_error=self.on_error,


                    on_close=self.on_close


                )



                self.ws.run_forever(


                    ping_interval=15,


                    ping_timeout=10


                )



            except Exception as e:


                self.log_error(

                    "OKX异常",

                    e

                )




            if not self.running:

                break



            self.reconnect_count += 1



            delay = min(

                60,

                5 * self.reconnect_count

            )



            print(

                f"OKX {delay}秒后重新连接..."

            )



            time.sleep(delay)









    def on_open(self, ws):


        self.reconnect_count = 0



        print(

            "OKX WebSocket连接成功"

        )



        # =====================
        # 只订阅实时行情
        #
        # K线由本地生成
        # =====================


        subscribe = {


            "op":

            "subscribe",


            "args": [


                {


                    "channel":

                    "tickers",


                    "instId":

                    "BTC-USDT-SWAP"


                }


            ]

        }



        ws.send(

            json.dumps(subscribe)

        )









    def on_message(self, ws, message):


        try:


            data = json.loads(message)



            # 过滤系统消息

            if "arg" not in data:

                return



            channel = data["arg"].get(

                "channel"

            )



            if channel != "tickers":

                return



            if "data" not in data:

                return



            if not data["data"]:

                return




            ticker = data["data"][0]



            last = ticker.get(

                "last"

            )



            if last is None:

                return



            try:


                price = float(last)


            except:


                return




            if price <= 0:

                return





            self.callback({


                "type":

                "tick",



                "exchange":

                "OKX",



                "symbol":

                "BTC-USDT-SWAP",



                "price":

                price,



                "time":

                int(

                    time.time()*1000

                )


            })






        except Exception as e:


            self.log_error(

                "OKX解析错误",

                e

            )









    def on_error(self, ws, error):


        self.log_error(

            "OKX错误",

            error

        )









    def on_close(

        self,

        ws,

        code=None,

        msg=None

    ):


        print(

            "OKX连接关闭"

        )









    def log_error(

        self,

        title,

        error

    ):


        now = time.time()



        # 5秒最多一次

        if now - self.last_error_time < 5:

            return



        self.last_error_time = now



        print(

            title,

            error

        )