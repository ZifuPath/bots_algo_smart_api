from nsepy import get_history,get_quote
import pandas as pd

import schedule,time
import smtplib

def sendMail(msg):
    try:
        sender_mail = ""
        rec_mail = [ "" ,"r" ,"@gmail.com"]

        password = ''
        messege = msg

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_mail,password)
        print("login Sucess")

        server.sendmail(sender_mail,rec_mail,messege)
        print("Email Sent to",rec_mail)
    except:
        print('EMAIL NOT SENT')
        print(f'{msg}')

def calculateCpr(df):
    pivot = df['Close'] + df['Low'] +df['High']
    df['Pivot']= pivot
    df['Pivot'] = df['Pivot'].div(3)
    df['BC'] = df['Low'] + df['High']
    df['BC'] = df['BC'].div(2)
    df['TC'] = df['Pivot'] - df['BC'] + df['Pivot']
    return df

def step_up_gap_down_notification():
    import datetime as dt
    df= get_history(symbol='BANKNIFTY',start=dt.date(2021,4,1),end=dt.date.today(),index=True)
    df = calculateCpr(df)
    df['STEP'] = ["UP" if df['TC'].iloc[i]>df['TC'].iloc[i-1]
                  else "DOWN" for i in range(len(df))]

    from nsetools import Nse

    nse = Nse()
    data = nse.get_index_quote(code="nifty bank")
    open_price = data['lastPrice']
    condition1=  [df['STEP'].iloc[-1] == 'DOWN',
                 df['STEP'].iloc[-2] == 'DOWN',
                 open_price> df['TC'].iloc[-1]]
    condition2=  [df['STEP'].iloc[-1] == 'UP',
                 df['STEP'].iloc[-2] == 'UP',
                 open_price< df['TC'].iloc[-1]]
    if all(condition1):
        msg= f'STEP DOWN GAP UP IN BANKNIFTY'
    elif all(condition2):
        msg= f'STEP UP GAP DOWN IN BANKNIFTY'
    else:
        msg ='NO CPR SETUP Today'
    sendMail(msg)


def main_task():
    schedule.every().day.at('09:15:00').do(step_up_gap_down_notification)

    while True:
        schedule.run_pending()
        time.sleep(1)
if __name__ == '__main__':
    step_up_gap_down_notification()
