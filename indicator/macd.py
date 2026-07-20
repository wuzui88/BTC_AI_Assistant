from indicator.ema import EMA



def MACD(data):


    if len(data)<60:

        return None



    ema12=EMA(data,12)

    ema26=EMA(data,26)


    dif=ema12-ema26


    return {

        "dif":dif

    }