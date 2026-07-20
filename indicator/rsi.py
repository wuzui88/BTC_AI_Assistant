def RSI(data, period=14):

    if len(data) < period + 1:
        return None


    gains = []
    losses = []


    for i in range(1,len(data)):

        diff = data[i]-data[i-1]


        if diff >=0:

            gains.append(diff)
            losses.append(0)

        else:

            gains.append(0)
            losses.append(abs(diff))


    avg_gain=sum(gains[-period:])/period

    avg_loss=sum(losses[-period:])/period


    if avg_loss==0:
        return 100


    rs=avg_gain/avg_loss


    return 100-(100/(1+rs))