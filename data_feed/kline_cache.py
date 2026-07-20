from collections import deque



class KlineCache:



    def __init__(
        self,
        max_size=500
    ):


        self.max_size = max_size


        # 自动限制长度
        self.data = deque(
            maxlen=max_size
        )





    def add(
        self,
        candle
    ):


        if candle is None:

            return



        self.data.append(
            candle
        )







    def get_all(self):


        return list(
            self.data
        )







    def latest(self):


        if self.data:


            return self.data[-1]



        return None






    def size(self):


        return len(
            self.data
        )