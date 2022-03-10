import pandas as pd
import yfinance as yf
import numpy as np
import ta as ta

"""
    Market: S&P 500
    Define trend: price above 200-day MA
    Entry: 10-period RSI below 30 (buy on next day's open)
    Exit: 10-period RSI above 40 or after 10 trading days (sell on next day's open)
    
    Strategy taken from: https://www.youtube.com/watch?v=W8ENIXvcGlQ
"""
pd.options.mode.chained_assignment = None

# creating the DataFrame using YahooFinance
df = yf.download('^GSPC', start='1995-01-01')

# calculation of the 200-period MA using TA Lib
df['SMA200'] = ta.trend.sma_indicator(df.Close, window=200)
df = df.dropna()

# calculation of the 10-period RSI using TA Lib
df['RSI'] = ta.momentum.rsi(df.Close, window=10)
df = df.dropna()

# creating a Signal column to get the signal if a condition is met
df['Signal'] = np.where((df.Close > df.SMA200) & (df.RSI < 30), True, False)
print(df)

# creating the trading logic
buying_dates = []
selling_dates = []

for i in range(len(df)-11):
    if df.Signal.iloc[i]:
        buying_dates.append(df.iloc[i+1].name)
        for j in range(1,11):
            if df['RSI'].iloc[i+j] > 40:
                selling_dates.append(df.iloc[i+j+1].name)
                break
            elif j == 10:
                selling_dates.append(df.iloc[i+j+1].name)
                

# getting the real trades on profits                
frame = pd.DataFrame({'Buying_dates': buying_dates, 'Selling_dates': selling_dates})
real_trades = frame[frame.Buying_dates > frame.Selling_dates.shift(1)]
real_trades = frame[:1].append(real_trades)

# calculating profits
profits = df.loc[real_trades.Selling_dates].Open.values - df.loc[real_trades.Buying_dates].Open.values  
profits_trades = len([i for i in profits if i > 0]) 
win_rate = ((profits_trades)/(len(profits)))*100
print(f'Win Rate: {win_rate}%')

# calculating relative profits per trade
rel_profits = (df.loc[real_trades.Selling_dates].Open.values - df.loc[real_trades.Buying_dates].Open.values)/df.loc[real_trades.Buying_dates].Open.values
print(f'Relative profit (%) per trade: {rel_profits.mean()*100}%')

# calculating Net profits in %
net_profit = (((rel_profits+1).cumprod())-1)*100
print(f'Total net profit (%) was : {net_profit[-1]}%')

# calculating maximun Drawdown
max_dd = rel_profits.min()
print(f'Maximum drawdown was: {max_dd*100}%')