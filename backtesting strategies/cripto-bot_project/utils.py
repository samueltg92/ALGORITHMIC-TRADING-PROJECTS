import pandas as pd

def ccxt_ohlcv_to_dataframe(ohlcv):
    """ Converts cctx ohlcv data from list of lists to dataframe. """

    df = pd.DataFrame(ohlcv)
    df.columns = ['time', 'open', 'high', 'low', 'close', 'volume']
    df['date'] = pd.to_datetime(df['time'] * 1000000, infer_datetime_format=True)

    return df

