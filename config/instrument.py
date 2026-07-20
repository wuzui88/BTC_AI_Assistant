# =================================================
# OKX 合约规格
# =================================================


INSTRUMENT_CONFIG = {


    "BTC-USDT-SWAP": {


        # 每张合约对应BTC数量

        "contract_size": 0.01


    }


}




def get_contract_size(
    symbol
):


    config = INSTRUMENT_CONFIG.get(
        symbol
    )


    if not config:

        return 1


    return config.get(
        "contract_size",
        1
    )