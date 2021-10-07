import talib
import numpy as np 
import config
import ccxt
import schedule
import pandas as pd
from notifier import Notifier
from sheets import Sheets
from datetime import datetime
import time

class Bot:
    def __init__(self):
        self.__exchange = ccxt.binanceusdm({"apiKey": config.BINANCE_API_KEY,"secret": config.BINANCE_SECRET_KEY})
        self.__notifier = Notifier()
        self.__sheets = Sheets()
        self.__in_position = False
        self.__buy_price = None
        self.__exit_price = None
        self.__gains = None
        self.__leverage = 10
        self.__stop_loss = 7.5
        self.__RSI_period = 14
        self.__entry_size = 0.7

    def run_bot(self):

        pd.set_option('display.max_rows', None)
        Balance = self.__exchange.fetch_balance()
        print(f"Fetching new bars for {datetime.now().isoformat()}")

        bars = self.__exchange.fetch_ohlcv('ETH/USDT', timeframe='1m', limit=100)
        df = pd.DataFrame(bars[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        print(df.tail(5))

        Balance_use_test = (((np.round(((Balance['total']['USDT'])*self.__entry_size),4))/df['close'])*self.__leverage).tail(1)
        Balance_use = np.round(float(Balance_use_test.tail(1)),3)

        print('\n',"RSI:")
        RSI = talib.RSI(df['close'],timeperiod=self.__RSI_period)

        current_RSI =np.round((RSI.tail(1)),3)
        print(float(current_RSI))
        print('\n',"BULLISH BOT ACTIVE")
        print('\n','I will use',Balance_use,'USDT in trades')

        if (current_RSI <= 30).bool():
                if not self.__in_position:
                    print('\n','BUYING NOW...')
                    order = self.__exchange.create_market_buy_order('ETH/USDT', Balance_use)
                    print(order)
                    self.__buy_price = df['close']
                    buy_price_mess=float(self.__buy_price.tail(1))
                    self.notify(f'[Longing bot]Buying ETH at: {buy_price_mess}')
                    self.__in_position = True
                else:
                    print("You are in position, waiting for exit...")            

        if (current_RSI >= 70).bool():
                if self.__in_position:  
                     print('\n','SELLING NOW...')
                     order = self.__exchange.create_market_sell_order('ETH/USDT', Balance_use)
                     print(order)
                     self.__exit_price=float(df['close'].tail(1))
                     price_difference = ((float(self.__buy_price.tail(1))/self.__exit_price)-1)
                     self.__gains = ("%.2f%%" %(float(price_difference)*100*self.__leverage*-1))
                     self.notify(f'[Longing bot] Selling ETH at: {self.__exit_price} with {self.__gains} gains')
                     self.sheets_log()
                     self.__in_position = False
                else:
                     print("You aren't in position, waiting for entry...")

        if self.__in_position:
            print('\n','Bought at:',float(self.__buy_price.tail(1)),"$")
            price_difference = np.round(float(((self.__buy_price.tail(1))/(df['close'].tail(1)))-1),6)
            print('\n',f'SL at {self.__stop_loss}%')
            print("%.4f%%" %(float(price_difference)))
            
            if (price_difference >= self.__stop_loss/100/self.__leverage):
                      print('SELLING NOW...')
                      order = self.__exchange.create_market_sell_order('ETH/USDT', Balance_use)
                      print(order)
                      self.__exit_price=float(df['close'].tail(1))
                      price_difference = ((float(self.__buy_price.tail(1))/self.__exit_price)-1)
                      self.__gains = ("%.2f%%" %(float(price_difference)*100*self.__leverage*-1))
                      self.notify(f'[Longing bot] {self.__stop_loss}% SL hit at: {self.__exit_price} with {self.__gains} gains')
                      self.sheets_log()
                      self.__in_position = False  

    def notify(self,msg):
        self.__notifier.notify(msg)

    def sheets_log(self):
        self.__sheets.log(self.__exit_price,self.__gains)

execute = Bot()
schedule.every(5).seconds.do(execute.run_bot)

while True:
    schedule.run_pending()
    time.sleep(1)