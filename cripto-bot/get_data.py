import ccxt
from dotenv import load_dotenv
import os

load_dotenv()
print(ccxt.exchanges)

public = os.getenv('PUBLIC1')
private = os.getenv('SECRET1')

binance = ccxt.binance({
    'apiKey': public,
    'secret': private,
    'timeout': 3000,
    'enableRateLimit': True
    })

exchange_id = 'binance'
exchange_class = getattr(ccxt, exchange_id)
exchange = exchange_class()

symbol = 'BTC/USDT'
timeframe = '1h'

binance_ohlcv = exchange.fetch_ohlcv(symbol, timeframe)


print('\nBinance Data Format: ')
print(binance_ohlcv)