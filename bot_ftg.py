from nsepy import get_history,get_quote
import pandas as pd

import schedule,time
import smtplib


def sendMail(msg):
    sender_mail = "zorif.maths1@gmail.com"
    rec_mail = [ "fzpathan@gmail.com" ,"rmshinde41@gmail.com"]

    password = '8087490543'
    messege = msg

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_mail,password)
    print("login Sucess")

    server.sendmail(sender_mail,rec_mail,messege)
    print("Email Sent to",rec_mail)

def bot_ftg():
    symbols = pd.read_csv('future.csv')
    stock = []

    for item in range(len(symbols)):
        symbol = symbols.iloc[item][0]
        print(symbol)
        data =get_quote(symbol=symbol)

        try:
            closePrice = (data['data'][0]['previousClose'])
            lastPrice = (data['data'][0]['lastPrice'])
            stocks = [symbol, lastPrice, closePrice]
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
    df['GT'] = [True if df['abs_change'].iloc[i]>0.01 else False for i in range(len(df))]
    data = df.sort_values(by = 'abs_change',ascending=False)
    data =data[data['GT']== True]
    data.reset_index(inplace=False)
    print(data.head(5))
    messages= []
    for item in range(len(data)):
        statement = (f'{data["SYMBOL"].iloc[item]} is placed at {data["LTP"].iloc[item]} with {data["type"].iloc[item]} order ')
        messages.append(statement)
        if item==5:
            break
    return data

def ftg_order():
    from retrive_data import order,equity_order,give_param
    import math
    data = bot_ftg()
    obj = order()
    FUND = 100000
    FACTOR = 10
    TOTAL  = FUND*FACTOR
    symbols = pd.read_csv('future_token.csv')
    for item in range(len(data)):
        symbol = data.iloc[item][0]
        symbol = symbol+'-EQ'
        type = data['type'].iloc[item]
        token = 0
        for num in symbols:
            if symbols['Symbol'].iloc[num]==symbol:
                token = symbols['token'].iloc[num]
        ltp = obj.ltpData(exchange='NSE',tradingsymbol=symbol,symboltoken=token)
        qty = round((TOTAL/5)/ltp)
        param = give_param(VARIETY='NORMAL',SYMBOL=symbol,
                             TOKEN=token,PRICE=0.0,QUANTITY=qty,TYPE=type,ORDERTYPE='MARKET')
        orderid = equity_order(obj= obj,param = param)
        position = obj.position()
        for it in position['data'][0]:
            if it['orderid'] == orderid and it['orderstaus'] == 'complete':
                price = it['fillprice']
                if type == 'BUY':
                    stop_loss = math.ceil(price*0.98)
                    st_type = 'SELL'
                else:
                    stop_loss = math.floor(price*1.02)
                    st_type = 'BUY'
            sl_param = give_param(VARIETY='STOPLOSS',SYMBOL=symbol,
                             TOKEN=token,PRICE=stop_loss,QUANTITY=qty,TYPE=st_type,ORDERTYPE='STOPLOSS_MARKET')
            sl_orderid = equity_order(obj=obj,param=sl_param)
            print(f'{type} {symbol} at {price} and SL placed at {stop_loss}')

    # sendMail(msg)



def main_task():
    schedule.every().day.at('09:15:45').do(bot_ftg)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    bot_ftg()