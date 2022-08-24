import pandas as pd
import numpy as np


class Backtester():
    
    def __init__(self, initial_balance = 10000, leverage = 10, trailing_sl = False, fee = 0.02, riskpct = 1):
        
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
        
    
    def open_position(self):
        pass
    
    def close_position(self):
        pass
    
    def takeprofit(self):
        pass
    
    def stoploss(self):
        pass
    
    def results(self):
        pass 