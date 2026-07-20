from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import asyncio
import json

from dashboard.data import get_dashboard_data


app = FastAPI()



# ==========================
# 首页
# ==========================

@app.get("/")
async def index():

    html = """

<!DOCTYPE html>

<html>


<head>

<title>
BTC AI Trading Dashboard
</title>



<style>


body{

    background:#111;

    color:white;

    font-family:Arial;

    padding:30px;

}



.title{

    font-size:36px;

    margin-bottom:30px;

}



.grid{

    display:flex;

    flex-wrap:wrap;

    gap:20px;

}



.card{

    background:#222;

    width:260px;

    padding:20px;

    border-radius:12px;

}



.card h3{

    color:#aaa;

}



.value{

    font-size:30px;

    color:#00ff99;

}



.red{

    color:#ff5555;

}



.yellow{

    color:#ffd700;

}



</style>


</head>




<body>


<div class="title">

BTC AI Trading Dashboard

</div>



<div class="grid">



<div class="card">

<h3>BTC价格</h3>

<div id="price" class="value">

0

</div>

</div>




<div class="card">

<h3>趋势</h3>

<div id="trend" class="value">

WAIT

</div>

</div>




<div class="card">

<h3>交易信号</h3>

<div id="signal" class="value">

WAIT

</div>

</div>




<div class="card">

<h3>当前仓位</h3>

<div id="position" class="value">

NONE

</div>

</div>




<div class="card">

<h3>浮动盈亏</h3>

<div id="pnl" class="value">

0

</div>

</div>




<div class="card">

<h3>止损</h3>

<div id="stop_loss" class="value">

0

</div>

</div>




<div class="card">

<h3>止盈</h3>

<div id="take_profit" class="value">

0

</div>

</div>




<div class="card">

<h3>RSI</h3>

<div id="rsi" class="value">

0

</div>

</div>




<div class="card">

<h3>MACD</h3>

<div id="macd" class="value">

0

</div>

</div>




<div class="card">

<h3>ATR</h3>

<div id="atr" class="value">

0

</div>

</div>



</div>





<script>


let ws = new WebSocket(

    "ws://" 
    +
    window.location.host
    +
    "/ws"

);




ws.onopen=function(){


    console.log(
        "Dashboard连接成功"
    );


};





ws.onmessage=function(event){


    let data =
    JSON.parse(event.data);



    document.getElementById(
        "price"
    ).innerHTML =
    data.price;




    document.getElementById(
        "trend"
    ).innerHTML =
    data.trend;




    document.getElementById(
        "signal"
    ).innerHTML =
    data.signal;




    document.getElementById(
        "position"
    ).innerHTML =
    data.position;




    document.getElementById(
        "pnl"
    ).innerHTML =
    data.pnl
    +
    " USDT";





    document.getElementById(
        "stop_loss"
    ).innerHTML =
    data.stop_loss;





    document.getElementById(
        "take_profit"
    ).innerHTML =
    data.take_profit;





    document.getElementById(
        "rsi"
    ).innerHTML =
    data.rsi;





    document.getElementById(
        "macd"
    ).innerHTML =
    data.macd;





    document.getElementById(
        "atr"
    ).innerHTML =
    data.atr;



};





ws.onerror=function(error){


    console.log(
        "WebSocket错误",
        error
    );
    ws.onclose=function(){

    console.log(
        "WebSocket断开，3秒后重连"
    );


    setTimeout(
        function(){

            location.reload();

        },
        3000
    );

};


};



</script>




</body>


</html>

"""


    return HTMLResponse(html)









# ==========================
# WebSocket实时数据
# ==========================

from fastapi import WebSocketDisconnect


@app.websocket("/ws")
async def websocket_endpoint(
        websocket: WebSocket
):

    await websocket.accept()

    print(
        "Dashboard WebSocket连接成功"
    )


    try:

        while True:


            data = get_dashboard_data()


            print(
                "发送Dashboard数据:",
                data
            )


            try:

                await websocket.send_json(
                    data
                )


            except Exception:


                print(
                    "客户端已关闭连接"
                )

                break



            await asyncio.sleep(1)



    except WebSocketDisconnect:


        print(
            "Dashboard客户端断开"
        )


    except Exception as e:


        print(
            "WebSocket异常:",
            e
        )