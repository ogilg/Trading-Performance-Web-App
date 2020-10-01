import yfinance as yf


def get_t_bill_return(start_date, end_date):
    tbill_data = yf.Ticker('^IRX')
    tbill = tbill_data.history(start=start_date, end=end_date, interval='1d', auto_adjust=False)
    tbill_price = tbill['Close']
    t_bill_return = ((tbill_price[-1] - tbill_price[0]) / tbill_price[0]) * 100
    return t_bill_return
