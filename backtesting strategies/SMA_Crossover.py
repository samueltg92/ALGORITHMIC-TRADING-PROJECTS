import pandas as pd
import yfinance as yf
import numpy as np
import talib as talib
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from backtesting import Strategy, Backtest
from backtesting.lib import crossover
import seaborn as sns

pd.options.mode.chained_assignment = None

# Creating DataFrame using Yahoo Finance
asset = str(input('Look on Yahho Finance for ticker /// '
                  'Asset to backtest: '))
df = yf.download(asset, start='1990-01-01')

df = df.reset_index()
df.set_index('Date', inplace=True)
print(df)

# Strategy definition
class SMACross(Strategy):
    n1 = 10
    n2 = 20
    
    def init(self):
        self.sma1 = self.I(talib.SMA, self.data.Close, self.n1)
        self.sma2 = self.I(talib.SMA, self.data.Close, self.n2)
        
    def next(self):
        if crossover(self.sma1, self.sma2):
            self.buy()
        elif crossover(self.sma2, self.sma1):
            self.position.close()

# Backtest deployment
print('*'*100)
print('*'*100)
print('BACKTESTING DEPLOYMENT')
print('*'*100)
bt = Backtest(df, SMACross, cash=10000, commission=0.04, exclusive_orders=True)
output= bt.run()
print(output)
bt.plot()

# Optimization process
print('*'*100)
print('*'*100)
print('OPTIMIZATION PROCESS')
print('*'*100)
stats, heatmap = bt.optimize(
    n1=range(5,120,5),
    n2=range(20,220,5),
    maximize='Equity Final [$]',
    constraint=lambda x: x.n1 < x.n2,
    return_heatmap=True
)

print(stats)
print(stats._strategy)
bt.plot()
print(heatmap.sort_values(ascending=False).iloc[:10])
hm = heatmap.groupby(['n1','n2']).mean().unstack()
plt.figure(figsize=(12,10))
sns.heatmap(hm[::-1], cmap='viridis')
# plt.savefig('sma-crossover-heatmap.png')