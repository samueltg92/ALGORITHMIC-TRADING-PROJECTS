import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from binance.client import Client
from tensorflow import keras
from datetime import datetime

# Conexión a la API de Binance
api_key = 'T4Bw573BSJCbaHscSo8jn37lE1SOoGsNircF8f7B061WIKBxNkP5nx68vvAev9uk'
api_secret = 'p7VN6HHKR6ZtGkfEeZC3FongJPkR2yr7AjPtPDC8IeaOkASdKZYCKyTuiIfGw57q'
client = Client(api_key, api_secret)

# Obtención de los datos históricos de precios de Bitcoin de 1 minuto
klines = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1HOUR, "13 years ago UTC") # intervalo de 15minutos a 10 años

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
data['t-24'] = data['close'].shift(24)
data.dropna(inplace=True)

X = np.array(data[['close', 't-24']])
X = np.reshape(X, (X.shape[0], X.shape[1], 1))

# Carga del modelo entrenado
model = keras.models.load_model('ruta/para/guardar/el/modelo/btc_price_prediction_model.h5')

# Creación del archivo de resultados
resultados = pd.DataFrame(columns=['timestamp', 'actual_price', 'predicted_price'])

# Predicción del precio de Bitcoin en tiempo real
while True:
    kline = client.get_klines(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_1MINUTE)[-2] #intervalo de 15minutos
    timestamp = kline[0]
    close_price = float(kline[4])

    # Normalizamos el nuevo precio de cierre
    normalized_close_price = (close_price - min_value) / (max_value - min_value)

    new_data = pd.DataFrame({'timestamp': [pd.to_datetime(timestamp, unit='ms')], 'close': [normalized_close_price]})
    new_data['t-24'] = new_data['close'].shift(24)
    new_data.dropna(inplace=True)  # Eliminamos la primera fila que ya no es necesaria
    
    data = pd.concat([data, new_data])
    
    X = np.array(data[['close', 't-24']])
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))

    yhat = model.predict(X[-1].reshape(1, X[-1].shape[0], X[-1].shape[1]))
    predicted_price = yhat[0][0] * (max_value - min_value) + min_value
    
    now = datetime.now()
    print(f'{now.strftime("%Y-%m-%d %H:%M:%S")}, Actual price: {close_price:.2f}, Predicted price: {predicted_price:.2f}')
    #print(f'Actual price: {close_price:.2f}, Predicted price: {predicted_price:.2f}')
    
    # Agregamos los resultados al dataframe
    resultados = resultados._append({"timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),"Actual Price": close_price, "Predicted Price": predicted_price}, ignore_index=True)

    # Guardamos el dataframe en un archivo CSV
    resultados.to_csv("Resultados_RN_BTC.csv", index=False)

    #time.sleep(60*60)  # Esperamos una hora antes de realizar la siguiente predicción
    #time.sleep(60*15)  # Esperamos 15min antes de realizar la siguiente predicción acá con lo de thiago
    time.sleep(60*1)  # Esperamos 1min antes de realizar la siguiente prediccións