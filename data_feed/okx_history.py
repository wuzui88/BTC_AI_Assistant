import requests
import time



class OKXHistory:



    def __init__(self):


        self.url = (
            "https://www.okx.com"
            "/api/v5/market/history-candles"
        )


        self.session = requests.Session()





    def get_history(
        self,
        inst_id="BTC-USDT-SWAP",
        bar="5m",
        limit=300
    ):



        params = {


            "instId":

                inst_id,


            "bar":

                bar,


            "limit":

                limit

        }




        retry_times = 3




        for attempt in range(
            retry_times
        ):


            try:



                r = self.session.get(


                    self.url,


                    params=params,


                    timeout=30

                )



                r.raise_for_status()



                data = r.json()



                if data.get("code") != "0":


                    print(

                        "OKX历史K线错误:",

                        data

                    )


                    return []






                candles = []





                for item in data.get(
                    "data",
                    []
                ):



                    try:



                        # =================================================
                        #
                        # OKX history-candles 返回:
                        #
                        # item[0]  时间
                        # item[1]  开
                        # item[2]  高
                        # item[3]  低
                        # item[4]  收
                        # item[5]  vol       合约张数
                        # item[6]  volCcy    BTC数量
                        # item[7]  volCcyQuote USDT成交额
                        #
                        # 系统统一:
                        #
                        # volume = BTC数量
                        #
                        # =================================================



                        volume = float(
                            item[6]
                        )



                        candles.append(



                            {


                                "time":

                                int(
                                    item[0]
                                ),



                                "open":

                                float(
                                    item[1]
                                ),



                                "high":

                                float(
                                    item[2]
                                ),



                                "low":

                                float(
                                    item[3]
                                ),



                                "close":

                                float(
                                    item[4]
                                ),

                                # OKX SWAP统一使用BTC数量作为volume
                                # item[6] = volCcy
                                "volume":

                                float(
                                    item[6]
                                ) if len(item) > 6 else 0.0,



                                "volume":

                                volume,



                                "volume_unit":

                                "BTC"



                            }



                        )





                    except Exception as e:



                        print(

                            "解析OKX历史K线失败:",

                            e

                        )


                        continue







                candles.reverse()





                print(

                    f"OKX历史K线获取成功:{len(candles)}"

                )



                if candles:


                    print(

                        "最新K线成交量:",

                        candles[-1]["volume"],

                        candles[-1]["volume_unit"]

                    )




                return candles









            except Exception as e:



                print(

                    f"OKX历史K线请求失败 "
                    f"({attempt+1}/{retry_times}):",

                    e

                )



                if attempt < retry_times - 1:



                    wait = (

                        2

                        +

                        attempt * 3

                    )



                    print(

                        f"{wait}秒后重试..."

                    )



                    time.sleep(wait)









        print(

            "OKX历史K线获取失败，使用本地数据"

        )


        return []

    def get_multi_timeframe(
        self,
        inst_id="BTC-USDT-SWAP",
        limit=200
    ):

        return {
            "5M": self.get_history(
                inst_id,
                "5m",
                300
            ),
            "15M": self.get_history(
                inst_id,
                "15m",
                limit
            ),
            "1H": self.get_history(
                inst_id,
                "1H",
                limit
            )
        }
