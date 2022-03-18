import pandas as pd
import yfinance as yf
import talib as talib
import matplotlib.pyplot as plt
from backtesting import Strategy, Backtest


"""
    Market: S&P 500
    Entry: Price above 500-day SMA & 10-period RSI below 30 
    Exit: close price below 500-day SMA
"""

pd.options.mode.chained_assignment = None

# create the DataFrame using YahooFinance
df = yf.download('^GSPC', start='1995-01-01')
print(df)


# defining the strategy
class MA_RSI(Strategy):
    n1 = 500
    n2 = 10
    
    def init(self):
        self.sma = self.I(talib.SMA, self.data.Close, self.n1)
        self.rsi = self.I(talib.RSI, self.data.Close, self.n2)
        
    def next(self):
        if self.data.Close > self.sma and self.rsi < 25:
            self.buy()
        elif self.data.Close < self.sma:
            self.position.close()
        
# Backtest deployment
print('*'*100)
print('*'*100)
print('BACKTESTING DEPLOYMENT')
print('*'*100)        
bt = Backtest(df, MA_RSI, cash=10_000, commission=0.04, exclusive_orders=False)
stats = bt.run()
print(stats)
bt.plot(plot_volume=False)