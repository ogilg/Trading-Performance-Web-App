import yfinance as yf
from datetime import datetime, timedelta

def get_us_tbill (start_date, end_date):
    tbill_data = yf.Ticker('^IRX')
    interval = '1d'
    tbill = tbill_data.history(start=start_date, end=end_date, interval=interval, auto_adjust=False)
    tbill_price = tbill['Close']
    tbill_return = tbill_price[-1] - tbill_price[0]
    tbill_final = format(tbill_return, '.2f')
    print(f"{tbill_final} %")

#test data
start_date = datetime(2020,1,1)
end_date = datetime(2020,9,20)
tbill = get_us_tbill(start_date,end_date)