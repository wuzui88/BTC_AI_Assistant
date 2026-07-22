# BTC AI Assistant System Architecture

版本:
V10.3-multi-timeframe

更新时间:
2026-07-22

项目:
BTC AI Assistant

目标:
构建一个基于实时行情、多周期技术分析、AI评分、风险控制和自动交易执行的 BTC 永续合约智能交易系统。


---

# 1. 系统总体架构

                OKX / Binance
                     |
                     |
             WebSocket行情层
                     |
                     v

             data_feed

                     |
                     v

          kline 多周期K线管理

                     |
                     |
    --------------------------------
    |              |               |
    v              v               v

   1H             15M             5M
大趋势判断      趋势确认        入场分析


                     |
                     v

             indicators


                     |
                     v

          market_analysis


                     |
                     v

          scoring_engine


                     |
                     v

           btc_strategy


                     |
                     v

                risk


                     |
                     v

                trade


                     |
                     v

              position管理


                     |
                     v

              database记录



---

# 2. 核心模块说明


## 2.1 data_feed


职责:

- 获取交易所实时行情
- WebSocket连接管理
- Tick数据处理


输入:

交易所:

- OKX
- Binance


输出:

```python
{
    price,
    volume,
    timestamp
}

2.2 kline

职责:

多周期K线管理。

支持周期:

1m
5m
15m
1H
4H

功能:

K线缓存
K线合成
最新K线维护

输出:

[
 {
  open,
  high,
  low,
  close,
  volume,
  time
 }
]
2.3 indicators

职责:

计算技术指标。

当前指标:

趋势指标
EMA20
EMA50
动量指标
RSI
MACD
波动指标
ATR
ATR_PERCENT
成交指标
Volume Ratio
资金指标
VWAP

输出:

{
"EMA20":0,
"EMA50":0,
"RSI":0,
"MACD":0,
"ATR":0,
"VWAP":0,
"VOLUME_RATIO":0
}
3. 多周期分析模型
3.1 周期职责
周期	职责
4H	长期趋势
1H	主要方向
15M	趋势确认
5M	交易信号
1M	执行优化
3.2 多周期决策逻辑

例如:

做空条件

4H:

下降趋势

1H:

EMA20 < EMA50
MACD < 0

15M:

反弹失败

5M:

出现空头信号

最终:

允许SHORT

如果周期冲突:

例如:

1H bullish

5M bearish

处理:

禁止立即开仓

等待周期统一
4. Market Analysis

文件:

analysis/market_analysis.py

职责:

判断市场状态。

输出:

{
"trend":"",
"market_mode":"",
"score":0,
"signal":"",
"confidence":0,
"reason":[],
"warning":[]
}

趋势类型:

bullish

bearish

bullish_pullback

bearish_rebound

neutral
5. Scoring Engine

文件:

strategy/scoring_engine.py

职责:

综合评分。

评分来源:

项目	分值
EMA趋势	±30
MACD	±20
RSI	±15
VWAP	±10
成交量	±15
ATR风险	±10

输出:

-100 ~ +100
6. Strategy Engine

文件:

strategy/btc_strategy.py

职责:

根据市场分析结果生成交易动作。

输出:

{
direction,
action,
entry,
stop_loss,
take_profit,
risk_reward
}

动作:

ENTER

WAIT

HOLD

CLOSE
7. Risk Management

目录:

risk/

职责:

仓位计算
最大风险控制
杠杆限制
RR过滤

当前模型:

本金:

20000 USDT

单笔风险:

1%

最大风险:

200 USDT
8. Trade Execution

目录:

trade/

职责:

下单
撤单
模拟交易
实盘接口

支持:

Paper Trading

OKX Swap
9. Position Management

目录:

position/

职责:

持仓记录
盈亏计算
移动止损
止盈止损
10. Database

数据库:

btc_ai.db

保存:

K线数据
指标
信号
交易记录
回测结果
11. 当前版本
V10.2.2

完成:

单周期交易
策略评分
风险控制
V10.3

开发目标:

完成:

多周期分析
大周期过滤
小周期执行
12. V10.3升级目标
新交易流程
Higher Timeframe

↓

Trend Confirmation

↓

Entry Signal

↓

Risk Check

↓

Order



核心原则:

不要因为5分钟短线信号逆势开仓。

13. 后续规划

V10.4:

AI预测模型
情绪分析
新闻因子

V10.5:

自动参数优化
强化学习

V11:

多交易品种支持


---
