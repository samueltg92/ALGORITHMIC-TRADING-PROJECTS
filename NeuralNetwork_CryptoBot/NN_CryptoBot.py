import tensorflow as tf
from tensorflow import keras
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from binance.client import Client

# Autenticación en la API de Binance
api_key = 'T4Bw573BSJCbaHscSo8jn37lE1SOoGsNircF8f7B061WIKBxNkP5nx68vvAev9uk'
api_secret = 'p7VN6HHKR6ZtGkfEeZC3FongJPkR2yr7AjPtPDC8IeaOkASdKZYCKyTuiIfGw57q'
client = Client(api_key, api_secret)

# Obtención de los datos históricos de precios de Bitcoin
klines = client.futures_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1HOUR, "1 year ago UTC")

# Creación de un dataframe con los datos
data = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])

# Eliminación de las columnas que no se van a utilizar
data = data.drop(['timestamp', 'high', 'low', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'], axis=1)

# Conversión de los precios a float
data['open'] = data['open'].astype(float)
data['close'] = data['close'].astype(float)

# Normalización de los datos
max_value = data['open'].max()
min_value = data['open'].min()
data['open'] = (data['open'] - min_value) / (max_value - min_value)
max_value = data['close'].max()
min_value = data['close'].min()
data['close'] = (data['close'] - min_value) / (max_value - min_value)

# Creación de la función para crear el conjunto de datos para el modelo
def create_dataset(data, look_back=1):
    dataX, dataY = [], []
    for i in range(len(data)-look_back-1):
        a = data[i:(i+look_back), :]
        dataX.append(a)
        dataY.append(data[i + look_back, 1])
    return np.array(dataX), np.array(dataY)

# Creación del conjunto de datos
look_back = 60
train_size = int(len(data) * 0.8)
test_size = len(data) - train_size
train, test = data.iloc[0:train_size,:], data.iloc[train_size:len(data),:]
trainX, trainY = create_dataset(train.values, look_back)
testX, testY = create_dataset(test.values, look_back)

# Creación del modelo de redes neuronales
model = keras.Sequential()
model.add(keras.layers.LSTM(units=50, return_sequences=True, input_shape=(trainX.shape[1], 2)))
model.add(keras.layers.Dropout(0.2))
model.add(keras.layers.LSTM(units=50, return_sequences=True))
model.add(keras.layers.Dropout(0.2))
model.add(keras.layers.LSTM(units=50))
model.add(keras.layers.Dropout(0.2))
model.add(keras.layers.Dense(units=1))

# Compilación del modelo
model.compile(loss='mean_squared_error', optimizer='adam')

# Entrenamiento del modelo
model.fit(trainX, trainY, epochs=50, batch_size=72, validation_data=(testX, testY), verbose=2)

# Evaluación del modelo
trainPredict = model.predict(trainX)
testPredict = model.predict(testX)
trainPredict = trainPredict.reshape(-1)
testPredict = testPredict.reshape(-1)

# Desnormalización de los datos
trainPredict = trainPredict * (max_value - min_value) + min_value
trainY = trainY * (max_value - min_value) + min_value
testPredict = testPredict * (max_value - min_value) + min_value
testY = testY * (max_value - min_value) + min_value

# Visualización de los resultados
plt.figure(figsize=(20,10))
plt.plot(trainY, color='blue', label='Actual price')
plt.plot(trainPredict, color='red', label='Predicted price')
plt.legend()
plt.show()

plt.figure(figsize=(20,10))
plt.plot(testY, color='blue', label='Actual price')
plt.plot(testPredict, color='red', label='Predicted price')
plt.legend()
plt.show()
