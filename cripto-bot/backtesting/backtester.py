import pandas as pd
import numpy as np


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
        
            
    def close_position(self):
        pass
    
    def takeprofit(self):
        pass
    
    def stoploss(self):
        pass
    
    def results(self):
        pass 