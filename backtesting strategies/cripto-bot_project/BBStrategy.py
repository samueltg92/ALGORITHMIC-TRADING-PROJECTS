import pandas_ta as ta
import pandas as pd
import ccxt
from data_processing import ccxt_ohlcv_to_dataframe

exchange = ccxt.binance()
symbol = 'BTC/USDT'
timeframe = '1h'
ohlcv = exchange.fetch_ohlcv(symbol, timeframe)
df = ccxt_ohlcv_to_dataframe(ohlcv)


class BBStrategy():
    
    def __init__(self, bb_len=20, n_std=2.0, rsi_len=14, rsi_ob=60, rsi_os=40):
        self.bb_len = bb_len
        self.n_std = n_std
        self.rsi_len = rsi_len
        self.rsi_ob = rsi_ob
        self.rsi_os = rsi_os
        
    def setup(self, df):
        bb = ta.bbands(
            close = df['close'],
            length = self.bb_len,
            std = self.n_std, fillna = 0)
        
        df['lbb'] = bb.iloc[:,0]
        df['mbb'] = bb.iloc[:,1]
        df['ubb'] = bb.iloc[:,2]
        df['rsi'] = ta.rsi(close = df['close'], length = self.rsi_len, fillna = 0)
        
        self.dataframe = df
        
    def checkLongSignal(self, i = None):
        df = self.dataframe
        
        if i == None:
            i = len(df)
            
        if (df['rsi'].iloc[i] < self.rsi_ob) and \
           (df['rsi'].iloc[i] > self.rsi_os) and \
           (df['low'].iloc[i-1] < df['lbb'].iloc[i-1]) and \
           (df['low'].iloc[i] > df['lbb'].iloc[i]):
            
            return True
        return False
    
    def checkShortSignal(self, i = None):
        df = self.dataframe
        
        if i == None:
            i = len(df)
            
        if (df['rsi'].iloc[i] < self.rsi_ob) and \
           (df['rsi'].iloc[i] > self.rsi_os) and \
           (df['high'].iloc[i-1] > df['ubb'].iloc[i-1]) and \
           (df['high'].iloc[i] < df['ubb'].iloc[i]):
            
            return True
        return False       
              
strat = BBStrategy(20,2.0,14,60,40)
strat.setup(df)

for i in range(len(df)):
    print(f' Short Signals: {strat.checkShortSignal(i)}')
    
    print(f' Long Signals: {strat.checkLongSignal(i)}')