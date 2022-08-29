import pandas as pd
import numpy as np
import quantstats as qsc
from BBStrategy import BBStrategy                           
import ccxt
from utils import ccxt_ohlcv_to_dataframe

exchange = ccxt.binance()
symbol = 'BTC/USDT'
timeframe = '1h'
ohlcv = exchange.fetch_ohlcv(symbol,timeframe)
df = ccxt_ohlcv_to_dataframe(ohlcv)

qs.extend_pandas()

class Backtester():
    
    def __init__(self, initial_balance = 10000, leverage = 10, trailing_sl = False, fee = 0.02, riskpct = 0.01):
        
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.amount = 0
        self.fee = fee / 100
        self.leverage = leverage
        self.trailing_sl = trailing_sl
        self.from_opened = 0
        
        self.riskpct = self.balance * riskpct * self.leverage
        
        self.pnl = []
        self.drawdown = []
        self.wins = 0
        self.losses = 0     
        self.num_trades = 0
        self.num_longs = 0
        self.num_shorts = 0
        
        self.is_long_open = False
        self.is_short_open = False
        
    def reset_results(self):
        
        self.balance = self.initial_balance
        self.amount = 0
        self.pnl = []
        self.drawdown = []
        self.wins = 0
        self.losses = 0
        self.num_trades = 0
        self.num_longs = 0
        self.num_shorts = 0
        self.is_long_open = False
        self.is_short_open = False
        self.from_opened = 0
            
    def open_position(self, price, side, from_opened = 0):
        
        self.num_trades += 1
        
        if side == 'long':
            self.num_longs += 1
            
            if self.is_long_open:
                self.long_open_price = (self.long_open_price + price) / 2
                self.amount += self.riskpct / price
            else:
                self.is_long_open = True
                self.long_open_price = price
                self.amount = self.riskpct / price
        
        elif side == 'short':
            self.num_shorts += 1
               
            if self.is_short_open:
                self.short_open_price = (self.short_open_price + price) / 2
                self.amount += self.riskpct / price
            else:
                self.is_short_open = True
                self.short_open_price = price
                self.amount = self.riskpct / price
        
        self.amount = self.riskpct / price
        
        if self.trailing_sl:
            self.from_opened = from_opened
        
            
    def close_position(self, price):
        
        self.num_trades += 1
        
        if self.is_long_open:
            result = self.amount * (self.long_open_price - price)
            self.is_long_open = False
            self.long_open_price = 0
            
        elif self.is_short_open:
            result = self.amount * (price - self.short_open_price)
            self.is_short_open = False
            self.short_open_price = 0
                
        self.pnl.append(result) # acá puedo buscar agregar la fecha en la que se generó ese PNL
        self.balance += result
        
        if result > 0:
            self.wins += 1
            self.drawdown.append(0)
        else:
            self.losses += 1
            self.drawdown.append(result)
            
        self.takeprofit_price = 0
        self.stoploss_price = 0
    
    def takeprofit(self, price, tp_long = 1.01, tp_short = 0.99):
        
        if self.is_long_open:
            self.takeprofit_price = price * tp_long
            
        elif self.is_short_open:
            self.takeprofit_price = price * tp_short
    
    def stoploss(self, price, sl_long = 0.99, sl_short = 1.01):
        
        if self.is_long_open:
            self.stoploss_price = price * sl_long
        
        elif self.is_short_open:
            self.stoploss_price = price * sl_short
    
    # def results(self, time):
        
    #     df2 = pd.DataFrame(self.pnl, index = ['time'] , columns = ['pnl'])
    #     df2['pct chng'] = df2['pnl'].pct_change()
    #     results = qs.reports.full(df2)
        
    #     return results
        
    
    def __backtesting__(self, df, strategy):
        
        high = df['high']
        close = df['close']
        low = df['low']
        
        for i in range(len(df)):
            
            if self.balance > 0:
                
                if strategy.checkLongSignal(i):
                    self.open_position(price = close[i], side = 'long', from_opened = i)
                    self.takeprofit(price = close[i], tp_long = 1.03)
                    self.stoploss(price = close[i], sl_long = 0.99)
                elif strategy.checkShortSignal(i):
                    self.open_position(price = close[i], side = 'short', from_opened = i)
                    self.takeprofit(price = close[i], tp_short = 0.97)
                    self.stoploss(price = close[i], sl_short = 1.01)     
                
                else:
                    if self.trailing_sl and (self.is_long_open or self.is_short_open):
                        new_max = high[self.from_opened : i].max()
                        previous_sl = self.stoploss_price                        
                        self.stoploss(price = new_max)
                        
                        if previous_sl > self.stoploss_price:
                            self.stoploss_price = previous_sl
                            
                    if self.is_long_open:
                        if high[i] >= self.takeprofit_price:
                            self.close_position(price = self.takeprofit_price)    
                        elif low[i] <= self.stoploss_price:
                            self.close_position(price = self.stoploss_price)       
                            
                    elif self.is_short_open:
                        if high[i] >= self.stoploss_price:
                            self.close_position(price = self.stoploss_price)
                        elif low[i] <= self.takeprofit_price:
                            self.close_position(price = self.takeprofit_price)    
                            


strategy = BBStrategy()
strategy.setup(df)

tryback = Backtester()
tryback.__backtesting__(df, strategy)
# print(tryback.results())


# para ver los reusltados debo crear un dict con las fechas donde se hicieron los profits 
# y con los profits, luego hacer un dataframe con ese dict y luego aplicarle un pct_change
# a la columna 'pnl' para luego aplicar la función de quantstats.

# la otra forma es ver en que punto puedo poner la lista de 'pnl' y convertirla a dataframe
# para luego poner como indice las fechas en las que se produjo ese profit and loss.
# luego aplicarle la función de quantstats. 