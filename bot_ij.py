from smartapi import smartExceptions
from ta.trend import ichimoku_conversion_line, ichimoku_base_line
from ta.momentum import rsi
import time
from datetime import datetime, timedelta
import datetime as dt
from retrive_data import candle_param, candle_data, order, equityParam, equity_order, equity_modify, \
    stoploss_param, interval, give_param

import pandas as pd

# import logging

STOCKS = {'TATASTEEL': 3499, 'JSWSTEEL':11723 , 'AXISBANK': 5900, 'RELIANCE': 2885, 'DRREDDY': 881,
          'SAIL':2963,'NMDC':15332,'ZEEL':3812 }

def bot_ij(stock, obj, BTGT, STGT):
    print(f'{stock} started')
    signal = False
    trade = True
    orderid = 0
    sl_orderid = 0
    target_price = 0
    stop_loss = 0.0
    count = 0
    tradingsymbol = stock + '-EQ'
    token = STOCKS.get(stock)
    QUANTITY = 15
    TYPE = ''
    sll1 = False
    sll2 = False
    sl_order = False
    dll = False
    while dt.time(9, 20) > datetime.now().time():
        time.sleep(1)
    while dt.time(9, 20) < datetime.now().time() < dt.time(15, 14):
        print(' In first while Loop')
        while True:

            if trade == False:
                break
            if dll or sl_order or sll1 or sll2:
                break
            val = datetime.now().minute
            condition_any = [val == 0, val == 15, val == 30, val == 45]
            if any(condition_any):
                break
            time.sleep(1)
        todate = (datetime.now() - timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M')
        todate1 = (datetime.now() - timedelta(minutes=15)).strftime('%Y-%m-%dT%H:%M') + ':00+05:30'
        # todate = "2021-06-10 12:30"
        print(todate1)

        fromdate = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d %H:%M')
        data = candle_param(token, fromdate, todate)
        candle = {}
        dll = False
        try:
            candle = candle_data(obj, data)
            data_list = candle['data']
            # print(data_list)
            df = pd.DataFrame(data_list, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
            # print(df.tail(1))
            todate2 = df.Date[-1:].values[0]
            # print(todate2)
            while todate1 != todate2:
                if sll1 or sll2 or dll or sl_order:
                    break
                candle = candle_data(obj, data)
                data_list = candle['data']
                # print(data_list)
                df = pd.DataFrame(data_list, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
                # print(df.tail(1))
                todate2 = df.Date[-1:].values[0]
                # todate1 = "2021-06-28T15:15:00+05:30"
                if todate1 == todate2:
                    break
            df['I_B'] = ichimoku_conversion_line(df['High'], df['Low'])
            df['IBB'] = ichimoku_base_line(df['High'], df['Low'])
            df['rsi'] = rsi(df.Close)
            # print(df.tail(1))
            conditions_buy = [df['I_B'][-1:].values[0] < df['High'][-1:].values[0],
                              df['I_B'][-1:].values[0] > df['Low'][-1:].values[0],
                              df['I_B'][-1:].values[0] >= df['IBB'][-1:].values[0],
                              df['Open'][-1:].values[0] < df['Close'][-1:].values[0],
                              df['rsi'][-1:].values[0] < 70, trade]
            print(conditions_buy)
            conditions_sell = [df['I_B'][-1:].values[0] < df['High'][-1:].values[0],
                               df['I_B'][-1:].values[0] > df['Low'][-1:].values[0],
                               df['I_B'][-1:].values[0] <= df['IBB'][-1:].values[0],
                               df['Open'][-1:].values[0] > df['Close'][-1:].values[0],
                               df['rsi'][-1:].values[0] > 30, trade]
            print(conditions_sell)
            if all(conditions_buy):
                print(f'Buy Condition Satiesfied for {stock}')
                buy_price = df['High'][-1:].values[0] + 0.1
                stop_loss = df['Low'][-1:].values[0]
                sl = abs(buy_price - stop_loss)
                target_price = round(buy_price + buy_price * BTGT,2)
                if sl > abs(buy_price * BTGT):
                    stop_loss = round(buy_price - buy_price * BTGT,2)
                TYPE = 'BUY'
                QUANTITY=round(15000*4/buy_price)
                quantity=round(700/abs(buy_price - stop_loss))
                if QUANTITY>quantity:
                    QUANTITY=quantity

                ltpdata = obj.ltpData(exchange='NSE', tradingsymbol=tradingsymbol, symboltoken=token)
                ltp = ltpdata['data']['ltp']
                if ltp < buy_price:
                    param = give_param(TYPE=TYPE, SYMBOL=tradingsymbol, TOKEN=token, PRICE=buy_price,
                                       QUANTITY=QUANTITY, ORDERTYPE='STOPLOSS_MARKET', VARIETY='STOPLOSS')
                else:
                    param = give_param(TYPE=TYPE, SYMBOL=tradingsymbol, TOKEN=token, PRICE="0.0",
                                       QUANTITY=QUANTITY, ORDERTYPE='MARKET', VARIETY='NORMAL')
                # print(param)
                orderid = equity_order(obj, param)
                print(f'Order Placed  {datetime.now()} for {stock}')
                sll1 = True
                count = 1
            time.sleep(1)
            while sll1:

                print(f'Checking if Order Hit for {stock}')
                orderbook = obj.orderBook()
                orderbook = orderbook['data']
                for item in orderbook:
                    if item['orderid'] == str(orderid) and item['status'] == 'trigger pending':
                        time.sleep(1)
                    if item['orderid'] == str(orderid) and item['status'] == 'complete':
                        trade = False
                        sl_param = give_param(TYPE='SELL', SYMBOL=tradingsymbol, TOKEN=token, PRICE=round(stop_loss, 1),
                                              QUANTITY=QUANTITY, ORDERTYPE='STOPLOSS_MARKET', VARIETY='STOPLOSS')
                        sl_orderid = equity_order(obj, sl_param)
                        signal = True
                        sl_order = True
                        sll1 = False
                        break
                if count == 1:
                    time.sleep(60)
                    count += 1
                else:
                    time.sleep(1)
                val1 = datetime.now().minute
                condition_any1 = [val1 == 0, val1 == 15, val1 == 30, val1 == 45]
                if any(condition_any1):
                    print(f'cancle order for {stock}')
                    obj.cancelOrder(order_id=str(orderid), variety='STOPLOSS')
                    trade = True
                    signal = False
                    sl_order = False
                    sll1 = False
                    dll = True
                    break
            while sl_order and TYPE == 'BUY':
                ltpdata = obj.ltpData(exchange='NSE', tradingsymbol=tradingsymbol, symboltoken=token)
                ltp = ltpdata['data']['ltp']
                print(f'Checking stock {stock} ltp {ltp} Target {target_price} and stoploss {stop_loss}')
                if ltp >= target_price:
                    param1 = equity_modify(SYMBOL=tradingsymbol, TOKEN=token, QUANTITY=QUANTITY,
                                           ORDERID=sl_orderid, TYPE='SELL')
                    obj.modifyOrder(param1)
                    signal = False
                    trade = True
                    sl_order = False
                    time.sleep(1)
                    break
                if ltp <= stop_loss:
                    trade = True
                    signal = False
                    sl_order = False
                    break
                orderbook = obj.orderBook()
                orderbook = orderbook['data']
                for item in orderbook:
                    if item['orderid'] == str(sl_orderid) and item['status'] == 'complete':
                        trade = True
                        signal = False
                        sl_order = False
                        break
                time.sleep(1)
            if all(conditions_sell):
                print(f'Buy Condition Satiesfied for {stock}')
                sell_price = df['Low'][-1:].values[0] - 0.1
                stop_loss = df['High'][-1:].values[0]
                sl = abs(sell_price - stop_loss)
                target_price = round(sell_price - sell_price * STGT,2)
                if sl > abs(sell_price - stop_loss):
                    stop_loss = round(sell_price + sell_price * STGT,2)
                TYPE = 'SELL'
                QUANTITY = round(15000 * 4 / sell_price)
                quantity = round(700 / abs(sell_price - stop_loss))
                if QUANTITY > quantity:
                    QUANTITY = quantity
                ltpdata = obj.ltpData(exchange='NSE', tradingsymbol=tradingsymbol, symboltoken=token)
                ltp = ltpdata['data']['ltp']
                if ltp > sell_price:
                    param = give_param(TYPE=TYPE, SYMBOL=tradingsymbol, TOKEN=token, PRICE=sell_price,
                                       QUANTITY=QUANTITY, ORDERTYPE='STOPLOSS_MARKET', VARIETY='STOPLOSS')
                else:
                    param = give_param(TYPE=TYPE, SYMBOL=tradingsymbol, TOKEN=token, PRICE="0.0",
                                       QUANTITY=QUANTITY, ORDERTYPE='MARKET', VARIETY='NORMAL')
                # print(param)
                orderid = equity_order(obj, param)
                print(f'Order Placed  {datetime.now()} for {stock}')
                # print(orderid)
                sll2 = True
                count = 1
            while sll2:

                print(f'Checking if Order Hit for {stock}')
                orderbook = obj.orderBook()
                orderbook = orderbook['data']
                for item in orderbook:
                    if item['orderid'] == str(orderid) and item['status'] == 'trigger pending':
                        time.sleep(1)
                    if item['orderid'] == str(orderid) and item['status'] == 'complete':
                        trade = False
                        sl_param = give_param(TYPE='BUY', SYMBOL=tradingsymbol, TOKEN=token, PRICE=round(stop_loss, 1),
                                              QUANTITY=QUANTITY, ORDERTYPE='STOPLOSS_MARKET', VARIETY='STOPLOSS')
                        sl_orderid = equity_order(obj, sl_param)
                        signal = True
                        sl_order = True
                        sll2 = False
                        break
                if count == 1:
                    time.sleep(60)
                    count += 1
                else:
                    time.sleep(1)
                val1 = datetime.now().minute
                condition_any1 = [val1 == 0, val1 == 15, val1 == 30, val1 == 45]
                if any(condition_any1):
                    obj.cancelOrder(order_id=orderid, variety='STOPLOSS')
                    trade = True
                    signal = False
                    sl_order = False
                    sll2 = False
                    dll = True
                    break
            while sl_order and TYPE == 'SELL':
                ltpdata = obj.ltpData(exchange='NSE', tradingsymbol=tradingsymbol, symboltoken=token)
                ltp = ltpdata['data']['ltp']
                print(f'Checking stock {stock} ltp {ltp} Target {target_price} and stoploss {stop_loss}')
                if ltp <= target_price:
                    param1 = equity_modify(SYMBOL=tradingsymbol, TOKEN=token, QUANTITY=QUANTITY,
                                           ORDERID=sl_orderid, TYPE='BUY')
                    obj.modifyOrder(param1)
                    trade = True
                    signal = False
                    sl_order = False
                    break
                if ltp >= stop_loss:
                    trade = True
                    signal = False
                    sl_order = False
                    break
                orderbook = obj.orderBook()
                orderbook = orderbook['data']
                for item in orderbook:
                    if item['orderid'] == str(sl_orderid) and item['status'] == 'complete':
                        trade = True
                        signal = False
                        sl_order = False
                        break
                time.sleep(1)
            check = 1
            while not signal:
                if dll:
                    break
                if check == 1:
                    time.sleep(60)
                else:
                    time.sleep(10)
                val = datetime.now().minute
                condition_any = [val == 0, val == 15, val == 30, val == 45]
                check += 1
                if any(condition_any):
                    print(f'Order Not Placed  {datetime.now()} for {stock}')
                    break
        except BaseException as e:
            print(f'ERROR :{e.args}')
            time.sleep(5)
        except smartExceptions as e:
            print(f'ERROR : {e.message}')
            time.sleep(5)


if __name__ == '__main__':
    obj = order()
    import multiprocessing
    task1 = multiprocessing.Process(target=bot_ij, args=('TATASTEEL', obj, 0.85 / 100, 0.85 / 100)).start()
    task2 = multiprocessing.Process(target=bot_ij, args=('NMDC', obj, 0.85 / 100, 0.85 / 100)).start()