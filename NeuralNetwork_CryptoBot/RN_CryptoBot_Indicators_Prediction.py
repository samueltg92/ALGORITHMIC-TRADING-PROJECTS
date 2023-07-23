import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error
import numpy as np
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
warnings.filterwarnings('ignore', category=RuntimeWarning)


# Conexión a la API de Binance
api_key = 'your_api_key'
api_secret = 'your_api_secret'
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

# Primero, reemplaza cualquier valor infinito en tus datos con NaN
data.replace([np.inf, -np.inf], np.nan, inplace=True)

# Ahora, reemplaza cualquier cero en tus columnas 'high', 'low' y 'close' con NaN 
# (asumiendo que los ceros no son válidos en estos contextos)
for col in ['high', 'low', 'close']:
    data[col].replace(0, np.nan, inplace=True)

# Ahora, rellena cualquier NaN en tus datos con el valor previo
data.fillna(method='ffill', inplace=True)

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
resultados = pd.DataFrame(columns=['timestamp', 'actual_price', 'predicted_price', 'MAE', 'MSE', 'RMSE', 'R2', 'MAPE'])

# Creación de listas vacías para almacenar las predicciones y los valores reales
y_true = []
y_pred = []

# Predicción del precio de Bitcoin en tiempo real
while True:

    klines = client.get_klines(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_1HOUR)[-49:-1]
    data = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])

    # Conversión de los precios a float
    data['open'] = data['open'].astype(float)
    data['high'] = data['high'].astype(float)
    data['low'] = data['low'].astype(float)
    data['close'] = data['close'].astype(float)
    
    # Primero, reemplaza cualquier valor infinito en tus datos con NaN
    data.replace([np.inf, -np.inf], np.nan, inplace=True)

    # Ahora, reemplaza cualquier cero en tus columnas 'high', 'low' y 'close' con NaN 
    # (asumiendo que los ceros no son válidos en estos contextos)
    for col in ['high', 'low', 'close']:
        data[col].replace(0, np.nan, inplace=True)

    # Ahora, rellena cualquier NaN en tus datos con el valor previo
    data.fillna(method='ffill', inplace=True)

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

    # Agrega los valores reales y las predicciones a las listas
    y_true.append(close_price)
    y_pred.append(predicted_price)

    # Calcula las métricas y las imprime
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_true, y_pred)
    mape = mean_absolute_percentage_error(y_true, y_pred)

    now = datetime.now()
    print(f'{now.strftime("%Y-%m-%d %H:%M:%S")}, Actual price: {close_price:.2f}, Predicted price: {predicted_price:.2f}, MAE: {mae:.2f}, MSE: {mse:.2f}, RMSE: {rmse:.2f}, R2: {r2:.2f}, MAPE: {mape:.2f}')

    # Agregamos los resultados al dataframe
    resultados = resultados._append({"timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),"actual_price": close_price, "predicted_price": predicted_price, "MAE": mae, "MSE": mse, "RMSE": rmse, "R2": r2, "MAPE": mape}, ignore_index=True)

    # Guardamos el dataframe en un archivo CSV
    resultados.to_csv("Resultados_RN_BTC_1HourInterval_13YearHistorical_100epochs_20batch_mse_adam_50LSTM_Indicators_metrics.csv", index=False)

    time.sleep(60*60)  # Esperamos un día antes de realizar la predicción

