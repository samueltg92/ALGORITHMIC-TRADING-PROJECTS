import ccxt

print(ccxt.exchanges)

binance = ccxt.binance({
    'apiKey': 'public key',
    'secret': 'secret key',
    'timeout': 3000,
    'enableRateLimit': True
})

exchange_id = 'binance'
exchange_class = getattr(ccxt, exchange_id)
exchange = exchange_class

symbol = 'BTC/USDT'
timeframe = '1h'

binance_ohlcv = exchange.fetch_ohlcv(symbol, timeframe)


print('\nBinance Data Format: ')
print(binance_ohlcv)