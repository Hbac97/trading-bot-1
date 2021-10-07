import pygsheets
import json 
import pandas as pd 
import config
from datetime import datetime

class Sheets:

    def __init__(self):
        with open('service_account.json') as source:
            info = json.load(source)
        self.__spreadsheet_url =(config.GOOGLE_SHEETS_SPREADSHEET_URL)
        self.__client = pygsheets.authorize(service_account_file='service_account.json')
        self.__sheet = self.__client.open_by_key(config.GOOGLE_SHEETS_SPREADSHEET_KEY)

    def log(self,__exit_price,gains):
        self.now = datetime.now() 
        timestamp = self.now.strftime("%d/%m/%Y %H:%M:%S")

        print(self.__sheet)

        sheets=[timestamp,__exit_price,gains]

        df2=pd.DataFrame([sheets], columns=['timestamp', 'close', 'PNL'])
        df2.style.hide_index()

        wks=self.__sheet[0]
        wks.insert_rows(row=1, number=1, values=None, inherit=False)
        wks.set_dataframe(df2, start='A1',index=False,extend=True)


