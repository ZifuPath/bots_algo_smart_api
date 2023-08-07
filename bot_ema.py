import threading

import schedule
from ta.trend import ema_indicator
import time
from datetime import datetime, timedelta
import datetime as dt
from bot.retrive_data import candle_param, candle_data, order, equityParam, equity_order, equity_modify, \
    stoploss_param, interval, give_param
import pandas as pd

STOCKS = {'MARUTI': 10999, 'BAJFINANCE': 317, 'INFY': 1594, 'RELIANCE': 2885}


def bot_one(stock,obj,target,qty):
    print(f'{stock} started')
    signal = False
    times = interval()
    print(times)
    trade = True
    orderid = 0
    target_price = 0

    stop_loss = 0.0
    count = 0
    tradingsymbol = stock+'-EQ'
    token = STOCKS.get(stock)

    QUANTITY = qty
    type = ''

    while dt.time(9, 15) > datetime.now().time():
        time.sleep(1)

    while dt.time(9, 15) < datetime.now().time() < dt.time(3, 15):
        todate = (datetime.now() - timedelta(minutes=2)).strftime('%Y-%m-%d %H:%M')
        fromdate = (datetime.now()-timedelta(days=60)).strftime('%Y-%m-%d %H:%M')
        data = candle_param(token, fromdate, todate)
        candle = {}
        try:
            candle = candle_data(obj, data)
        except BaseException as e:
            print('ERROR : f ')
            candle['data'] = []
        data_list = candle['data']
        df = pd.DataFrame(data_list, columns=['date_stamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
        # print(df)
        # df = df.reset_index(df)
        df['EMA_7'] = ema_indicator(df['Close'],window=7)
        df['EMA_21'] = ema_indicator(df['Close'],window=21)
        # print(df)
        conditions_buy = [df['EMA_7'][-2:].values[0] < df['EMA_21'][-2:].values[0],
                        df['EMA_7'][-1:].values[0] > df['EMA_21'][-1:].values[0],
                      trade]
        conditions_sell = [df['EMA_7'][-2:].values[0] > df['EMA_21'][-2:].values[0],
                        df['EMA_7'][-1:].values[0] < df['EMA_21'][-1:].values[0],
                        trade]
        if all(conditions_buy):
            buy_price = df['Open'][-1:].values[0]
            stop_loss = df['Low'][-1:].values[0]
            target_price = buy_price + target
            type = 'BUY'
            param = give_param(TYPE=type,SYMBOL=tradingsymbol, TOKEN=token, PRICE=buy_price,
                                QUANTITY=QUANTITY,ORDERTYPE='MARKET',VARIETY='NORMAL')
            orderid = equity_order(obj, param)
            trade = False
            signal = True

        sl_order = True
        if all(conditions_sell):
            sell_price = df['Open'][-1:].values[0]
            stop_loss = df['High'][-1:].values[0]
            target_price = sell_price - target
            type = 'SELL'
            param = give_param(TYPE=type,SYMBOL=tradingsymbol, TOKEN=token, PRICE=sell_price,
                                QUANTITY=QUANTITY,ORDERTYPE='MARKET',VARIETY='NORMAL')
            orderid = equity_order(obj, param)
            trade = False
            signal = True


        sl_order = True

        while signal and type == 'BUY' :
            orderid_sl = ''
            orders = obj.orderBook()
            orders =orders['data'][0]
            if orders['orderid'] == str(orderid) and orders['status'] == 'complete' and sl_order:
                param = stoploss_param(SYMBOL=stock,TYPE='SELL', TOKEN=token, QUANTITY=QUANTITY, STOPLOSS=stop_loss)
                orderid_sl = equity_order(obj, param)
                sl_order = False
            if not sl_order:
                ltpdata = obj.ltpData(exchange='NSE', tradingsymbol=tradingsymbol, symboltoken=token)
                ltp = ltpdata['data']['ltp']
                if ltp > target_price:
                    param1 = equity_modify(SYMBOL=tradingsymbol, TOKEN=token, QUANTITY=QUANTITY, ORDERID=orderid_sl,TYPE='SELL')
                    obj.modifyOrder(param1)
                    signal = False
                    trade = True
                    sl_order = True
                    time.sleep(1)
                if ltp<= stop_loss:
                    signal = False
                    trade = True
                    sl_order = True
                if sl_order:
                    time.sleep(1)

            val1 = datetime.now().minute
            condition_any1 = [val1 == 0, val1 == 15, val1 == 30, val1 == 45]
            if any(condition_any1):
                break

        while signal and type == 'SELL' :
            orderid_sl = ''
            orders = obj.orderBook()
            orders =orders['data'][0]
            if orders['orderid'] == str(orderid) and orders['status'] == 'complete' and sl_order:
                param = stoploss_param(SYMBOL=stock,TYPE='BUY', TOKEN=token, QUANTITY=QUANTITY, STOPLOSS=stop_loss)
                orderid_sl = equity_order(obj, param)
                sl_order = False
            if not sl_order:
                ltpdata = obj.ltpData(exchange='NSE', tradingsymbol=tradingsymbol, symboltoken=token)
                ltp = ltpdata['data']['ltp']
                if ltp < target_price:
                    param1 = equity_modify(SYMBOL=tradingsymbol, TOKEN=token, QUANTITY=QUANTITY, ORDERID=orderid_sl,TYPE='BUY')
                    obj.modifyOrder(param1)
                    signal = False
                    trade = True
                    sl_order = True
                    time.sleep(1)
                if ltp>= stop_loss:
                    signal = False
                    trade = True
                    sl_order = True
                if sl_order:
                    time.sleep(1)
            val1 = datetime.now().minute
            condition_any1 = [val1 == 0, val1 == 15, val1 == 30, val1 == 45]
            if any(condition_any1):
                break
        while not signal:
            val = datetime.now().minute
            condition_any = [val == 0, val == 15, val == 30, val == 45]

            print(stock,datetime.now())
            if any(condition_any):
                print('Order Not Placed ')
                break
            time.sleep(50)

def main_task(stock,obj,target,qty):
    schedule.every().day.at('09:15:00').do(bot_one, stock,obj,target,qty)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    obj= order()
    target = 20
    qty = 25
    # main_task('MARUTI',obj,target,qty)
    from threading import Thread
    import multiprocessing
    task1 = multiprocessing.Process(target=bot_one,args=('MARUTI',obj,40,15,),name = 'MARUTI')
    task2 = multiprocessing.Process(target=bot_one,args=('BAJFINANCE',obj,35,15,),name = 'BAJFINANCE')
    task3 = multiprocessing.Process(target=bot_one,args=('RELIANCE',obj,15,25,),name = 'RELIANCE')
    task1.start()
    task2.start()
    task3.start()