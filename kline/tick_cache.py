import threading
from collections import deque


class TickCache:


    def __init__(self, max_size=5000):

        self.ticks = deque(
            maxlen=max_size
        )

        self.lock = threading.Lock()



    def add(self, data):

        with self.lock:

            self.ticks.append(data)



    def latest(self):

        with self.lock:

            if self.ticks:

                return self.ticks[-1]

            return None



    def get_all(self):

        with self.lock:

            return list(self.ticks)