import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from binance.client import Client
from tensorflow import keras

# Conexión a la API de Binance
api_key = 'T4Bw573BSJCbaHscSo8jn37lE1SOoGsNircF8f7B061WIKBxNkP5nx68vvAev9uk'
api_secret = 'p7VN6HHKR6ZtGkfEeZC3FongJPkR2yr7AjPtPDC8IeaOkASdKZYCKyTuiIfGw57q'
client = Client(api_key, api_secret)

# Obtención de los datos históricos de precios de Bitcoin de 1 minuto
klines = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1MINUTE, "10 years ago UTC")

# Conversión de los datos a un dataframe de pandas
data = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
data = data[['timestamp', 'close']]
data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
data.set_index('timestamp', inplace=True)
data['close'] = pd.to_numeric(data['close'], errors='coerce')

# Normalización de los datos
max_value = data['close'].max()
min_value = data['close'].min()
data['close'] = (data['close'] - min_value) / (max_value - min_value)

# Procesamiento de los datos para la entrada del modelo
data['t-1'] = data['close'].shift(1)
data.dropna(inplace=True)

X = np.array(data[['close', 't-1']])
X = np.reshape(X, (X.shape[0], X.shape[1], 1))

# Carga del modelo entrenado
model = keras.models.load_model('ruta/para/guardar/el/modelo/btc_price_prediction_model.h5')

# Predicción del precio de Bitcoin en tiempo real
while True:
    kline = client.get_klines(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_1HOUR)[-2]
    timestamp = kline[0]
    close_price = float(kline[4])

    data = data.append({'timestamp': pd.to_datetime(timestamp, unit='ms'), 'close': close_price}, ignore_index=True)
    data['close'] = (data['close'] - min_value) / (max_value - min_value)
    data['t-1'] = data['close'].shift(1)
    data.dropna(inplace=True)  # Eliminamos la primera fila que ya no es necesaria
    X = np.array(data[['close', 't-1']])
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))

    yhat = model.predict(X[-1].reshape(1, X[-1].shape[0], X[-1].shape[1]))
    predicted_price = yhat[0][0] * (max_value - min_value) + min_value

    print(f'Actual price: {close_price:.2f}, Predicted price: {predicted_price:.2f}')
    #time.sleep(60*60)  # Esperamos una hora antes de realizar la siguiente predicción
    #time.sleep(60*15)  # Esperamos 15min antes de realizar la siguiente predicción
    time.sleep(60*1)  # Esperamos 1min antes de realizar la siguiente predicción