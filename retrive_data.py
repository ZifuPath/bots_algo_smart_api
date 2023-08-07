import pandas as pd
from smartapi import SmartConnect

from smartapi import smartExceptions
from config import *
def candle_param(token ,formdate , todate):

    param ={
            "exchange": "NSE",
            "symboltoken": token,
            "interval": "FIFTEEN_MINUTE",
            "fromdate": formdate,
            "todate": todate,
            }
    # MARUTI - 10999  , BAJFIANCE --- 317 ,INFY -- 1594 REL -2885
    # try:
    #     candle = obj.getCandleData(param)
    # except Exception as e:
    #     print("Historic Api failed: {}".format(e.message))
    #     candle = {}
    return param

def candle_data(obj,param):
    try:
        candle = obj.getCandleData(param)
    except smartExceptions as e :
        print("Historic Api failed: {}".format(e.args))

        candle = []
    return candle

def order():
    API_KEY = API_KEY_MJ
    obj=SmartConnect(api_key=API_KEY,)
                    #optional
                    #access_token = "your access token",
                    #refresh_token = "your refresh_token")
    print(obj)
    USERID= USERID_MJ
    PASSWORD = PASSWORD_MJ
    data = obj.generateSession(USERID,PASSWORD)

    refreshToken= data['data']['refreshToken']

    feedToken=obj.getfeedToken()

    userProfile= obj.getProfile(refreshToken)
    return obj

def equityParam(SYMBOL,TOKEN,PRICE,QUANTITY):
    param ={
        "variety": "STOPLOSS",
        "tradingsymbol": SYMBOL +"-EQ",
        "symboltoken": str(TOKEN),
        "transactiontype": "SELL",
        "exchange": "NSE",
        "ordertype": "STOPLOSS_MARKET",
        "producttype": "INTRADAY",
        "duration": "DAY",
        "triggerprice": str(PRICE),
        "squareoff": "0.0",
        "stoploss": "0.0",
        "quantity": str(QUANTITY),
        }
    return param
    #

def give_param(TYPE,SYMBOL,TOKEN,PRICE,QUANTITY,ORDERTYPE,VARIETY):

    param ={
        "variety": VARIETY,
        "tradingsymbol": SYMBOL,
        "symboltoken": str(TOKEN),
        "transactiontype": TYPE,
        "exchange": "NSE",
        "ordertype": ORDERTYPE,
        "producttype": "INTRADAY",
        "duration": "DAY",
        "triggerprice": str(PRICE),
        "squareoff": "0.0",
        "stoploss": "0.0",
        "quantity": str(QUANTITY),
        }
    return param

def equity_order(obj,param):
    orderid = 0
    try:
        orderId = obj.placeOrder(param)

        print("The order id is: {}".format(orderId))
        return orderId
    except BaseException as e:
        print("Order placement failed: {}".format(e.args))
    except smartExceptions as e:
        print("Order placement failed: {}".format(e.message))
    return None


def equity_modify(ORDERID,SYMBOL,TOKEN,QUANTITY,TYPE):
    param = {
        "variety": "NORMAL",
        "orderid": str(ORDERID),
        "ordertype": "MARKET",
        "producttype": "INTRADAY",
        "duration": "DAY",
        "transactiontype": TYPE,
        "price": "0.0",
        "quantity": str(QUANTITY),
        "tradingsymbol": SYMBOL+"-EQ",
        "symboltoken": str(TOKEN),
        "exchange": "NSE"
    }
    return param

def stoploss_param(SYMBOL,TOKEN,QUANTITY,STOPLOSS,TYPE):
    param = {
        "variety": "STOPLOSS",
        "tradingsymbol": SYMBOL +"-EQ",
        "symboltoken": str(TOKEN),
        "transactiontype": TYPE,
        "exchange": "NSE",
        "ordertype": "STOPLOSS_MARKET",
        "producttype": "INTRADAY",
        "duration": "DAY",
        "triggerprice": str(STOPLOSS),
        "price": "0.0",
        "squareoff": "0.0",
        "stoploss": "0.0",
        "quantity": str(QUANTITY),
        }
    return param


from datetime import date,timedelta ,datetime
import time

def interval():
    year = datetime.now().year
    month = datetime.now().month
    day = datetime.now().day
    d = datetime.strptime('2017-05-04',"%Y-%m-%d")
    endtime = d.replace(minute=30, hour=15, second=00, year=year, month=month, day=day)
    minutes = (endtime-datetime.now())
    interval = ((minutes.seconds)/60)/15
    return int(interval)


def get_token():
    import requests
    BASE_URL = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'

    data = requests.get(BASE_URL)
    data = data.json()
    df =  pd.read_csv('future.csv')
    with open('future.csv') as f:
        stock = f.readline().splitlines()
    ts = []
    tokens = []
    for item in range(len(df)):
        symbol = df.iloc[item][0]
        symbol = symbol.rstrip()
        tradingsymbol = f'{symbol}'+'-EQ'
        tradingsymbol.replace(" ",'')

        print(tradingsymbol)
        for it in data:
            if it['symbol'] == tradingsymbol:
                    token = int(float(it['token']))

                    ts.append(tradingsymbol)
                    tokens.append(token)
                    print(token)
    print(tokens)
    df1 = pd.DataFrame(ts , columns = ['Symbol'])
    df2 = pd.DataFrame(tokens , columns = ['Token'])
    df1 = df1.join(df2)
    df1.to_csv('future_token.csv')

if __name__ == '__main__':
    get_token()
