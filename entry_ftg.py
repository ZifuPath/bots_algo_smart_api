import datetime

import pandas as pd

import schedule,time
import smtplib
from retrive_data import order,equity_order,give_param


def bot_ftg(obj):
    symbols = pd.read_csv('future_token.csv')
    stock = []

    for item in range(len(symbols)):
        symbol = symbols['Symbol'].iloc[item]
        token = symbols['Token'].iloc[item]
        token = int(float(token))

        try:
            LTP = obj.ltpData(exchange='NSE', tradingsymbol=symbol, symboltoken=token)
            # print(LTP)
            ltp = LTP['data']['ltp']
            closePrice = LTP['data']['close']
            print(f'symbol:{symbol},LTP:{ltp} ,Last CLose : {closePrice}')
            stocks = [symbol, ltp,closePrice]
            stock.append(stocks)
        except:
            pass


        # print(stock)
    df = pd.DataFrame(stock,columns=['SYMBOL','LTP','Close'])
    df["Close"] = [float(str(i).replace(",", "")) for i in df["Close"]]
    df["LTP"] = [float(str(i).replace(",", "")) for i in df["LTP"]]
    print(df.head(5))

    df['change'] = [(df['LTP'].iloc[i]-df['Close'].iloc[i])/(df['Close'].iloc[i]) for i in range(len(df))]
    df['abs_change'] = [abs(df['change'].iloc[i]) for i in range(len(df))]
    df['type'] = ['BUY' if df['change'].iloc[i]<0 else 'SELL' for i in range(len(df))]
    df['GT'] = [True if df['abs_change'].iloc[i]>0.02 else False for i in range(len(df))]
    # print(df.head(5))
    data = df.sort_values(by = 'abs_change',ascending=False)
    data =data[data['GT']== True]
    data.reset_index(inplace=False)
    print(data)
    # messages= []
    # for item in range(len(data)):
    #     statement = (f'{data["SYMBOL"].iloc[item]} is placed at {data["LTP"].iloc[item]} with {data["type"].iloc[item]} order ')
    #     messages.append(statement)
    #     if item==5:
    #         break
    return data

def ftg_order(obj,data,SL):
    print('running')
    import math
    symbols = pd.read_csv('future_token.csv')
    times= 5
    if len(data)<=5:
        times = len(data)
    for item in range(times):
        symbol = data.iloc[item][0]
        type = data['type'].iloc[item]
        token = 0
        for num in range(len(symbols)):
            if symbols['Symbol'].iloc[num]==symbol:
                token = symbols['Token'].iloc[num]
                token = int(float(token))
                # print(token)
                # print(symbol)
        ltp = obj.ltpData(exchange='NSE',tradingsymbol=symbol,symboltoken=token)
        ltp =ltp['data']['ltp']
        if type == 'BUY':
            qty = round(SL/(ltp-(ltp*0.98)))
        else:
            qty = round(SL/((ltp*1.02)-ltp))

        param = give_param(VARIETY='NORMAL',SYMBOL=symbol,
                             TOKEN=token,PRICE=0.0,QUANTITY=qty,TYPE=type,ORDERTYPE='MARKET')
        orderid = equity_order(obj= obj,param = param)
        time.sleep(0.5)

    try:
        position = obj.orderBook()
        for it in position['data']:
            if it['orderstatus'] == 'complete':
                price = it['averageprice']
                if it["transactiontype"] == 'BUY':
                    stop_loss = math.ceil(float(price)*0.98)
                    st_type = 'SELL'
                else:
                    stop_loss = math.floor(float(price)*1.02)
                    st_type = 'BUY'
                sl_param = give_param(VARIETY='STOPLOSS',SYMBOL=it["tradingsymbol"],
                                 TOKEN=it["symboltoken"],PRICE=stop_loss,QUANTITY=it["quantity"],TYPE=st_type,ORDERTYPE='STOPLOSS_MARKET')
                sl_orderid = equity_order(obj=obj,param=sl_param)
                print(f'{it["transactiontype"]} {it["tradingsymbol"]} at {price} and SL placed at {stop_loss}')
                time.sleep(0.5)
    except:
        pass


    # sendMail(msg)


def main_task1(obj,data,SL):
    schedule.every().day.at('09:15:02').do(ftg_order,obj,data,SL)



    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    obj = order()
    sl = 400
    data = bot_ftg(obj)
    main_task1(obj,data,sl)
    # orderbook = obj.orderBook()
    # for item in orderbook['data']:
    #     print(item)
    # # data = bot_ftg(obj)
    # # sl = 400
    # # # ftg_order(obj,data,sl)
    # # main_task1(obj,data,sl)
    # # position = obj.tradeBook()
    # # position =position['data']
    # # print(position)
    # while datetime.time(15,10)>datetime.datetime.now().time():
    #     position = obj.position()
    #     position =position['data']
    #     PNL = 0
    #     for item in position:
    #         PNL = PNL + float(item['pnl'])
    #         print('Profit  :',item['pnl'])
    #     PNL = round(PNL)
    #     print('Total Profit :', PNL)
    #     time.sleep(10)
    # symbol = 'APOLLOHOSP-EQ'
    # token = 157

    # ltp = obj.ltpData(exchange='NSE', tradingsymbol=symbol, symboltoken=token)
    # print(ltp['data'])
    # data =bot_ftg(obj)
    # SL = 300
    # ftg_order(obj,data,SL)

