import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

"""
    Market: S&P 500
    Define trend: price above 200-day MA
    Entry: 10-period RSI below 30 (buy on next day's open)
    Exit: 10-period RSI above 40 or after 10 trading days (sell on next day's open)
"""

