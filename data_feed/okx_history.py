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


            "instId": inst_id,


            "bar": bar,


            "limit": limit


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



                # HTTP错误

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
                                )


                            }


                        )


                    except Exception:


                        continue






                candles.reverse()



                print(

                    f"OKX历史K线获取成功:{len(candles)}"

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