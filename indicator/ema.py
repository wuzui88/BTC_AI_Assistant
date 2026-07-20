def EMA(data, period):

    if len(data) < period:
        return None


    ema = data[0]


    alpha = 2 / (period + 1)


    for price in data[1:]:

        ema = (
            price * alpha
            +
            ema * (1-alpha)
        )


    return ema