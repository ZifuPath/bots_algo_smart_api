from smartapi import smartConnect
from retrive_data import order
import csv
import json

import datetime
def get_token(instrument_list):
    with open(instrument_list) as f:
        stock_list = {}
        import requests

        BASE_URL = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'

        data = requests.get(BASE_URL)
        data = data.json()
        for row in csv.reader(f):
            stock = row[0]
            for items in data:
                if items['symbol'] == row[0]+'-EQ':
                    stock_list[row[0]+'-EQ'] = items['token']
        columns = ['symbol','token']
        with open('stock_token.csv' ,mode='w') as file:
            for key in stock_list.keys():
                print(stock_list[key])
                file.write("%s,%s\n" % (key, stock_list[key]))
    # csv.DictWriter(stock_list,'tstock_token.csv')
import time
def bot_ohol(obj):
    with open('stock_token.csv') as f:
        symbols = f.read().splitlines()
        stock = {}
        while datetime.time(9, 15)  < datetime.datetime.now().time() < datetime.time(15, 15):
            for symbol in symbols:
                tradingsymbol = symbol.split(',')[0]
                token = symbol.split(',')[1]
                ltpdata = obj.ltpData(exchange='NSE', tradingsymbol=tradingsymbol, symboltoken=token)
                ltp = ltpdata['data']['ltp']
                stock[tradingsymbol]={'Open': ltpdata['data']['open'],'High' : ltpdata['data']['high'],
                                      'Low':ltpdata['data']['low'],'Trade': False}
                condition1 = [stock[tradingsymbol]['Open'] == stock[tradingsymbol]['High'],
                              not stock[tradingsymbol]['Trade']]
                condition2 =[stock[tradingsymbol]['Open'] == stock[tradingsymbol]['Low'],
                              not stock[tradingsymbol]['Trade']]
                if all(condition1):
                    print(f' SELL : {tradingsymbol} at {datetime.datetime.now()} @{ltp}')
                    stock[tradingsymbol]['Trade'] = True
                if all(condition2):
                    print(f' BUY : {tradingsymbol} at {datetime.datetime.now()} @{ltp}')
                    stock[tradingsymbol]['Trade'] = True
            time.sleep(2)
if __name__ == '__main__':
    obj = order()
    bot_ohol(obj)
