import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from app import app
from pages.page import Page

page = Page('Overview')
page.set_path('/analysis/overview')

asset_list = ['ALL ASSETS', 'GOOG', 'AMZN']
overview_metrics = ['profit-list', 'rate-of-return', 'aggregate-value-by-day', 'total-amount-traded']

page.set_storage(overview_metrics)

metrics = html.Div([
    dbc.Row(
        [
            dbc.Col(html.Div(
                [html.H3(id="p&l"), html.P("P&L")],
                id="p&l",
                className="mini_container", )
            ),
        ],
    ),
    dbc.Row(
        [
            dbc.Col(html.Div(
                [html.H3(id='total-amount-traded'), html.P("Total Amount Traded")],
                id="total-amount-traded",
                className="mini_container", )
            ),
            dbc.Col(html.Div(
                [html.H3(id='rate-of-return'), html.P("Rate of Return")],
                id="rate-of-return",
                className="mini_container", )
            ),
            dbc.Col(html.Div(
                [html.H3(id='profit-factor'), html.P("Profit Factor")],
                id='profit-factor',
                className="mini_container")
            ),
        ]
    ),
    dcc.Graph(id='aggregate-value-close'),
]
)

page.set_layout([
    html.H1(
        page.name,
        style={"margin-bottom": "10px",
               "margin-left": "4px",
               },
    ),

    html.Div(children='''
            Trading activity overview.
        '''),
    metrics,
])


@app.callback(
    [Output("p&l", "children"), Output('rate-of-return', 'children'), Output('profit-factor', 'children'),
     Output('total-amount-traded', 'children')],
    [Input('overview-profit-list', 'modified_timestamp'), Input('overview-rate-of-return', 'modified_timestamp')],
    [State('overview-profit-list', 'data'), State('overview-rate-of-return', 'data'),
     State('overview-total-amount-traded', 'data')]
)
def update_metrics(ts1, ts2, profit_list, rate_of_return, total_amount_traded):
    if profit_list is None:
        raise PreventUpdate
    total_profit = sum(profit_list)
    profit_factor = rate_of_return + 1

    return round(total_profit, 2), round(rate_of_return, 2), round(profit_factor, 2), round(total_amount_traded, 2)


@app.callback(
    Output("aggregate-value-close", "figure"),
    [Input('overview-aggregate-value-by-day', 'modified_timestamp')],
    [State('overview-aggregate-value-by-day', 'data')],
)
def update_aggregate_profit(ts, aggregate_value_daily):
    if ts is None:
        raise PreventUpdate
    profit_at_close = px.line(aggregate_value_daily, x='Date', y='Stock Close', title='Portfolio Value at Close')
    return profit_at_close



