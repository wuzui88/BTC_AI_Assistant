import requests
import time


class OKXAPI:


    def __init__(self):

        self.url = (
            "https://aws.okx.com/api/v5/market/candles"
        )



    def get_candles(
            self,
            instId="BTC-USDT-SWAP",
            bar="5m",
            limit=300
    ):


        try:

            params = {

                "instId": instId,

                "bar": bar,

                "limit": limit
            }



            response = requests.get(
                self.url,
                params=params,
                timeout=10
            )


            result = response.json()



            if result["code"] != "0":

                print(
                    "OKX K线获取失败:",
                    result
                )

                return []



            candles=[]



            # OKX返回:
            # [ts,o,h,l,c,vol,...]

            for item in result["data"]:


                candle={

                    "time":int(item[0]),

                    "open":float(item[1]),

                    "high":float(item[2]),

                    "low":float(item[3]),

                    "close":float(item[4])

                }


                candles.append(
                    candle
                )



            # OKX时间倒序
            # 转成正序

            candles.reverse()


            return candles



        except Exception as e:


            print(
                "OKX历史K线错误:",
                e
            )


            return []