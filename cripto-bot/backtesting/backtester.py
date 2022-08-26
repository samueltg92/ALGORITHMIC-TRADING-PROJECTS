import pandas as pd
import numpy as np
import quantstats as qs

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
        self.wins = []
        self.losses = []
        
        self.num_trades = 0
        self.num_longs = 0
        self.num_shorts = 0
        
        self.is_long_open = False
        self.is_short_open = False
        
    
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
        
        # self.amount = self.riskpct / price
        
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
                
        self.pnl.append(result)
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
    
    def results(self, symbol, start_date, end_date):
        pass 