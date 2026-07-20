import websocket
import json
import time
import threading

from config.instrument import get_contract_size



class OKXFeed:


    def __init__(
        self,
        callback
    ):


        # =========================
        # 基础配置
        # =========================

        self.symbol = (
            "BTC-USDT-SWAP"
        )


        self.contract_size = (
            get_contract_size(
                self.symbol
            )
        )


        self.callback = callback



        self.url = (
            "wss://ws.okx.com:8443/ws/v5/public"
        )



        self.ws = None



        # =========================
        # 状态控制
        # =========================

        self.running = True


        self.reconnect_count = 0



        # 错误防刷

        self.last_error_time = 0




        # =========================
        # 成交量缓存
        # =========================

        self.volume_cache = 0.0



        # 成交量线程锁

        self.volume_lock = (
            threading.Lock()
        )








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



                print(
                    "开始运行WebSocket..."
                )



                self.ws.run_forever(


                    ping_interval=15,


                    ping_timeout=10,

                    origin="https://www.okx.com"
                 

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









    def on_open(

        self,

        ws

    ):


        self.reconnect_count = 0



        print(

            "OKX WebSocket连接成功"

        )



        print(

            "正在订阅OKX频道..."

        )




        subscribe = {


            "op":

            "subscribe",



            "args": [



                {


                    "channel":

                    "tickers",


                    "instId":

                    self.symbol


                },



                {


                    "channel":

                    "trades",


                    "instId":

                    self.symbol


                }



            ]

        }




        ws.send(

            json.dumps(
                subscribe
            )

        )



        print(

            "OKX订阅发送完成"

        )









    def on_message(

        self,

        ws,

        message

    ):


        try:



            data = json.loads(
                message
            )




            # =========================
            # OKX事件消息
            # =========================


            if "event" in data:

                return





            if "arg" not in data:


                return





            channel = data["arg"].get(

                "channel"

            )



            if "data" not in data:


                return




            if not data["data"]:


                return







            # =========================
            # trades成交量
            # =========================


            if channel == "trades":



                for trade in data["data"]:



                    size = trade.get(
                        "sz"
                    )



                    if size is None:

                        continue



                    try:


                        volume = (

                            float(size)

                            *

                            self.contract_size

                        )



                        with self.volume_lock:


                            self.volume_cache += volume



                    except:


                        pass



                return







            # =========================
            # tickers价格
            # =========================


            if channel != "tickers":


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







            # =========================
            # 获取成交量
            # =========================


            with self.volume_lock:



                volume = (

                    self.volume_cache

                )



                self.volume_cache = 0.0







            self.callback({



                "type":

                "tick",



                "exchange":

                "OKX",



                "symbol":

                self.symbol,



                "price":

                price,



                "size":

                volume,



                "time":

                int(

                    time.time()

                    *

                    1000

                )



            })








        except Exception as e:



            self.log_error(

                "OKX解析错误",

                e

            )









    def on_error(

        self,

        ws,

        error

    ):


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



        if (

            now -

            self.last_error_time

            <

            5

        ):


            return





        self.last_error_time = now



        print(

            title,

            error

        )