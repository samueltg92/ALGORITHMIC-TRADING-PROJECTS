import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from binance.client import Client
from tensorflow import keras
from datetime import datetime
import ta
from sklearn.preprocessing import MinMaxScaler

# Conexión a la API de Binance
api_key = 'T4Bw573BSJCbaHscSo8jn37lE1SOoGsNircF8f7B061WIKBxNkP5nx68vvAev9uk'
api_secret = 'p7VN6HHKR6ZtGkfEeZC3FongJPkR2yr7AjPtPDC8IeaOkASdKZYCKyTuiIfGw57q'
client = Client(api_key, api_secret)

# Obtención de los datos históricos de precios de Bitcoin de 1 minuto
klines = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1HOUR, "13 years ago UTC")

# Conversión de los datos a un dataframe de pandas
data = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
data = data[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
data.set_index('timestamp', inplace=True)
data['close'] = pd.to_numeric(data['close'], errors='coerce')

data['open'] = pd.to_numeric(data['open'], errors='coerce')
data['high'] = pd.to_numeric(data['high'], errors='coerce')
data['low'] = pd.to_numeric(data['low'], errors='coerce')
data['close'] = pd.to_numeric(data['close'], errors='coerce')
data['volume'] = pd.to_numeric(data['volume'], errors='coerce')

window_size = 14

if len(data) > window_size:
    data['ATR'] = ta.volatility.AverageTrueRange(data['high'], data['low'], data['close'], window=window_size).average_true_range()
else:
    print(f"window_size is too large. Must be less than {len(data)}")

# Calculamos los indicadores técnicos
data['RSI'] = ta.momentum.RSIIndicator(data['close']).rsi()
data['MACD'] = ta.trend.MACD(data['close']).macd_diff()
data['EMA_100'] = ta.trend.EMAIndicator(data['close'], 100).ema_indicator()
data['EMA_200'] = ta.trend.EMAIndicator(data['close'], 200).ema_indicator()
#data['ADX'] = ta.trend.ADXIndicator(data['high'], data['low'], data['close'], window=window_size).adx()
data['ATR'] = ta.volatility.AverageTrueRange(data['high'], data['low'], data['close']).average_true_range()
data['Momentum'] = ta.momentum.AwesomeOscillatorIndicator(data['high'], data['low']).awesome_oscillator()

# Normalizador
scaler = MinMaxScaler()
scaler.fit(data)  # Ajustamos el scaler a los datos

# Carga del modelo entrenado
model = keras.models.load_model('modelos de entrenamiento/btc_price_prediction_model_indicators.h5')

# Creación del archivo de resultados
resultados = pd.DataFrame(columns=['timestamp', 'actual_price', 'predicted_price'])

# Predicción del precio de Bitcoin en tiempo real
data = pd.DataFrame()
N = 200  # Mantén los últimos 200 períodos de datos

while True:
    kline = client.get_klines(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_1HOUR)[-2]
    timestamp = kline[0]
    close_price = float(kline[4])
    high_price = float(kline[2])
    low_price = float(kline[3])
    volume = float(kline[5])

    # Añadimos los datos actuales al dataframe
    new_data = pd.DataFrame({'timestamp': [pd.to_datetime(timestamp, unit='ms')], 'high': [high_price], 'low': [low_price], 'close': [close_price], 'volume': [volume]})
    data = pd.concat([data, new_data])

    # Mantén solo los últimos N períodos de datos
    data = data.tail(N)


    window_size = 14

    if len(data) > window_size:
        data['ATR'] = ta.volatility.AverageTrueRange(data['high'], data['low'], data['close'], window=window_size).average_true_range()
    else:
        print(f"window_size is too large. Must be less than {len(data)}")

    # Calculamos los indicadores técnicos
    data['RSI'] = ta.momentum.RSIIndicator(data['close']).rsi()
    data['MACD'] = ta.trend.MACD(data['close']).macd_diff()
    data['EMA_100'] = ta.trend.EMAIndicator(data['close'], 100).ema_indicator()
    data['EMA_200'] = ta.trend.EMAIndicator(data['close'], 200).ema_indicator()
    #data['ADX'] = ta.trend.ADXIndicator(data['high'], data['low'], data['close'], window=window_size).adx()
    data['ATR'] = ta.volatility.AverageTrueRange(data['high'], data['low'], data['close']).average_true_range()
    data['Momentum'] = ta.momentum.AwesomeOscillatorIndicator(data['high'], data['low']).awesome_oscillator()
    data['Volume'] = data['volume']

    # Normalización de los datos
    data_normalized = pd.DataFrame(scaler.transform(data[['high', 'low', 'close', 'volume', 'RSI', 'MACD', 'EMA_100', 'EMA_200', 'Momentum', 'ADX', 'ATR', 'open']]), columns=['high', 'low', 'close', 'volume', 'RSI', 'MACD', 'EMA_100', 'EMA_200', 'Momentum', 'ADX', 'ATR', 'open'])

    # Procesamiento de los datos para la entrada del modelo
    X = np.array(data_normalized[['close', 'RSI', 'MACD', 'EMA_100', 'EMA_200', 'Momentum', 'Volume']])
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))

    # Predicción del precio
    yhat = model.predict(X[-1].reshape(1, X[-1].shape[0], X[-1].shape[1]))
    predicted_price = yhat[0][0] 
    
    now = datetime.now()
    print(f'{now.strftime("%Y-%m-%d %H:%M:%S")}, Actual price: {close_price:.2f}, Predicted price: {predicted_price:.2f}')
    
    # Agregamos los resultados al dataframe
    resultados = resultados.append({"timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),"actual_price": close_price, "predicted_price": predicted_price}, ignore_index=True)

    # Guardamos el dataframe en un archivo CSV
    resultados.to_csv("Resultados_RN_BTC_1HourInterval_13YearHistorical_200epochs_32batch_mse_adam_100LSTM_Indicators.csv", index=False)

    # Esperamos 1 minuto antes de realizar la siguiente predicción
    time.sleep(60)