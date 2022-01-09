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

#response = create_order("AAPL", 100, "buy", "market", "gtc")
#response = create_order("DRN", 1, "buy", "market", "gtc")

orders = get_orders()
#print(orders)

def get_candles(symbol):
    # Get daily price data for AAPL over the last 5 trading days.
    barset = api.get_barset(symbol, 'day', limit=5)
    candle_data = barset[symbol]

    df = barset.df
    #print(df,"\n-------------------")

    newDF =df[("AAPL","close")]

    high_close_val = newDF.max()
    max_close_day = newDF.idxmax() #find associated time/date with high_close_val
    max_close_day = str(max_close_day).split(' ', 1)[0] #extract date

    #print("max close is $%s on %s" % (high_close_val, max_close_day))
    
    return candle_data

def get_close_candles(symbol, days):
    # Get daily price data for AAPL over the last 5 trading days.
    barset = api.get_barset(symbol, 'day', limit=days)
    candle_data = barset[symbol]

    df = barset.df

    newDF =df[("AAPL","close")]

    col_one_list = newDF.tolist()
    
    return col_one_list

def moving_average(bars, length):
    sum = 0
    for i in range(length):
        sum += bars[i]
    return sum / length

MOVING_TEN_AVG = []
MOVING_FIFTY_AVG = []
for i in range(50):
    bars_ten = get_close_candles('AAPL', 50-i)
    n = float("{:.2f}".format(moving_average(bars_ten, 10)))
    MOVING_TEN_AVG.append(n)

for i in range(50):
    bars_fifty = get_close_candles('AAPL', 100-i)
    n = float("{:.2f}".format(moving_average(bars_fifty, 50)))
    MOVING_FIFTY_AVG.append(n)
    
#for i in range(50):
#    abs(MOVING_TEN_AVG[i] - MOVING_FIFTY_AVG[i])

bars_ten = get_close_candles('AAPL', 10)
ten_day_avg = moving_average(bars_ten, len(bars_ten))

bars_fifty = get_close_candles('AAPL', 50)
fifty_day_avg = moving_average(bars_fifty, len(bars_fifty))

print(ten_day_avg)
#print(fifty_day_avg)