class MTFBuilder:


    def __init__(self):

        self.data = {

            "5M":[],
            "15M":[],
            "1H":[]

        }


    def load_history(self, history):

        if not history:
            return

        self.data["5M"] = history.get("5M", [])[-300:]
        self.data["15M"] = history.get("15M", [])[-200:]
        self.data["1H"] = history.get("1H", [])[-200:]


    def update(self,candle):


        self.data["5M"].append(
            candle
        )


        self.build(
            "15M",
            3
        )


        self.build(
            "1H",
            12
        )


        return self.get_latest()



    def get_latest(self):


        return {


            "5M":
            self.data["5M"][-100:],


            "15M":
            self.data["15M"][-100:],


            "1H":
            self.data["1H"][-100:]

        }



    def build(
        self,
        name,
        count
    ):


        source=self.data["5M"]


        if len(source)<count:

            return



        group_index=len(source)//count


        existing=len(self.data[name])


        if group_index <= existing:

            return



        group=source[-count:]



        candle={


            "time":
            group[0]["time"],


            "open":
            group[0]["open"],


            "high":
            max(
                x["high"]
                for x in group
            ),


            "low":
            min(
                x["low"]
                for x in group
            ),


            "close":
            group[-1]["close"],


            "volume":
            sum(
                x["volume"]
                for x in group
            )

        }



        self.data[name].append(
            candle
        )