import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from binance.client import Client
from tensorflow import keras
from datetime import datetime
import ta
from sklearn.preprocessing import MinMaxScaler
import joblib
import warnings
from sklearn.exceptions import DataConversionWarning
warnings.filterwarnings(action='ignore', category=UserWarning)


# Conexión a la API de Binance
api_key = 'T4Bw573BSJCbaHscSo8jn37lE1SOoGsNircF8f7B061WIKBxNkP5nx68vvAev9uk'
api_secret = 'p7VN6HHKR6ZtGkfEeZC3FongJPkR2yr7AjPtPDC8IeaOkASdKZYCKyTuiIfGw57q'
client = Client(api_key, api_secret)

# Obtención de los datos históricos de precios de Bitcoin de 1 minuto
klines = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1HOUR, "1 year ago UTC")

# Conversión de los datos a un dataframe de pandas
data = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])

# Conversión de los precios a float
data['open'] = data['open'].astype(float)
data['high'] = data['high'].astype(float)
data['low'] = data['low'].astype(float)
data['close'] = data['close'].astype(float)

# Calcula los indicadores técnicos
data['momentum'] = ta.momentum.roc(data['close'], fillna=True)
data['ATR'] = ta.volatility.average_true_range(data['high'], data['low'], data['close'], fillna=True)
data['ADX'] = ta.trend.adx(data['high'], data['low'], data['close'], fillna=True)
data['MACD'] = ta.trend.macd_diff(data['close'], fillna=True)

# Carga los MinMaxScalers
scalers = {}
for column in ['open', 'high', 'low', 'close', 'momentum', 'ATR', 'ADX', 'MACD']:
    scalers[column] = joblib.load(f'scalers/{column}_scaler.gz')
    data[column] = scalers[column].transform(data[column].values.reshape(-1, 1))

# Procesamiento de los datos para la entrada del modelo
data['next_close'] = data['close'].shift(-1)
data.dropna(inplace=True)

X = np.array([data[['close', 'momentum', 'ATR', 'ADX', 'MACD']].values[i-48:i] for i in range(48, len(data))])
X = np.reshape(X, (X.shape[0], X.shape[1], X.shape[2]))

# Carga del modelo entrenado
model = keras.models.load_model('modelos de entrenamiento/btc_price_prediction_model_Indicators_copy.h5')

# Creación del archivo de resultados
resultados = pd.DataFrame(columns=['timestamp', 'actual_price', 'predicted_price'])

# Predicción del precio de Bitcoin en tiempo real
while True:

    klines = client.get_klines(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_1HOUR)[-49:-1]
    data = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])

    # Conversión de los precios a float
    data['open'] = data['open'].astype(float)
    data['high'] = data['high'].astype(float)
    data['low'] = data['low'].astype(float)
    data['close'] = data['close'].astype(float)

    # Calcula los indicadores técnicos
    data['momentum'] = ta.momentum.roc(data['close'], fillna=True)
    data['ATR'] = ta.volatility.average_true_range(data['high'], data['low'], data['close'], fillna=True)
    data['ADX'] = ta.trend.adx(data['high'], data['low'], data['close'], fillna=True)
    data['MACD'] = ta.trend.macd_diff(data['close'], fillna=True)

    # Normalización de los datos y los indicadores técnicos
    for column in ['open', 'high', 'low', 'close', 'momentum', 'ATR', 'ADX', 'MACD']:
        data[column] = scalers[column].transform(data[column].values.reshape(-1, 1))

    timestamp = data['timestamp'].values[-1]
    close_price = data['close'].values[-1]

    X = np.array([data[['close', 'momentum', 'ATR', 'ADX', 'MACD']].values[-48:]])
    X = np.reshape(X, (X.shape[0], X.shape[1], X.shape[2]))

    yhat = model.predict(X)

    predicted_price = scalers['close'].inverse_transform(yhat)[0][0]
    close_price = scalers['close'].inverse_transform(np.array(close_price).reshape(-1, 1)).item()  # Desnormalizar el precio actual

    now = datetime.now()
    print(f'{now.strftime("%Y-%m-%d %H:%M:%S")}, Actual price: {close_price:.2f}, Predicted price: {predicted_price:.2f}')

    # Agregamos los resultados al dataframe
    resultados = resultados._append({"timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),"actual_price": close_price, "predicted_price": predicted_price}, ignore_index=True)

    # Guardamos el dataframe en un archivo CSV
    resultados.to_csv("Resultados_RN_BTC_1HourInterval_13YearHistorical_100epochs_20batch_mse_adam_50LSTM_copy.csv", index=False)

    time.sleep(60*60)  # Esperamos una hora antes de realizar la predicción

