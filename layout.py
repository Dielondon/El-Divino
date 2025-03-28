from dash import html, dcc
import dash_bootstrap_components as dbc

def layout_tab_setup():
    return html.Div([
        html.H3("Configuración de la partida"),
        dbc.Input(id='input-player', placeholder='Nombre del jugador...', type='text'),
        html.Div(id='player-error', style={'color': '#ff4d6d', 'marginTop': '5px'}),  # 👈 NUEVO
        html.Br(),
        dbc.Button("Agregar jugador", id='btn-add-player', color='primary'),
        html.Br(), html.Br(),
        html.Div(id='player-list'),
        html.Hr(),

        html.Label("Tipo de trago:"),
        dcc.Dropdown(
            id='drink-type',
            options=[
                {'label': 'Suave', 'value': 'soft'},
                {'label': 'Fuerte', 'value': 'strong'},
                {'label': 'Random', 'value': 'random'}
            ],
            value='soft'
        ),
        html.Br(),

        html.Div([
            dbc.Button("Iniciar juego", id='btn-start', color='success', className='me-2'),
            dbc.Button("Pausar", id='btn-pause', color='warning', className='me-2'),
            dbc.Button("Detener", id='btn-stop', color='danger')
        ])
    ])


def layout_tab_game():
    return html.Div([
        html.H3("¡Hora de beber!"),
        html.Div(id='current-round', children=[
            html.H4("Ronda actual: 1")
        ]),
        html.Div(id='player-shot-list'),
        html.Br(),

        html.Hr(),

        html.Div([
            html.H2("⏰ Temporizador:"),
            html.H1(id='timer-display', children='60'),
        ]),

        html.Audio(id='round-audio', src="", autoPlay=True),
        html.Div(id='round-animation'),

    ])



def layout_tab_stats():
    return html.Div([
        html.H3("Estadísticas del juego"),
        dcc.Graph(id='bar-shots'),
    ])
