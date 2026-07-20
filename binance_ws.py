import websocket
import json
import ssl


def on_open(ws):

    print("Binance连接成功")

    msg = {
        "method": "SUBSCRIBE",
        "params": [
            "btcusdt@ticker"
        ],
        "id": 1
    }

    ws.send(json.dumps(msg))


def on_message(ws, message):

    print(message)


def on_error(ws,error):

    print("错误:",error)


def on_close(ws,*args):

    print("关闭")


ws = websocket.WebSocketApp(
    "wss://stream.binance.com:9443/ws",
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)


ws.run_forever(
    sslopt={
        "cert_reqs":ssl.CERT_NONE
    }
)