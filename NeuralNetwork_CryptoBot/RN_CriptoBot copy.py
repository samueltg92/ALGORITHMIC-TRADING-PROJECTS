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
data['next_close'] = data['close'].shift(-1)  # Cambio importante: usamos el próximo cierre como objetivo
data.dropna(inplace=True)

X = np.array([data['close'].values[i-48:i] for i in range(48, len(data))])  # Cambio importante: creamos secuencias de 48 pasos
X = np.reshape(X, (X.shape[0], X.shape[1], 1))

# Carga del modelo entrenado
model = keras.models.load_model('modelos de entrenamiento/btc_price_prediction_model_copy.h5')

# Creación del archivo de resultados
resultados = pd.DataFrame(columns=['timestamp', 'actual_price', 'predicted_price'])

# Predicción del precio de Bitcoin en tiempo real
while True:
    kline = client.get_klines(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_1HOUR)[-49:-1]  # Cambio importante: obtenemos los últimos 48 cierres
    timestamp = kline[-1][0]
    close_price = float(kline[-1][4])
    
    # Normalizamos el nuevo precio de cierre
    normalized_close_price = [(float(k[4]) - min_value) / (max_value - min_value) for k in kline]
    
    new_data = np.array(normalized_close_price).reshape(1, 48, 1)  # Cambio importante: creamos una secuencia de 48 pasos
    
    yhat = model.predict(new_data)

    predicted_price = yhat[0][0] * (max_value - min_value) + min_value

    now = datetime.now()
    print(f'{now.strftime("%Y-%m-%d %H:%M:%S")}, Actual price: {close_price:.2f}, Predicted price: {predicted_price:.2f}')
    #print(f'Actual price: {close_price:.2f}, Predicted price: {predicted_price:.2f}')

    # Agregamos los resultados al dataframe
    resultados = resultados._append({"timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),"actual_price": close_price, "predicted_price": predicted_price}, ignore_index=True)

    # Guardamos el dataframe en un archivo CSV
    resultados.to_csv("Resultados_RN_BTC_1HourInterval_13YearHistorical_100epochs_20batch_mse_adam_50LSTM_copy.csv", index=False)

    time.sleep(60*60)  # Esperamos una hora antes de realizar la siguiente predicción