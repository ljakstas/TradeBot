from pandas.core.indexes.multi import maybe_droplevels
import requests, json
from config import *
import alpaca_trade_api as tradeapi
import pandas as pd

APCA_API_BASE_URL= "https://paper-api.alpaca.markets"
ACCOUNT_URL = "{}/v2/account".format(APCA_API_BASE_URL)
ORDERS_URL = "{}/v2/orders".format(APCA_API_BASE_URL)

APCA_API_KEY_ID = os.getenv('APCA_API_KEY_ID')
APCA_API_SECRET_KEY = os.getenv('APCA_API_SECRET_KEY')

HEADERS = {'APCA-API-KEY-ID': APCA_API_KEY_ID, 'APCA-API-SECRET-KEY': APCA_API_SECRET_KEY}

api = tradeapi.REST(api_version='v2')

#class Candle:


def get_account():
    r = requests.get(ACCOUNT_URL, headers = HEADERS)

    return json.loads(r.content)

def create_order(symbol, qty, side, type, time_in_force):
    data = {
        "symbol": symbol,
        "qty": qty, 
        "side": side, 
        "type": type, 
        "time_in_force": time_in_force, 
    }

    r = requests.post(ORDERS_URL, json= data, headers= HEADERS)

    return json.loads(r.content)

def get_orders():
    r = requests.get(ORDERS_URL, headers = HEADERS)

    return json.loads(r.content)

orders = get_orders()
#print(orders)

def get_candles(symbol, limit_days):
    # Get daily price data for AAPL over the last 5 trading days.
    barset = api.get_barset(symbol, 'day', limit=limit_days)
    candle_data = barset[symbol]

    df = barset.df
    #print(df,"\n-------------------")

    newDF =df[("AAPL","close")]

    high_close_val = newDF.max()
    max_close_day = newDF.idxmax() #find associated time/date with high_close_val
    max_close_day = str(max_close_day).split(' ', 1)[0] #extract date

    #print("max close is $%s on %s" % (high_close_val, max_close_day))
    
    return candle_data['AAPL']

def get_close_candles(symbol, days):
    # Get daily price data for AAPL over the last 5 trading days.
    barset = api.get_barset(symbol, 'day', limit=days)

    df = barset.df

    newDF =df[("AAPL","close")]
    col_one_list = newDF.tolist()
    
    return col_one_list

def moving_average(bars, length):
    sum = 0
    for i in range(length):
        sum += bars[i].c
    return float("{:.2f}".format(sum / length))


def get_moving_avg_arr(symbol, numDayAvg, arrLength):
    MOVING_AVG_ARR = []
    for i in range(arrLength): #desired len
        barset = api.get_barset(symbol, 'day', limit=(arrLength + numDayAvg)-(i+1)) #arrlen+moving day avg - (i+1)
        bb = barset[symbol]
        n = moving_average(bb, numDayAvg) #moving day avg
        MOVING_AVG_ARR.append(n)
    
    return MOVING_AVG_ARR



avg10arr = get_moving_avg_arr('AAPL', 10, 50)
print(avg10arr[-1])


#bars = get_close_candles('AAPL',50)
#newDF =df[("AAPL","close")]
#print(bars)
#arr50 = get_moving_avg_arr(50, 100)
#arr10 = get_moving_avg_arr(10, 100)
#for i in range(50):
#    print(float("{:.2f}".format(arr50[i]-arr10[i])))

#response = create_order("AAPL", 100, "buy", "market", "gtc")
#response = create_order("DRN", 1, "buy", "market", "gtc")