class RiskManager:



    def __init__(
        self,
        balance=20000,
        risk_percent=1,
        leverage=30,
        max_margin_percent=20,
        max_position=1
    ):


        self.balance = balance

        self.risk_percent = risk_percent

        self.leverage = leverage

        self.max_margin_percent = max_margin_percent

        self.max_position = max_position





    def adjust_risk_by_market(self, market):
        """根据行情强弱动态调整风险比例"""
        if not market:
            return self.risk_percent
        trend = market.get("trend", "")
        confidence = market.get("confidence", 0)
        if confidence < 50:
            return min(self.risk_percent, 0.5)
        if "rebound" in trend:
            return min(self.risk_percent, 0.75)
        return self.risk_percent


    def calculate(
        self,
        entry,
        stop_loss
    ):



        result = {


            "balance": self.balance,

            "risk_amount": None,

            "position_size": None,

            "margin": None,

            "actual_risk": None,

            "risk_level": None,

            "leverage": self.leverage

        }





        if entry is None or stop_loss is None:

            return result






        # =====================
        # 最大允许亏损
        # =====================


        risk_amount = (

            self.balance

            *

            self.risk_percent

            /

            100

        )


        result["risk_amount"] = round(

            risk_amount,

            2

        )






        # =====================
        # 止损距离
        # =====================


        stop_distance = abs(

            entry - stop_loss

        )


        if stop_distance == 0:

            return result







        # =====================
        # 根据风险计算仓位
        # =====================


        position_size = (

            risk_amount

            /

            stop_distance

        )








        # =====================
        # 最大BTC限制
        # =====================


        if position_size > self.max_position:


            position_size = self.max_position






        # =====================
        # 保证金计算
        # =====================


        margin = (

            position_size

            *

            entry

            /

            self.leverage

        )






        # =====================
        # 最大保证金限制
        # =====================


        max_margin = (

            self.balance

            *

            self.max_margin_percent

            /

            100

        )



        if margin > max_margin:


            margin = max_margin


            position_size = (

                margin

                *

                self.leverage

                /

                entry

            )








        # =====================
        # 实际风险
        # =====================


        actual_risk = (

            position_size

            *

            stop_distance

        )








        result["position_size"] = round(

            position_size,

            4

        )



        result["margin"] = round(

            margin,

            2

        )



        result["actual_risk"] = round(

            actual_risk,

            2

        )








        # =====================
        # 风险等级
        # =====================


        margin_rate = (

            margin

            /

            self.balance

        )



        if margin_rate <= 0.15:


            risk_level = "LOW"



        elif margin_rate <= 0.3:


            risk_level = "MEDIUM"



        else:


            risk_level = "HIGH"





        result["risk_level"] = risk_level





        return result