from dash import Dash, html, dcc
from layout import layout_tab_setup, layout_tab_game, layout_tab_stats
from callbacks import register_callbacks
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback_context

app = Dash(
    __name__,
    suppress_callback_exceptions=True,  # ✅ AGREGAR ESTO
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)
server = app.server

# app.py

app.layout = html.Div([
    dcc.Store(id='store-players', data=[]),
    dcc.Store(id='store-shots', data={}),

    dcc.Store(id='store-game-state', data={'running': False, 'paused': False, 'round': 1}),
    dcc.Store(id='store-current-round-shots', data={}),
    
    dcc.Store(id='store-card-cooldowns', data={}),
    dcc.Store(id='store-active-card', data={}),
    dcc.Store(id='store-flexiones-tiempo', data=40),
    html.Div(id='card-overlay'),

    dcc.Interval(id='interval-timer', interval=1000, n_intervals=0, disabled=True),

    dcc.Tabs(id="tabs", value='tab-setup', children=[
        dcc.Tab(label='🎮 Setup', value='tab-setup'),
        dcc.Tab(label='🔥 Juego', value='tab-game'),
        dcc.Tab(label='📊 Estadísticas', value='tab-stats'),
    ]),

    html.Div(id='tabs-content', children=[
        html.Div(id='tab-setup', children=layout_tab_setup(), style={'display': 'block'}),
        html.Div(id='tab-game', children=layout_tab_game(), style={'display': 'none'}),
        html.Div(id='tab-stats', children=layout_tab_stats(), style={'display': 'none'})
    ])
])

@app.callback(
    Output('tab-setup', 'style'),
    Output('tab-game', 'style'),
    Output('tab-stats', 'style'),
    Input('tabs', 'value')
)
def toggle_tabs(tab):
    return (
        {'display': 'block'} if tab == 'tab-setup' else {'display': 'none'},
        {'display': 'block'} if tab == 'tab-game' else {'display': 'none'},
        {'display': 'block'} if tab == 'tab-stats' else {'display': 'none'},
    )


register_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)

