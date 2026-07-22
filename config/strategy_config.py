"""
strategy_config.py
BTC AI Assistant V10.1.9

统一策略参数配置
"""


STRATEGY_CONFIG = {


    # =========================
    # 信号评分
    # =========================

    "LONG_SCORE_THRESHOLD": 75,

    "SHORT_SCORE_THRESHOLD": 75,


    "WAIT_SCORE_THRESHOLD": 55,



    # =========================
    # 成交量过滤
    # =========================

    "MIN_VOLUME_RATIO": 0.6,
     # 成交量过滤
    "LOW_VOLUME_BLOCK": 0.25,
     # 最低信心
    "MIN_CONFIDENCE": 50,

    # =========================
    # ATR风险
    # =========================
    # ATR止损
    "STOP_ATR_MULTIPLE": 1.6,
    # ATR止盈
    "TAKE_PROFIT_ATR_MULTIPLE": 2.8,



    # =========================
    # 移动止损
    # =========================
    # 保本
    "BREAK_EVEN_PROFIT": 60,
    # 开始追踪
    "TRAIL_START_PROFIT": 120,
    # ATR追踪距离
    "TRAIL_ATR_MULTIPLE": 0.8,



    # =========================
    # RSI过滤
    # =========================

    "RSI_OVERBUY": 75,

    "RSI_OVERSOLD": 30,



    # =========================
    # 风险控制
    # =========================

    "MAX_POSITION_RISK": 0.01,
    # 杠杆
    "DEFAULT_LEVERAGE": 30

}
