from binance.client import Client
import ccxt
import pandas as pd
from datetime import datetime
import openpyxl
from dotenv import load_dotenv
import os

register1 = pd.read_excel('Registro_de_operaciones_Binance_Noviembre2022.xlsx',index_col='datetime', sheet_name = 'SamuelTM')

load_dotenv()

publicsam = os.getenv('PUBLIC1')
privatesam = os.getenv('SECRET1')


def register_balance(API_KEY, PRIVATE_KEY):
      
    binance = ccxt.binanceusdm({
        'apiKey': API_KEY,
        'secret': PRIVATE_KEY,
        'verbose': False,
    })
    

    balance_free = binance.fetch_balance().get('USDT').get('free')
    balance_used = binance.fetch_balance().get('USDT').get('used')

    total = balance_free + balance_used
    pair = binance.fetch_balance()

    for x,y in pair.items():
        if x == 'total':              
            for x,pair in y.items():
                if x == 'USDT':    
                    df = pd.DataFrame({
                        'Paridad': x,
                        'Balance': total},index=[1])
                    df['datetime'] = datetime.today().strftime('%Y-%m-%d')
                    df = df.set_index('datetime')
                    print(df)
    return df

if __name__ == '__main__':

    df1 = register_balance(publicsam, 
                     privatesam,
                     )
    



    df4 = pd.concat([register1, df1])
    
  
writer = pd.ExcelWriter('Registro_de_operaciones_Binance_Noviembre2022.xlsx', mode = 'a', if_sheet_exists = 'overlay', engine = 'openpyxl')
df4.to_excel(writer, sheet_name = 'SamuelTM',)


writer.save()