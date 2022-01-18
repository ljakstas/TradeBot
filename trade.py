from pandas.core.indexes.multi import maybe_droplevels
import requests, json
from config import *
import alpaca_trade_api as tradeapi
import pandas as pd
from datetime import datetime
from pytz import timezone


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


def get_moving_avg_arr(symbol, numDayAvg, arrLength, timespan):
    MOVING_AVG_ARR = []
    for i in range(arrLength): #desired len
        barset = api.get_barset(symbol, timespan, limit=(arrLength + numDayAvg)-(i+1)) #arrlen+moving day avg - (i+1)
        bb = barset[symbol]
        n = moving_average(bb, numDayAvg) #moving day avg
        MOVING_AVG_ARR.append(n)
    
    return MOVING_AVG_ARR

def decide_todays_candles(symbol, array_length):
    #assume 30 min (2*15?)
    #-if goes well, lookn at closer??????

    #tz = timezone('EST')
    #full=str(((str(datetime.now(tz)).split(' ', 5)[1]).split('-', 5)[0]))[0:5]
    #curr_hr = int(full[0:2])
    #print(curr_hr, end = " ")
    #curr_min = int(full[3:5])
    
    open_hr = 9
    open_min =30
    close_hr = 15
    close_min = 60

    #print(open_hr)
    #print(curr_hr - open_hr)
    #print(curr_min, end = " ")
    #print(open_min)
    #print(open_min - curr_min)

    barset = api.get_barset(symbol, '15Min', limit=array_length)
    bb = barset[symbol]
    return bb


def daddy_decider(symbol, dayAvg_a, dayAvg_b): #b > a
    crossed_to_neg = False #move outside for thread???
    crossed_to_pos = False



    
    todays_bars = api.get_barset('AAPL', 'day', limit=100)['AAPL']
    curr_day_close = todays_bars[-1].c

    todays_bars = api.get_barset('AAPL', 'day', limit=5)['AAPL']
    curr_day_close = todays_bars[-1].c
    todays_min_bars = api.get_barset('AAPL', 'day', limit=5)['AAPL']
    curr_min_close = todays_min_bars[-1].c

    avg_arr_a = get_moving_avg_arr(symbol, dayAvg_a, dayAvg_b, 'day')
    avg_arr_b = get_moving_avg_arr(symbol, dayAvg_b, dayAvg_b, 'day')

    diff = avg_arr_a[-1] - avg_arr_b[-1]
    open_into_negative = 0
    close_out_negative = 0
    open_into_positive = 0
    close_out_positive = 0
    if crossed_to_neg == False and crossed_to_pos == False: #current state
        if diff < 0:
            crossed_to_neg =True
        elif diff > 0:
            crossed_to_pos = True
        elif diff == 0 and avg_arr_a[-2] - avg_arr_b[-2] < 0:
            crossed_to_pos = True
        else:
            crossed_to_neg = True
    
    if crossed_to_neg==True and diff>=0: 
        crossed_to_neg = False
        crossed_to_pos = True
        close_out_negative = curr_day_close #use more percise,15min???
        open_into_positive = close_out_negative

        #??call option??



        return 1
    #Change in state - positive -> negative
    if crossed_to_pos==True and diff<=0:#breaking down positive ->selling?
        crossed_to_neg = True
        crossed_to_pos = False
        open_into_negative = curr_day_close #use more percise,15min???!!
        close_out_positive = open_into_negative

        percent_change = ((open_into_positive - close_out_positive) / open_into_positive) * 100
        if percent_change > 5:
            #SELL ORDER!!
            return "SELL"

        #??put option??!!

        return 1
    #buying in

    if crossed_to_neg==True and diff<0:#continued? dipping -> buying point
        #bell curve for buying in
        #open_into_negative
        #curr_day_close #use more percise,15min???
        percent_change = ((open_into_negative - curr_day_close) / open_into_negative) * 100
        #array of under curve closed? - bell curve for investing?!

        return 1
    
    if crossed_to_pos==True and diff>0:#continued? rising ->  point
        #check curr 15min for future cross
        return 1
    

#daddy_decider('AAPL', 10, 50)


avg10arr = get_moving_avg_arr('AAPL', 10, 100, 'day')
#('AAPL', 10, 50)
#print(avg10arr[-1])
avg50arr = get_moving_avg_arr('AAPL', 50, 100, 'day')
#print(avg50arr[-1])

for i in range(100):
   print(i, float("{:.2f}".format(avg10arr[i]-avg50arr[i])))


#response = create_order("AAPL", 100, "buy", "market", "gtc")
#response = create_order("DRN", 1, "buy", "market", "gtc")