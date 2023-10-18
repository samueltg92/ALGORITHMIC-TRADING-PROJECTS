import backtrader as bt
import yfinance as yf
from strategy import BuyAndHoldStrategy
import backtrader.analyzers as btanalyzers

cerebro = bt.Cerebro()

# Lista de activos y pesos
assets = {
    "AAPL": 0.4,
    "GOOGL": 0.3,
    "MSFT": 0.3}

# Descargar datos y agregarlos al cerebro
for asset, weight in assets.items():
    data = yf.download(tickers=asset, start="2010-01-01", end="2023-10-12")
    data = bt.feeds.PandasData(dataname=data)
    cerebro.adddata(data, name=asset)  # Asignar un nombre al activo

# Pasar los pesos como parámetro al agregar la estrategia
cerebro.addstrategy(BuyAndHoldStrategy, weights=assets)
cerebro.broker.set_cash(100.0)

# Analyzer
cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='mysharpe')
cerebro.addanalyzer(btanalyzers.DrawDown, _name='mydd')
cerebro.addanalyzer(btanalyzers.AnnualReturn, _name='myar')

thestrats = cerebro.run()
thestrat = thestrats[0]

print('Sharpe Ratio:', thestrat.analyzers.mysharpe.get_analysis())
print('Drawdown:', thestrat.analyzers.mydd.get_analysis())
print('Annual Return:', thestrat.analyzers.myar.get_analysis())

get_value = cerebro.broker.getvalue()
print(f'Final value: {get_value}')
