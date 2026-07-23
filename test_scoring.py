# ============================================================
# test_scoring.py
#
# BTC AI Assistant V10.2
#
# scoring_engine 统一模型测试
#
# 与 live 模型完全一致
# ============================================================


from strategy.scoring_engine import scoring_engine



# ============================================================
# 测试案例1
#
# BTC真实日志:
#
# 价格:
# 66691.1
#
# MARKET:
# bullish
# WAIT_LONG
#
# ============================================================


case_1 = {


    "price":

        66691.1,


    "EMA20":

        66500.76,


    "EMA50":

        66418.04,


    "RSI":

        42.17,


    "MACD":

        91.35,


    "VWAP":

        65801.02,


    "VOLUME_RATIO":

        1.03,


    "ATR_PERCENT":

        0.00116

}





# ============================================================
# 测试案例2
#
# 成交量不足
#
# BTC:
# VOLUME_RATIO 0.62
#
# ============================================================


case_2 = {


    "price":

        66673.8,


    "EMA20":

        66532.71,


    "EMA50":

        66437.95,


    "RSI":

        60,


    "MACD":

        94.49,


    "VWAP":

        66158.57,


    "VOLUME_RATIO":

        0.62,


    "ATR_PERCENT":

        0.00112

}





# ============================================================
# 测试案例3
#
# RSI高位 + 极低成交量
#
# 防止追涨
#
# ============================================================


case_3 = {


    "price":

        66369.7,


    "EMA20":

        66489.01,


    "EMA50":

        66452.94,


    "RSI":

        73.83,


    "MACD":

        -12.96,


    "VWAP":

        66179.48,


    "VOLUME_RATIO":

        0.08,


    "ATR_PERCENT":

        0.00118

}





# ============================================================
# 测试案例4
#
# 空头环境
#
# ============================================================


case_4 = {


    "price":

        66000,


    "EMA20":

        66200,


    "EMA50":

        66400,


    "RSI":

        35,


    "MACD":

        -80,


    "VWAP":

        66500,


    "VOLUME_RATIO":

        1.3,


    "ATR_PERCENT":

        0.002

}

# ============================================================
# 测试案例5
#
# MTF 多周期一致多头
#
# 1H  bullish
# 15M bullish
# 5M bullish
#
# ============================================================


case_5 = {


    "price":

        66691.1,


    "EMA20":

        66500.76,


    "EMA50":

        66418.04,


    "RSI":

        42,


    "MACD":

        90,


    "VWAP":

        65800,


    "VOLUME_RATIO":

        1.2,


    "ATR_PERCENT":

        0.0012,



    "MTF": {


        "1H": {

            "trend":

                "bullish",


            "score":

                80

        },


        "15M": {

            "trend":

                "bullish",


            "score":

                70

        },


        "5M": {

            "trend":

                "bullish",


            "score":

                60

        }

    }

}

# ============================================================
# 测试案例6
#
# MTF 空头压制
#
# 1H bearish
# 15M bearish
# 5M bullish
#
# 防止逆势抄底
#
# ============================================================


case_6 = {


    "price":

        66000,


    "EMA20":

        66100,


    "EMA50":

        66300,


    "RSI":

        45,


    "MACD":

        -20,


    "VWAP":

        66400,


    "VOLUME_RATIO":

        1.1,


    "ATR_PERCENT":

        0.0015,



    "MTF": {


        "1H": {

            "trend":

                "bearish",


            "score":

                -70

        },


        "15M": {

            "trend":

                "bearish",


            "score":

                -60

        },


        "5M": {

            "trend":

                "bullish",


            "score":

                50

        }

    }

}



def run_test(
    name,
    data
):


    print("\n")

    print("=" * 60)

    print(name)

    print("=" * 60)



    result = scoring_engine.evaluate(

        data

    )



    print()

    print(

        "趋势:",

        result["trend"]

    )


    print(

        "市场模式:",

        result["market_mode"]

    )


    print(

        "评分:",

        result["score"]

    )


    print(

        "信心:",

        result["confidence"]

    )


    print(

        "信号:",

        result["signal"]

    )



    print()

    print(

        "原因:"

    )


    for r in result["reason"]:


        print(

            " +",

            r

        )



    print()

    print(

        "警告:"

    )


    for w in result["warning"]:


        print(

            " -",

            w

        )





if __name__ == "__main__":



    run_test(

        "测试案例1 - BTC真实多头等待",

        case_1

    )



    run_test(

        "测试案例2 - BTC成交量不足",

        case_2

    )



    run_test(

        "测试案例3 - RSI高位低量过滤",

        case_3

    )



    run_test(

        "测试案例4 - 空头环境",

        case_4

    )

    run_test(

        "测试案例5 - MTF三周期一致多头",

        case_5

    )



    run_test(

        "测试案例6 - MTF高周期空头压制",

        case_6

    )