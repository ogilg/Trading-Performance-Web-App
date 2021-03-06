from datetime import datetime, timedelta

import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import yfinance as yf
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from app import app
from pages.analysis.asset_mode_dropdown import generate_analysis_mode_dropdown
from pages.page import Page

page = Page("Exit-Quality")
page.set_path('/pages/exit_quality')
page.set_storage(['asset-list', 'buy-price-dict', 'sell-price-dict'])

exit_quality_gauge = {'axis': {'range': [-100, 100]},
                      'bar': {'color': 'black'},
                      'steps': [
                          {'range': [-100, 0], 'color': 'red'},
                          {'range': [0, 50], 'color': 'orange'},
                          {'range': [50, 75], 'color': 'green'},
                          {'range': [75, 100], 'color': 'darkgreen'}],
                      }

exit_quality_fig = go.Figure()
exit_quality_fig.add_trace(go.Indicator(
    domain={'x': [0, 1], 'y': [0, 1]},
    value=0,
    mode="gauge+number+delta",
    title={'text': "Exit quality"},
    gauge=exit_quality_gauge))

gauge_layout = html.Div([
    dcc.DatePickerRange(
        id='date-picker',
        max_date_allowed=datetime.today(),
        initial_visible_month=datetime.today(),
        start_date=(datetime.today() - timedelta(30)).date(),
        end_date=datetime.today().date(),
        display_format='MMM Do, YY',
        persistence=True,
        persisted_props=['start_date'],
        updatemode='bothdates',

    ),
    html.Br(),
    dcc.Graph(id='exit-quality-indicator', figure=exit_quality_fig)

])

page.layout = [
    html.H1(
        page.name,
        style={"margin-bottom": "10px",
               "margin-left": "4px",
               },
    ),
    generate_analysis_mode_dropdown(page.id),
    gauge_layout
]


@app.callback(
    Output('exit-quality-indicator', 'figure'),
    [Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date'),
     Input('exit-quality-asset-dropdown', 'value')],
    [State(page.id + '-buy-price-dict', 'data'), State(page.id + '-sell-price-dict', 'data')]
)
def update_exit_quality_indicator(start_date, end_date, stock_code, buy_price_dict, sell_price_dict):
    if stock_code is None:
        raise PreventUpdate
    start_date = datetime.strptime(start_date.split('T')[0], '%Y-%m-%d')
    end_date = datetime.strptime(end_date.split('T')[0], '%Y-%m-%d')

    sell_price = sell_price_dict[stock_code]
    buy_price = buy_price_dict[stock_code]

    stock_data = yf.download(stock_code, start=start_date, end=end_date)

    sorted_stock_closes = sorted(stock_data['Close'], reverse=True)
    max_close = round(sorted_stock_closes[0], 2)

    actual_return = ((sell_price - buy_price) / buy_price) * 100
    max_return = ((max_close - buy_price) / buy_price) * 100

    exit_rating = (actual_return / max_return) * 100

    exit_quality_fig = go.Figure()
    exit_quality_fig.add_trace(go.Indicator(
        domain={'x': [0, 1], 'y': [0, 1]},
        value=exit_rating,
        mode="gauge+number+delta",
        title={'text': "Exit quality"},
        gauge=exit_quality_gauge
    ))
    return exit_quality_fig


@app.callback(
    Output('exit-quality-asset-dropdown', 'options'),
    [Input('exit-quality-asset-list', 'modified_timestamp')],
    [State('exit-quality-asset-list', 'data')]
)
def update_asset_dropdown(ts, asset_list):
    if asset_list is None:
        raise PreventUpdate
    asset_options = [{'label': asset_name, 'value': asset_name} for asset_name in asset_list]
    return asset_options
