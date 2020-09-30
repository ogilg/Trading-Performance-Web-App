import plotly.graph_objects as go
import dash
import dash_core_components as dcc


from model.ratio_metrics import *
import statistics
import yfinance as yf
import pandas as pd
import numpy as np

import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from app import app
from pages.analysis.asset_mode_dropdown import generate_analysis_mode_dropdown
from pages.page import Page

page = Page("Reward-Risk")
page.set_path('/pages/reward_risk')
page.set_storage(['asset-list', 'buy-price-dict', 'sell-price-dict', 'number-of-shares'])

###Intermediate calculations###

#Amounts
amounts_buy = []
for number_share, buy_price in zip(number_of_shares,buy_price_list):
    amounts_buy.append(number_share*buy_price)
amounts_sell = []
for number_share, sell_price in zip(number_of_shares, sell_price_list):
    amounts_sell.append(number_share*sell_price)

#Rate of return:
#option1: use overall exit prices and buy prices
total_sell_price = sum(amounts_sell)
total_buy_price  = sum(amounts_buy)
one_rate_of_return = ((total_sell_price - total_buy_price)/total_buy_price)*100
rate_return = one_rate_of_return
#option2: find return for each stock and do weighted average
first_rate_returns = []
for sell_price, buy_price in zip(sell_price_list, buy_price_list):
    first_rate_returns.append(((sell_price-buy_price)/buy_price)*100)
proportions = []
sum_amounts_buy = sum(amounts_buy)
for amount_buy in amounts_buy:
    proportions.append(amount_buy/sum_amounts_buy)
two_rate_return_first = []
for first_rate_return, proportion in zip(first_rate_returns, proportions):
    two_rate_return_first.append(first_rate_return*proportion)
two_rate_return = sum(two_rate_return_first)

# Finding the start and end dates
sorted_buy_dates = buy_dates.sort()
sorted_sell_dates = sell_dates.sort()
start_date = sorted_buy_dates[0]
end_date = sorted_sell_dates[-1]


# Finding the T-Bill rate of return between the first trade and the last trade
tbill_data = yf.Ticker('^IRX')
tbill = tbill_data.history(start=start_date, end=end_date, interval='1d', auto_adjust=False)
tbill_price = tbill['Close']
tbill_return = ((tbill_price[-1] - tbill_price[0])/tbill_price[0])*100
us_t_bill  = tbill_return

# Finding the standard deviation of the EXCESS returns
std_excess_return = np.std(one_rate_of_return - tbill_return)

# Finding the standard deviation of the DOWNSIDE returns
neg_returns_list = [num for num in two_rate_return_first if num < 0]
std_downside_return = np.std(neg_returns_list)

# Finding the beta of the portfolio
beta1 = []
for asset in asset_list:
    info = yf.Ticker(asset)
    beta_specific = info.info['beta']
    beta1.append((beta_specific))
beta_portfolio = np.average(beta1, weights=proportions)

# Overall portfolio gains
amounts_diff = []
for amount_buy, amount_sell in zip(amounts_buy, amounts_sell):
    amounts_diff.append(amount_sell-amount_buy)
gains = [num for num in amounts_diff if num>0]
losses = [num for num in amounts_diff if num<0]
total_gains = sum(gains)
total_losses = abs(sum(losses))


### various ratios ###
sharpe_ratio = calculate_sharpe_ratio(rate_return, us_t_bill, std_excess_return)
sortino_ratio = calculate_sortino_ratio(rate_return, us_t_bill, std_downside_return)
calmar_ratio = calculate_calmar_ratio(rate_return, us_t_bill, beta_portfolio)
gain_to_pain_ratio = total_gains / total_losses


sharpe_ratio_fig = go.Figure(go.Indicator(
    domain = {'x': [0, 1], 'y': [0, 1]},
    value = sharpe_ratio,
    mode = "gauge+number+delta",
    title = {'text': "Sharpe ratio"},
    gauge = {'axis': {'range': [None, 4]},
            'bar': {'color': "black"},
             'steps' : [
                 {'range': [0, 1], 'color': "red"},
                 {'range': [1, 2], 'color': "orange"},
                 {'range': [2,3], 'color': 'green'},
                 {'range': [3,4], 'color': 'darkgreen'}],
             }))

sortino_ratio_fig = go.Figure(go.Indicator(
    domain = {'x': [0, 1], 'y': [0, 1]},
    value = sortino_ratio,
    mode = "gauge+number+delta",
    title = {'text': "Sortino ratio"},
    gauge = {'axis': {'range': [None, 4]},
            'bar': {'color': "black"},
             'steps' : [
                 {'range': [0, 1], 'color': "red"},
                 {'range': [1, 2], 'color': "orange"},
                 {'range': [2,3], 'color': 'green'},
                 {'range': [3,4], 'color': 'darkgreen'}],
             }))

gain_to_pain_fig = go.Figure(go.Indicator(
    domain = {'x': [0, 1], 'y': [0, 1]},
    value = gain_to_pain_ratio,
    mode = "gauge+number+delta",
    title = {'text': "Gain to Pain ratio"},
    gauge = {'axis': {'range': [None, 4]},
            'bar': {'color': "black"},
             'steps' : [
                 {'range': [0, 1], 'color': "red"},
                 {'range': [1, 2], 'color': "orange"},
                 {'range': [2,3], 'color': 'green'},
                 {'range': [3,4], 'color': 'darkgreen'}],
             }))


page.set_layout([
    html.H1(
        page.name,
        style={"margin-bottom": "10px",
               "margin-left": "4px",
               },
    ),

    generate_analysis_mode_dropdown(page.id),
    html.Div(id=page.id + '-content'),
])


# @app.callback(
#     [Output()], # add output
#     [Input('-'.join((page.id, 'entry-dates')), 'modified_timestamp')],
#     [State('-'.join((page.id, 'asset-list')), 'data'), State('-'.join((page.id, 'buy-price-dict')), 'data'),State('-'.join((page.id, 'sell-price-dict')), 'data'),State('-'.join((page.id, 'number-of-shares')), 'data')]
# )
# def update_risk_metrics(timestamp, asset_list, buy_price_dict, sell_price_dict, number_of_shares):
#     #TODO: add risk adjusted ratio figures
#     buy_price = buy_price_dict['AAPL'] for example
#     raise PreventUpdate
#     return

@app.callback(
    Output('-'.join((page.id, 'asset-dropdown')), 'options'),
    [Input('-'.join((page.id, 'asset-list')), 'modified_timestamp')],
    [State('-'.join((page.id, 'asset-list')), 'data')]
)
def update_asset_dropdown(ts, asset_list):
    asset_options = [{'label': asset_name, 'value': asset_name} for asset_name in asset_list]
    return asset_options