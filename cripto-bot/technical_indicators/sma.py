import ccxt
import pandas_ta as ta
import pandas as pd
from utils import ccxt_ohlcv_to_dataframe

def SimpleMovingAverage(source, period):
    
    sma = []
    source = list(source)
    
    for i in range(period - 1):
        sma.append(None)
        
    for i in range (period, len(source) + 1):
        sma.append(sum(source[(i-period): i])/period)
        
    return sma

exchange = ccxt.binance()
symbol = 'BTC/USDT'
timeframe = '1h'
ohlcv = exchange.fetch_ohlcv(symbol,timeframe)
df = ccxt_ohlcv_to_dataframe(ohlcv)

df['sma'] = SimpleMovingAverage(df['close'], 10)
df['sma_ta'] = df.ta.sma(length = 10)

print(df.drop(columns = ['time', 'open', 'high', 'low', 'volume', 'date']))