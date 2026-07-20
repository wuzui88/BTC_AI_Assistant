class PositionManager:



    def __init__(
        self,
        contract_size=0.01
    ):


        # 每张合约对应BTC数量

        self.contract_size = contract_size





    def create_order(
        self,
        direction,
        position_size,
        leverage=30
    ):



        result = {


            "instId": "BTC-USDT-SWAP",

            "side": None,

            "posSide": None,

            "size_btc": None,

            "contracts": None,

            "leverage": leverage

        }





        if direction == "LONG":


            result["side"] = "buy"

            result["posSide"] = "long"




        elif direction == "SHORT":


            result["side"] = "sell"

            result["posSide"] = "short"




        else:


            return result







        # BTC数量

        result["size_btc"] = round(

            position_size,

            4

        )






        # BTC转换合约张数

        contracts = (

            position_size

            /

            self.contract_size

        )



        result["contracts"] = int(

            contracts

        )





        return result