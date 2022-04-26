import backtrader as bt
import datetime as datetime
from strategy import MaRsiStrat

cerebro = bt.Cerebro()

data = bt.feeds.GenericCSVData(dataname = '/mnt/c/Users/samue/Documents/ALGORITHMIC-TRADING-PROJECTS/backtesting strategies/data_sets/EURUSD_Candlestick_15_M_BID_21.04.2004-16.04.2022-copy.csv',
    name = 'EUR-USD 15min',
    fromdate = datetime.datetime(2004, 4, 21),
    todate = datetime.datetime(2022, 4, 16),
    timeframe = bt.TimeFrame.Minutes,
    compression = 15,
    datetime = 0,
    open = 1,
    high = 2,
    low = 3,
    close = 4,
    volume = 5,
    openinterest = -1,
    dtformat = '%Y-%m-%d %H:%M:%S'
)


cerebro.adddata(data)
cerebro.addstrategy(MaRsiStrat)
cerebro.broker.setcash(100.0)



get_value = cerebro.broker.getvalue()
print(f'Starting value: {get_value}')

cerebro.run()

print(f'Final value: {get_value}')