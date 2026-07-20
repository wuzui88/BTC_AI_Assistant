class PaperTrader:


    def __init__(self):


        self.position = None


        self.history = []





    def open_position(
        self,
        order,
        entry,
        stop_loss,
        take_profit
    ):


        if self.position:


            return {

                "status": "EXIST_POSITION",

                "position": self.position

            }





        self.position = {


            "direction": order["posSide"],


            "side": order["side"],


            "entry": entry,


            "stop_loss": stop_loss,


            "take_profit": take_profit,


            "size_btc": order["size_btc"],


            "contracts": order["contracts"]


        }





        return {


            "status": "OPEN_SUCCESS",

            "position": self.position

        }







    def check_position(
        self,
        price
    ):



        if self.position is None:


            return None






        direction = self.position["direction"]



        entry = self.position["entry"]


        stop_loss = self.position["stop_loss"]


        take_profit = self.position["take_profit"]


        size = self.position["size_btc"]






        result = None






        # =====================
        # 多单
        # =====================


        if direction == "long":



            if price <= stop_loss:



                result = self.close_position(

                    price,

                    "STOP_LOSS"

                )




            elif price >= take_profit:



                result = self.close_position(

                    price,

                    "TAKE_PROFIT"

                )









        # =====================
        # 空单
        # =====================


        elif direction == "short":



            if price >= stop_loss:



                result = self.close_position(

                    price,

                    "STOP_LOSS"

                )




            elif price <= take_profit:



                result = self.close_position(

                    price,

                    "TAKE_PROFIT"

                )







        return result







    def close_position(
        self,
        price,
        reason
    ):


        position = self.position



        if position is None:


            return None






        entry = position["entry"]


        size = position["size_btc"]






        if position["direction"] == "long":



            pnl = (

                price - entry

            ) * size





        else:



            pnl = (

                entry - price

            ) * size







        record = {


            "direction": position["direction"],


            "entry": entry,


            "exit": price,


            "size": size,


            "pnl": round(

                pnl,

                2

            ),


            "reason": reason


        }






        self.history.append(record)



        self.position = None




        return {


            "status": "CLOSED",


            "record": record

        }