import sqlite3



class TradeStatistics:


    def __init__(
        self,
        db_path="btc_ai.db"
    ):

        self.db_path = db_path





    # =====================
    # 获取交易
    # =====================

    def get_trades(self):


        conn = sqlite3.connect(

            self.db_path

        )


        cursor = conn.cursor()


        cursor.execute(
            """
            SELECT

            direction,
            entry,
            exit,
            pnl,
            reason,
            hold_minutes,
            max_profit,
            max_drawdown

            FROM trades

            ORDER BY id ASC

            """
        )


        rows = cursor.fetchall()


        conn.close()


        return rows







    # =====================
    # 分析
    # =====================

    def analyze(self):


        trades = self.get_trades()


        if not trades:


            return {

                "message":
                "暂无交易"

            }





        total = len(trades)


        win = 0

        lose = 0



        total_profit = 0

        total_loss = 0



        profits = []

        losses = []



        hold_times = []


        win_hold_times = []

        lose_hold_times = []



        drawdowns = []



        retraces = []



        stop_count = 0





        for t in trades:



            pnl = t[3]

            reason = t[4]

            hold = t[5] or 0

            max_profit = t[6] or 0

            max_drawdown = t[7] or 0





            hold_times.append(

                hold

            )


            drawdowns.append(

                max_drawdown

            )






            # 盈利

            if pnl > 0:



                win += 1


                total_profit += pnl


                profits.append(

                    pnl

                )


                win_hold_times.append(

                    hold

                )



                # 盈利回吐

                if max_profit > 0:


                    retrace = (

                        max_profit - pnl

                    ) / max_profit * 100


                    retraces.append(

                        retrace

                    )




            else:



                lose += 1


                total_loss += pnl


                losses.append(

                    pnl

                )


                lose_hold_times.append(

                    hold

                )





            if reason in [

                "STOP_LOSS",

                "TRAIL_STOP"

            ]:


                stop_count += 1






        # 胜率


        win_rate = round(

            win / total * 100,

            2

        )






        # 平均盈利

        avg_profit = round(

            sum(profits)

            /

            len(profits)

            if profits else 0,

            2

        )





        # 平均亏损

        avg_loss = round(

            sum(losses)

            /

            len(losses)

            if losses else 0,

            2

        )






        # 盈亏比

        rr = 0


        if abs(avg_loss) > 0:


            rr = round(

                avg_profit

                /

                abs(avg_loss),

                2

            )






        return {



            "total_trades":

                total,


            "win":

                win,


            "lose":

                lose,


            "win_rate":

                win_rate,



            "net_profit":

                round(

                    total_profit

                    +

                    total_loss,

                    2

                ),



            "average_profit":

                avg_profit,



            "average_loss":

                avg_loss,



            "profit_loss_ratio":

                rr,



            "average_hold_minutes":

                round(

                    sum(hold_times)

                    /

                    total,

                    1

                ),



            "win_average_hold":

                round(

                    sum(win_hold_times)

                    /

                    len(win_hold_times)

                    if win_hold_times else 0,

                    1

                ),



            "lose_average_hold":

                round(

                    sum(lose_hold_times)

                    /

                    len(lose_hold_times)

                    if lose_hold_times else 0,

                    1

                ),



            "max_profit":

                round(

                    max(

                        [

                        t[6] or 0

                        for t in trades

                        ]

                    ),

                    2

                ),




            "average_profit_retrace":

                round(

                    sum(retraces)

                    /

                    len(retraces)

                    if retraces else 0,

                    2

                ),




            "stop_loss_count":

                stop_count,



            "average_drawdown":

                round(

                    sum(drawdowns)

                    /

                    len(drawdowns)

                    if drawdowns else 0,

                    2

                )

        }








    # =====================
    # 输出报告
    # =====================

    def print_report(self):


        data = self.analyze()



        print()

        print(
            "==========交易统计=========="
        )


        for k,v in data.items():


            print(

                k,

                ":",

                v

            )


        print(
            "============================"
        )