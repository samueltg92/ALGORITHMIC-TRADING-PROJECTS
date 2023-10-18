import backtrader as bt

class BuyAndHoldStrategy(bt.Strategy):
    params = (
        ("initial_cash", 10000.0),  # Capital inicial
        ("weights", None),        # Parámetro para los pesos de activos
    )

    def __init__(self):
        self.start_cash = self.params.initial_cash
        self.cash = self.params.initial_cash

    def nextstart(self):
        # Calcular el peso para cada activo en la cartera
        weights = self.params.weights

        for data in self.datas:
            asset_name = data._name
            weight = weights.get(asset_name, 0.0) # Obtener el peso del activo de la cartera (0.0 si no existe)
            size = (self.cash * weight) / data.open
            self.buy(data=data, size=size)

    def stop(self):
        # Calcular el rendimiento final
        final_value = self.broker.get_value()
        profit = final_value - self.start_cash
        print(f"Rendimiento final: {profit:.2f} ({(profit/self.start_cash)*100:.2f}%)")
 