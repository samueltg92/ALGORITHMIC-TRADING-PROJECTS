import ccxt
import pandas as pd

def ccxt_ohlcv_to_dataframe(ohlcv):
    df = pd.DataFrame(ohlcv)
    df.columns = ['time', 'open', 'high', 'low', 'close', 'volume']
    df['date'] = pd.to_datetime(df['time']*1000000, infer_datetime_format=True)
    
    return df

exchange = ccxt.binance()
symbol = 'BTC/USDT'
timeframe = '1h'
ohlcv = exchange.fetch_ohlcv(symbol,timeframe)
df = ccxt_ohlcv_to_dataframe(ohlcv)

print(df)
print(type(df['close'][0]))