
from retrive_data import order
import schedule,time

def exit_order(obj):
    orderbook = obj.orderBook()
    for item in orderbook['data']:
        if item['status'] == 'trigger pending' and item['exchange'] == 'NSE' \
                and item['producttype'] == 'INTRADAY':
            orderId = item['orderid']
            tradingsymbol = item['tradingsymbol']
            symboltoken = item['symboltoken']
            quantity = item['quantity']
            type = item['transactiontype']
            param = {
                "variety": "NORMAL",
                'orderid': orderId,
                "tradingsymbol": tradingsymbol,
                "symboltoken": str(symboltoken),
                "transactiontype": type,
                "exchange": "NSE",
                "ordertype": "MARKET",
                "producttype": "INTRADAY",
                "duration": "DAY",
                "price": '0.0',
                "squareoff": "0",
                "stoploss": "0",
                "quantity": str(quantity), }
            obj.modifyOrder(param)
            print('order Exceuted')
            position = obj.position()
            position =position['data'][0]
            print('Profit  :',position['pnl'])


def main_task(obj):
    schedule.every().day.at('15:14:00').do(exit_order, obj)



    while True:
        schedule.run_pending()
        time.sleep(1)



if __name__ == '__main__':
    import datetime
    obj =order()
    main_task(obj)
