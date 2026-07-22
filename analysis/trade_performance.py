"""
trade_performance.py
BTC AI Assistant V10.1.9

交易表现分析模块
读取 trades 表并生成统计报告
"""

import sqlite3
from collections import Counter


class TradePerformance:

    def __init__(self, db_path="data/trading.db"):
        self.db_path = db_path


    def load_trades(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()
        cursor.execute("""
            SELECT *
            FROM trades
            ORDER BY id ASC
        """)

        rows = cursor.fetchall()
        conn.close()

        return rows


    def calculate(self):

        trades = self.load_trades()

        if not trades:
            return {
                "total": 0,
                "message": "暂无交易数据"
            }


        pnls = [
            float(t["pnl"] or 0)
            for t in trades
        ]

        wins = [
            p for p in pnls
            if p > 0
        ]

        losses = [
            p for p in pnls
            if p < 0
        ]


        total = len(trades)

        win_rate = (
            len(wins) / total * 100
        )


        total_pnl = sum(pnls)


        avg_win = (
            sum(wins) / len(wins)
            if wins else 0
        )


        avg_loss = (
            abs(sum(losses) / len(losses))
            if losses else 0
        )


        profit_factor = (
            sum(wins) / abs(sum(losses))
            if losses else 0
        )


        reasons = Counter(
            t["reason"]
            for t in trades
        )


        trailing = Counter(
            t["trailing_status"]
            for t in trades
        )


        return {

            "total": total,

            "wins": len(wins),

            "losses": len(losses),

            "win_rate": round(
                win_rate,
                2
            ),

            "total_pnl": round(
                total_pnl,
                2
            ),

            "avg_win": round(
                avg_win,
                2
            ),

            "avg_loss": round(
                avg_loss,
                2
            ),

            "profit_factor": round(
                profit_factor,
                2
            ),

            "exit_reason": dict(
                reasons
            ),

            "trailing_status": dict(
                trailing
            )
        }


    def print_report(self):

        r = self.calculate()

        print("=" * 40)
        print("BTC AI Performance Report")
        print("=" * 40)

        for k, v in r.items():
            print(
                f"{k}: {v}"
            )


if __name__ == "__main__":

    TradePerformance().print_report()
