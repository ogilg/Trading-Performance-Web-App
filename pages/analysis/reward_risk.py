import dash_html_components as html

from pages.analysis.asset_mode_dropdown import generate_analysis_mode_dropdown
from pages.page import Page

page = Page("Reward-Risk")
page.set_path('/pages/reward_risk')

asset_list = ['ALL ASSETS', 'GOOG', 'AMZN']
sessions = ['session 1', 'session 2']
asset_dropdown = generate_analysis_mode_dropdown(asset_list, sessions)

page.layout = html.Div([
    html.H1(
        page.name,
        style={"margin-bottom": "10px",
               "margin-left": "4px",
               },
    ),

    asset_dropdown,
    html.Div(id=page.id + '-content'),
])