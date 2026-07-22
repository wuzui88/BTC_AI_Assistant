# BTC AI Assistant V10.3
# System Architecture

版本:
V10.3-multi-timeframe

分支:
V10.3-multi-timeframe


---

# 1. 系统概述


BTC AI Assistant 是一个面向 BTC 永续合约交易的 AI 辅助交易系统。

系统目标：

1. 实时采集交易行情
2. 构建多周期K线
3. 计算技术指标
4. 进行多周期市场分析
5. 生成交易信号
6. 执行模拟交易
7. 管理仓位风险
8. 记录交易结果
9. 分析策略表现


当前版本：

V10.3-multi-timeframe

核心升级：

- 多周期市场分析
- 市场状态管理
- 策略评分模型
- 风险管理模块
- 交易生命周期管理


---

# 2. 总体架构

             Exchange
                |
                |
      +----------------+
      | WebSocket/API |
      +----------------+
                |
                v

          data_feed

                |
                v

    +--------------------+
    | Kline Builder      |
    | Candle Manager     |
    +--------------------+

                |
                v

          indicators

                |
                v

    +--------------------+
    | Multi Timeframe    |
    | Market Analysis    |
    +--------------------+

                |
                v

          analysis

                |
                v

    +--------------------+
    | Strategy Engine    |
    | Scoring Engine     |
    +--------------------+

                |
                v

          risk

                |
                v

    +--------------------+
    | Paper Trader       |
    | Position Manager   |
    +--------------------+

                |
                v

          database

                |
                v

         Dashboard / Statistics


---

# 3. 数据采集层


目录：
data_feed/



职责：

负责交易所行情接入。


主要模块：

## okx_feed.py

OKX实时行情。


功能：

- WebSocket行情订阅
- Tick数据接收


---

## okx_api.py

OKX REST API。


功能：

- 历史K线
- 市场数据查询


---

## binance_feed.py

Binance行情接口。


---

## market_manager.py


市场数据统一管理。


负责：

- 当前价格
- K线缓存
- 市场状态


---

# 4. K线系统


目录：


kline/



职责：

构建标准交易K线。


主要模块：

## candle.py

K线数据结构。


---

## kline_builder.py

负责：

- Tick转换K线
- 周期生成


支持：

- 1分钟
- 5分钟
- 多周期扩展


---

## tick_cache.py

Tick缓存。


---

# 5. 指标计算层


目录：


indicator/
indicators/



职责：

技术指标计算。


当前支持：

- EMA
- MACD
- RSI
- ATR
- VWAP
- Volume Ratio


---

主要文件：


indicators/technical.py



统一指标入口。


输出：

```python
{
EMA20,
EMA50,
RSI,
MACD,
ATR,
VWAP,
VOLUME_RATIO,
ATR_PERCENT
}
6. 多周期市场分析层

目录：

market/
analysis/
market/multi_timeframe_analysis.py

V10.3核心模块。

职责：

融合多个周期：

例如：

1m
5m
15m
1h
4h

判断：

大趋势
当前周期趋势
趋势一致性

输出：

{
trend,
market_mode,
score,
confidence,
signal
}
analysis/market_analysis.py

负责：

单周期市场状态分析。

核心：

EMA趋势
MACD方向
RSI状态
VWAP位置
成交量
ATR市场模式
7. 策略层

目录：

strategy/
btc_strategy.py

交易决策核心。

职责：

输入：

market
indicators

输出：

{
direction,
action,
entry,
stop_loss,
take_profit,
risk_reward
}

负责：

做多条件
做空条件
入场过滤
止盈止损计算
scoring_engine.py

统一评分模型。

评分因素：

项目	权重
趋势	30
EMA	20
MACD	15
VWAP	10
RSI	10
成交量	10
confidence	10

输出：

score -100 ~ +100
signal_filter.py

信号过滤。

负责：

防止频繁交易
风险过滤
信号质量检查
8. 风控系统

目录：

risk/
risk_manager.py

负责：

仓位计算
最大风险
杠杆控制

输入：

balance
risk_percent
leverage

输出：

position_size
margin
risk_amount
9. 交易执行层

目录：

trade/
paper_trader.py

模拟交易引擎。

负责：

开仓
平仓
止盈
止损
移动止损

交易生命周期：

SIGNAL

↓

OPEN

↓

HOLD

↓

TRAIL_STOP

↓

CLOSE
10. 持仓管理

目录：

position/
position_manager.py

负责：

当前持仓
盈亏计算
状态同步
11. 数据库层

目录：

database/

负责：

数据持久化。

主要：

market_db.py

行情状态。

position_db.py

持仓。

trade_db.py

交易记录。

sqlite_db.py

数据库基础。

12. 回测系统

目录：

backtest/

负责：

历史行情回测
策略验证
13. Dashboard

目录：

dashboard/

提供：

当前行情
持仓状态
交易记录
策略表现
14. 主程序流程

main.py

执行流程：

启动

↓

初始化数据库

↓

连接交易所

↓

获取Tick

↓

生成K线

↓

计算指标

↓

多周期分析

↓

策略评分

↓

生成交易信号

↓

风险检查

↓

模拟交易

↓

保存数据库

↓

Dashboard展示
15. 当前版本特点

V10.3-multi-timeframe

新增：

多周期分析框架
市场状态模块
更完整交易链路

优化：

策略评分
风险过滤
仓位管理
交易记录
16. 后续升级方向
V10.4

计划：

多周期权重优化
趋势一致性评分
AI预测模型接入
V10.5

计划：

实盘交易接口
自动参数优化
策略机器学习