import ccxt
import pandas as pd
import pandas_ta as ta
from data_processing import ccxt_ohlcv_to_dataframe

## Llamo a los datos desde binance y creo el dataframe
exchange = ccxt.binance()
symbol = 'BTC/USDT'
timeframe = '1h'
ohlcv = exchange.fetch_ohlcv(symbol,timeframe)
df = ccxt_ohlcv_to_dataframe(ohlcv)
close = df['close']

## Creo una variable SMA con el cálculo de ella 
sma = ta.sma(close, length=21)
print(sma)

## Aplico la SMA de TA directamente al df
df.ta.sma(length=21, append = True, fillna=0)
print(df)

## Definir cuantos núcleos de procesamiento voy a usar
df.ta.cores = 5

## Creo una estrategia de cruce de emas
emastrat = ta.Strategy(
    name = 'emacross',
    ta = [
        {'kind': 'ema', 'length': 9, 'fillna': 0},
        {'kind': 'ema', 'length': 35, 'fillna': 0}
          ]
)

df.ta.strategy(emastrat)
print(df)