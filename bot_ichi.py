
import schedule
from ta.trend import ichimoku_conversion_line, ichimoku_base_line
import time
from datetime import datetime, timedelta
from trading.bot.retrive_data import candle_param, candle_data, order, equityParam, equity_order, equity_modify, \
    stoploss_param, interval
import pandas as pd

STOCKS = {'MARUTI': 10999, 'BAJFINANCE': 317, 'INFY': 1594, 'RELIANCE': 2885}


def bot_one(stock):
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

    QUANTITY = 2
    obj = order()
    for num in range(times):
        todate = datetime.now().strftime('%Y-%m-%d %H:%M')
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
        df['I_B'] = ichimoku_conversion_line(df['High'], df['Low'])
        df['IBB'] = ichimoku_base_line(df['High'], df['Low'])
        print(df)
        if df['I_B'][-2:].values[0] < df['High'][-1:].values[0] \
                and df['I_B'][-1:].values[0] > df['Low'][-1:].values[0] \
                and df['I_B'][-1:].values[0] <= df['IBB'][-1:].values[0] and trade:
            sell_price = df['Low'][-1:].values[0] - 1
            stop_loss = sell_price + 25
            target_price = sell_price - 15
            param = equityParam(SYMBOL=stock, TOKEN=token, PRICE=sell_price,
                                QUANTITY=QUANTITY)
            orderid = equity_order(obj, param)
            trade = False
            signal = True
            count = 0
        sl_order = True

        while signal:

            orderid_sl = ''


            orders = obj.orderBook()

            orders =orders['data'][0]
            if orders['orderid'] == str(orderid) and orders['status'] == 'complete' and sl_order:
                param = stoploss_param(SYMBOL=stock, TOKEN=token, QUANTITY=QUANTITY, STOPLOSS=stop_loss)
                orderid_sl = equity_order(obj, param)
                sl_order = False
            if not sl_order:
                ltpdata = obj.ltpData(exchange='NSE', tradingsymbol=tradingsymbol, symboltoken=token)
                ltp = ltpdata['data']['ltp']

                if ltp < target_price:
                    param1 = equity_modify(SYMBOL=tradingsymbol, TOKEN=token, QUANTITY=QUANTITY, ORDERID=orderid_sl,TYPE='BUY')
                    obj.modifyOrder(orderparams=param1)
                    signal = False
                    trade = True
                    sl_order = True
                    time.sleep(1)
                if sl_order:
                    time.sleep(1)
            if (datetime.now().minute == (0 or 15 or 30 or 45)):
                break

            count += 1
        if signal and not trade and count == 1:
            position = obj.orderBook()

            for item in position['data'][0]:
                if item['orderid'] == orderid and item['orderstaus'] == 'trigger pending':
                    try:
                        obj.cancelOrder(obj, str(orderid), variety='STOPLOSS')
                        signal = False
                        trade = True
                    except BaseException as e:
                        print("Order placement failed: {}".format(e.args))

        while not signal:

            if (datetime.now().minute == (0 or 15 or 30 or 45)):
                print('Order Not Placed ')
                break


def main_task(stock):
    schedule.every().day.at('09:15:00').do(bot_one, stock)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    import multiprocessing
    task1 = multiprocessing.Process(target=main_task,args=('MARUTI',),name='MARUTI')
    task2 = multiprocessing.Process(target=main_task, args=('BAJFINANCE',), name='BAJFINANCE')
    task3 = multiprocessing.Process(target=main_task, args=('INFY',), name='INFY')
    task4 = multiprocessing.Process(target=main_task, args=('RELIANCE',), name='RELIANCE')
    task1.start()
    task2.start()
    task3.start()
    task4.start()

    # obj =order()
    # todate = datetime.now().strftime('%Y-%m-%d %H:%M')
    # fromdate = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d %H:%M')
    # data = candle_param(10999, fromdate, todate)
    # candle = {}
    # try:
    #     candle = candle_data(obj, data)
    # except BaseException as e:
    #     print('ERROR : f ')
    #     candle['data'] = []
    # data_list = candle['data']
    # df = pd.DataFrame(data_list, columns=['date_stamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
    # # print(df)
    # # df = df.reset_index(df)
    # df['I_B'] = ichimoku_conversion_line(df['High'], df['Low'])
    # df['IBB'] = ichimoku_base_line(df['High'], df['Low'])
    # print(df)
    # orders = obj.ltpData(exchange='NSE' , tradingsymbol='MARUTI-EQ', symboltoken='10999')
    # print(orders)