import backtrader as bt

class MaRsiStrat(bt.Strategy):
    
    params = (
        ('emaperiod', 200),
        ('rsiperiod', 2)      
              )
    
    def __init__(self):
        self.dataclose = self.datas[0].Close
        self.ma = bt.talib.EMA(self.dataclose, timeperiod = self.p.emaperiod)
        self.rsi = bt.talib.RSI(self.dataclose, timeperiod = self.p.rsiperiod)
        
    def next(self):
        
        if self.dataclose >= self.ema and self.rsi <= 10:
            self.buy()

        if self.dataclose <= self.ema and self.rsi >= 90:
            self.sell()