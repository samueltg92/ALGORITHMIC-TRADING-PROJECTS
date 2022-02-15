import pandas as pd
from tqdm import tqdm
from binance.client import Client

client = Client() # Initialize the Client from binance

info = client.get_exchange_info() # Here I obtain all data from binance exchange
symbols = [x['symbol'] for x in info['symbols']] # here I filter only "symbols" (using List comprehension)

exclude = ['UP', 'DOWN', 'BEAR', 'BULL'] # Here is to exclude all leveraged tokens
non_lev = [symbol for symbol in symbols if all (excludes not in symbol for excludes in exclude)] # (using List comprehension)
relevant = [symbol for symbol in non_lev if symbol.endswith('USDT')] # Here is to filter all pairs that ends with "USDT" (using List comprehension)

klines = {} # Empty dictionary where it will fill with the kline data
for symbol in tqdm(relevant): # a for loop, looping throught the "relevant" data using "tqdm" to get a progress bar
    klines[symbol] = client.get_historical_klines(symbol, '1m', '1 hour ago UTC') # creating the keys for all symbols using the info from binance. I provide the symbol, the interval and how much time i wanna go back
    
returns, symbols = [], [] # Get returns for all symbols appending thats info into both dictionaries

for symbol in relevant: # a loop through al the "relevant" symbols with USDT
    
    if len(klines[symbol]) > 0: # Going to check and exclude symbols with no entries ("returns")
        
        cumreturn = (pd.DataFrame(klines[symbol])[4].astype(float).pct_change() +1).prod() -1 # Here I define the cumulative return creating a data frame for each iteration, indexing for the 4th column, converting to a float value
        returns.append(cumreturn*100) # append the "cumreturn" values to "returns" dictionary
        symbols.append(symbol) # append the "symbol" values (symbols) to the symbols dictionary
        
returndf = pd.DataFrame(returns, index=symbols, columns=['ret']) # Creating a variable to store the returns organized

print(returndf.ret.nlargest(int(input('How many cryptos do you want to watch?: '))))