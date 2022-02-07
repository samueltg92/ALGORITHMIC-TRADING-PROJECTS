import pandas as pd
from tqdm import tqdm
from binance.client import Client

client = Client() # Initialize the Client from binance

info = client.get_exchange_info() # Here I obtain all data from binance exchange
symbols = [x['symbol'] for x in info['symbols']] # here I filter only "symbols" (using List comprehension)

exclude = ['UP', 'DOWN', 'BEAR', 'BULL'] # Here is to exclude all leveraged tokens
non_lev = [symbol for symbol in symbols if all (excludes not in symbol for excludes in exclude)] # (using List comprehension)
relevant = [symbol for symbol in non_lev if symbol.endswith('USDT')] # Here is to filter all pairs that ends with "USDT" (using List comprehension)
