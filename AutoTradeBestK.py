import time
import pyupbit
import datetime
import pandas as pd
import numpy as np


import datetime

btc_current=pyupbit.get_current_price("KRW-BTC")
xrp_current=pyupbit.get_current_price("KRW-XRP")



class PARAMS:
  prev_ror=0



access = "xfNbCKU7lTuQ4Nupl6P7vBBd4yirECKhmnR6OTm7"
secret = "fMdyg4n7tN6OJa2rUL1wC2wZ7T6Z4okruX9kxKDh"

bestk=0.1

def get_ror(k=0.5):
    df = pyupbit.get_ohlcv("KRW-BTC", count=30)
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)


    df['ror'] = np.where(df['high'] > df['target'],
                         df['close'] / df['target'],
                         1)

    ror = df['ror'].cumprod()[-2]
    
    return ror



 

n=0


for k in np.arange(0.1, 1.0, 0.1):
    
    ror = get_ror(k)
    
    if PARAMS.prev_ror is not 0:
      if PARAMS.prev_ror < ror:
        bestk=k

    
    PARAMS.prev_ror=ror
 
    n+=1
    print("%.1f %f" % (k, ror))

    
  
def get_target_price(ticker, bestk):
    
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * bestk
    return target_price

def get_start_time(ticker):
  
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
   
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):

    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]


upbit = pyupbit.Upbit(access, secret)
print("autotrade start")


while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price("KRW-BTC", bestk)
            current_price = get_current_price("KRW-BTC")
            if target_price < current_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    upbit.buy_market_order("KRW-BTC", krw*0.9995)
        else:
            btc = get_balance("BTC")
            if btc > 0.0002:
                upbit.sell_market_order("KRW-BTC", btc*0.9995)
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)  
