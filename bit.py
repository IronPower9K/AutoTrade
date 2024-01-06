import pandas as pd
from prophet import Prophet
import pyupbit
import plotly.graph_objects as plt
import datetime
from dateutil.relativedelta import relativedelta
from PIL import Image
import time

# Set Upbit API key and secret (replace with your own key and secret)
upbit_access_key = "WN9wHM9q8Q7Bm630wASI9wXyK9E2XPpKw0GdVIbO"
upbit_secret_key = "lJWaIvgDHnSdRGEH8t0WhmAQtBiVgI1vHx0fkadc"
upbit = pyupbit.Upbit(upbit_access_key, upbit_secret_key)

dt_now = datetime.datetime.now()
dt_past1 = dt_now - relativedelta(weeks=1)

def bit_pre():
    dt_now = datetime.datetime.now()
    option = 'KRW-BTC'
    

    # Fetch historical price data from Upbit
    data = pyupbit.get_ohlcv(option, interval='minute60', count=50000)


    data = data[["open"]] # data의 값 중 open값만 data에 다시 저장
    print(data)

    data = data.reset_index() # data의 인덱스 초기화

    data.columns = ["ds", "y"] # data의 열을 ds , y로 저장

    data['ds'] = pd.to_datetime(data['ds'],format='%y-%m-%d') #data의 ds값을 pandas에 호환되는 날짜의 값으로 변환

    dt_now = pd.to_datetime(dt_now) # dt_now를 pandas에 호환이 되는 값으로 변환

    data.index = data['ds']  # data의 인덱스에 ds값을 삽입
    data.set_index('ds', inplace=True) # 그 ds값을 data의 인덱스로 선언 (날짜로 그 날짜에 해당하는 y값을 쉽게 추출하기 위함)



    data = data.reset_index() # data의 인덱스 초기화

    data.columns = ['ds', 'y']# data의 열을 ds , y로 저장

    data_prophet = Prophet(changepoint_prior_scale=0.15, daily_seasonality=True)
    data_prophet.fit(data)

    fcast_time = 1000
    data_forecast = data_prophet.make_future_dataframe(periods=fcast_time,freq='H')
    data_forecast = data_prophet.predict(data_forecast)

    # Find the index of the minimum and maximum values of 'y' in the forecast data
    min_index = data_forecast[data_forecast.index > 50000]['yhat'].idxmin()
    max_index = data_forecast[data_forecast.index > 50000]['yhat'].idxmax()


    # Get the corresponding 'ds' and 'y' values
    min_ds = data_forecast.loc[min_index, 'ds']
    min_y = data_forecast.loc[min_index, 'yhat']

    max_ds = data_forecast.loc[max_index, 'ds']
    max_y = data_forecast.loc[max_index, 'yhat']

    # Print the results
    print(f"Minimum value at {min_ds}: {min_y}")
    print(f"Maximum value at {max_ds}: {max_y}")
     

    fig = plt.Figure()
    fig.add_trace(plt.Scatter(x=data['ds'], y=data['y'], name='실제값'))
    fig.add_trace(plt.Scatter(x=data_forecast['ds'], y=data_forecast['yhat'], name='예측값'))

    print(data_forecast)
    fig.update_layout(title=f"비트코인",
                        xaxis_title='년도',
                        yaxis_title='비트코인 가격',
                        template='plotly_white')

    fig.show()

    return min_ds, min_y, max_ds, max_y


def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]



upbit = pyupbit.Upbit(upbit_access_key, upbit_secret_key)
print("autotrade start")
min_ds, min_y, max_ds, max_y = bit_pre()

while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)
        current_price = get_current_price("KRW-BTC")
        btc_sell = 5000 / current_price

        
        if (get_balance("BTC") != 0) and (current_price >= max_y):
            btc = get_balance("BTC")
            if btc > btc_sell:
                upbit.sell_market_order("KRW-BTC", btc*0.9995)
        
        elif start_time < now < min_ds + datetime.timedelta(hours=10):
            #target_price = get_target_price("KRW-BTC", 0.5)
            
            if current_price <= min_y:
                krw = get_balance("KRW")
                if krw > 5000:
                    upbit.buy_market_order("KRW-BTC", krw*0.9995)

        else:
            min_ds, min_y, max_ds, max_y = bit_pre()
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)    
    
        