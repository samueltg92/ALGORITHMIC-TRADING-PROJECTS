import backtrader as bt
import datetime

class MaRsiStrat(bt.Strategy):
    
    params = (
        ('emaperiod', 200),
        ('rsiperiod', 2)      
              )
    
    def log(self):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
    
    def __init__(self):
        self.dataclose = self.datas[0].Close
        self.ma = bt.talib.EMA(self.dataclose, timeperiod = self.p.emaperiod)
        self.rsi = bt.talib.RSI(self.dataclose, timeperiod = self.p.rsiperiod)
        
    def next(self):
        
        self.log('Close, %.2f' % self.dataclose[0])
        
        if self.dataclose >= self.ema and self.rsi <= 10:
            self.log('BUY CREATED, %.2f' % self.dataclose[0])
            self.buy()

        if self.dataclose <= self.ema and self.rsi >= 90:
            self.log('SELL CREATED, %.2f' % self.dataclose[0])
            self.sell()