from dash import Input, Output, State, callback_context
from layout import layout_tab_setup, layout_tab_game, layout_tab_stats
from dash import Input, Output, State, MATCH, ALL
from dash.exceptions import PreventUpdate
import plotly.express as px
import pandas as pd
from dash import html
from logic import generar_ronda
from dash import ctx
import dash
from random import randint
import random
from datetime import datetime, timedelta
import time
from logic import generar_carta
from dash import dcc
import plotly.graph_objects as go
import re

def register_callbacks(app):



    @app.callback(
        Output('player-list', 'children'),
        Input('store-players', 'data')
    )
    def display_players(players):
        if not players:
            return html.I("Sin jugadores aún.")

        return html.Div([
            html.Div([
                html.Span(p, style={'margin-right': '10px'}),
                html.Button("❌", id={'type': 'delete-player', 'index': p}, n_clicks=0, style={'color': 'red'})
            ], style={'margin-bottom': '8px'}) for p in players
        ])


    @app.callback(
        Output('player-shot-list', 'children'),
        Input('store-players', 'data'),
        Input('store-current-round-shots', 'data'),
        Input('store-card-cooldowns', 'data')  # 👈 CAMBIADO a Input
    )
    def update_game_tab_players(players, round_shots, cooldowns):
        if not players:
            return html.Div("Agrega jugadores primero.")

        ahora = time.time()
        return html.Div([
            html.Div([
                html.H4(f"{p} ({round_shots.get(p, 0)} shots)"),
                html.Button(
                    "🎴 Usar carta",
                    id={'type': 'use-card', 'index': p},
                    n_clicks=0,
                    className='card-button-cooldown' if (ahora - cooldowns.get(p, 0)) < 300 else '',
                    style={'margin': '8px'}
                ),
            ], style={'margin': '10px'}) for p in players
        ])



    @app.callback(
        Output('bar-shots', 'figure'),
        Input('store-shots', 'data')
    )
    def update_bar_chart(shots_data):
        if not shots_data:
            return go.Figure(
                layout=dict(
                    plot_bgcolor='#1c1c1e',
                    paper_bgcolor='#1c1c1e',
                    font=dict(color='#ffccff', size=18),
                    title='No hay jugadores aún',
                )
            )

        jugadores = list(shots_data.keys())
        shots = list(shots_data.values())

        colors = [
            f"hsl({i * 360 / len(jugadores)}, 80%, 60%)"
            for i in range(len(jugadores))
        ]

        fig = go.Figure(data=[
            go.Bar(
                x=jugadores,
                y=shots,
                marker=dict(color=colors),
                text=shots,
                textposition='auto',
                hoverinfo='x+y'
            )
        ])

        fig.update_layout(
            title='🍻 Shots por jugador',
            plot_bgcolor='#1c1c1e',
            paper_bgcolor='#1c1c1e',
            font=dict(color='white', size=18),
            xaxis=dict(title='Jugador', showgrid=False, tickfont=dict(size=16)),
            yaxis=dict(title='Shots', showgrid=False, tickfont=dict(size=16)),
            margin=dict(t=60, b=60, l=40, r=40),
            height=500,
        )

        return fig
    

    @app.callback(
        Output('timer-display', 'children'),
        Output('store-game-state', 'data'),
        Output('interval-timer', 'disabled'),
        Output('store-current-round-shots', 'data'),
        Output('store-shots', 'data'),
        Output('current-round', 'children'),
        Output('round-audio', 'src'),
        Input('btn-start', 'n_clicks'),
        Input('btn-pause', 'n_clicks'),
        Input('btn-stop', 'n_clicks'),
        Input('interval-timer', 'n_intervals'),
        State('store-players', 'data'),
        State('drink-type', 'value'),
        State('store-game-state', 'data'),
        State('store-shots', 'data'),
        State('timer-display', 'children'),
        prevent_initial_call=True,
        allow_missing=True,
    )

    def manejar_juego(n_clicks_start, n_clicks_pause, n_clicks_stop, n_intervals,
                    jugadores, tipo_trago, game_state, shots_totales, tiempo_actual):

        trigger = ctx.triggered_id

        if not jugadores:
            raise PreventUpdate

        if trigger == 'btn-start':
            tiempo, nuevos_shots = generar_ronda(jugadores, tipo_trago)
            for j in nuevos_shots:
                if j not in shots_totales:
                    shots_totales[j] = 0  # 👈 Asegura que la clave existe
                shots_totales[j] += nuevos_shots[j]

            game_state = {'running': True, 'paused': False, 'round': 1}

            return (
                tiempo,
                game_state,
                False,
                nuevos_shots,
                shots_totales,
                html.H4("Ronda actual: 1"),
                dash.no_update 
            )

        elif trigger == 'btn-pause':
            game_state['paused'] = not game_state['paused']
            return (
                dash.no_update,
                game_state,
                game_state['paused'],  # True: desactiva timer, False: lo reanuda
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update 
            )

        elif trigger == 'btn-stop':
            return (
                "60",
                {'running': False, 'paused': False, 'round': 1},
                True,
                {},
                {},
                html.H4("Ronda actual: 1"),
                dash.no_update 
            )

        elif trigger == 'interval-timer' and game_state['running'] and not game_state['paused']:
            tiempo_actual = int(tiempo_actual)
            tiempo_actual -= 1

            if tiempo_actual <= 0:
                tiempo, nuevos_shots = generar_ronda(jugadores, tipo_trago)
                for j in nuevos_shots:
                    if j not in shots_totales:
                        shots_totales[j] = 0
                    shots_totales[j] += nuevos_shots[j]
                game_state['round'] += 1

                return (
                    tiempo,
                    game_state,
                    False,
                    nuevos_shots,
                    shots_totales,
                    html.H4(f"Ronda actual: {game_state['round']}"),
                    f"/assets/tomar.wav?{randint(0, 1_000_000)}"  # 👈 fuerza recarga del audio
                )
            else:
                return (
                    tiempo_actual,
                    dash.no_update,
                    dash.no_update,
                    dash.no_update,
                    dash.no_update,
                    dash.no_update,
                    dash.no_update  # no cambia audio
                )

        raise PreventUpdate


    @app.callback(
        Output('store-players', 'data', allow_duplicate=True),
        Output('store-shots', 'data', allow_duplicate=True),
        Output('player-error', 'children'),  # 👈 NUEVO
        Input('btn-add-player', 'n_clicks'),
        Input({'type': 'delete-player', 'index': ALL}, 'n_clicks'),
        State('input-player', 'value'),
        State('store-players', 'data'),
        State('store-shots', 'data'),
        prevent_initial_call=True,
    )
    def actualizar_jugadores(add_click, delete_clicks, input_name, players, shots):
        triggered = ctx.triggered_id

        if not triggered:
            raise PreventUpdate

        # ✅ Agregar jugador
        if triggered == 'btn-add-player':
            if not input_name:
                return dash.no_update, dash.no_update, "El nombre no puede estar vacío."

            input_name = input_name.strip()

            if not input_name:
                return dash.no_update, dash.no_update, "El nombre no puede estar vacío."

            if not re.match(r'^[a-zA-Z0-9ñÑáéíóúÁÉÍÓÚüÜ\s]{1,20}$', input_name):
                return dash.no_update, dash.no_update, "Solo letras, números y espacios. Máx 20 caracteres."

            if input_name.lower() in [p.lower() for p in players]:
                return dash.no_update, dash.no_update, "Ese nombre ya está en uso."

            players.append(input_name)
            shots[input_name] = 0
            return players, shots, ""  # 👈 Limpia error

        # ✅ Eliminar jugador
        elif isinstance(triggered, dict) and triggered.get('type') == 'delete-player':
            jugador = triggered['index']
            players = [p for p in players if p != jugador]
            shots.pop(jugador, None)
            return players, shots, ""

        raise PreventUpdate



    @app.callback(
        Output('store-active-card', 'data'),
        Output('store-card-cooldowns', 'data'),
        Output('store-flexiones-tiempo', 'data'),
        Input({'type': 'use-card', 'index': ALL}, 'n_clicks'),
        State('store-players', 'data'),
        State('store-card-cooldowns', 'data'),
        prevent_initial_call=True
    )
    def activar_carta(n_clicks_list, jugadores, cooldowns):
        triggered = ctx.triggered_id

        if not triggered or triggered.get('type') != 'use-card' or ctx.triggered[0]['value'] == 0:
            raise PreventUpdate

        jugador = triggered['index']

        # Verificamos cooldown
        ahora = time.time()
        ultimo_uso = cooldowns.get(jugador, 0)
        if ahora - ultimo_uso < 300:
            raise PreventUpdate  # cooldown activo

        # Generar carta
        carta = generar_carta(jugador_actual=jugador, jugadores=jugadores)

        # Guardar carta activa y actualizar cooldown
        cooldowns[jugador] = ahora
        return carta, cooldowns, 40



    @app.callback(
        Output('card-overlay', 'children'),
        Input('store-active-card', 'data'),
        State('store-players', 'data'),
        prevent_initial_call=True
    )
    def mostrar_overlay(carta, jugadores):
        if not carta or not isinstance(carta, dict) or 'id' not in carta:
            return html.Div()

        jugador_actual = carta.get("jugador")
        tipo = carta.get("tipo")
        imagen = carta.get("imagen", None)

        contenido = []

        # 📸 Imagen de la carta
        if imagen:
            contenido.append(html.Img(
                src=f"/assets/{imagen}",
                style={
                    'width': '100%',
                    'maxWidth': '350px',
                    'borderRadius': '10px',
                    'boxShadow': '0 0 15px rgba(0,0,0,0.5)',
                    'marginBottom': '20px'
                }
            ))

        # 📝 Nombre y descripción
        contenido.extend([
            html.H2(carta["nombre"], style={'marginBottom': '10px'}),
            html.P(carta["descripcion"], style={'fontSize': '18px'})
        ])

        # 🎯 Opciones según tipo
        if tipo == "dropdown" and jugador_actual:
            opciones = [{'label': j, 'value': j} for j in jugadores if j != jugador_actual]
            contenido.extend([
                dcc.Dropdown(id='dropdown-carta', options=opciones, placeholder='Elige jugador...'),
                html.Br(),
                html.Button("Confirmar", id='btn-confirmar-carta', n_clicks=0)
            ])

        elif tipo == "confirmacion":
            contenido.extend([
                html.Div(id='flexiones-timer', style={'fontSize': '20px', 'margin': '10px'}),
                html.Button("✅ ¡Sí! Lo logré", id='btn-flexiones-si', n_clicks=0, style={'marginRight': '10px'}),
                html.Button("❌ No pude", id='btn-flexiones-no', n_clicks=0),
                dcc.Interval(id='interval-flexiones', interval=1000, n_intervals=0, max_intervals=40)
            ])
        elif tipo == "animacion":
            contenido.extend([
                html.Div(id='cara-cruz-resultado', style={
                    'fontSize': '28px',
                    'margin': '20px',
                    'color': '#ffe6ff',
                    'textShadow': '1px 1px 3px black',
                    'fontFamily': "'Cinzel', serif",
                    'animation': 'fadeIn 0.5s ease-in-out'
                }),
                dcc.Interval(id='interval-moneda', interval=500, n_intervals=0, max_intervals=12)
            ])

        # ❌ Botón de cerrar
        contenido.append(html.Button("Cerrar", id='btn-cerrar-carta', n_clicks=0, style={'marginTop': '20px'}))

        return html.Div(
            html.Div(contenido, className="card-container"),
            className="card-overlay-wrapper"
        )


        



    @app.callback(
        Output('store-active-card', 'data', allow_duplicate=True),
        Output('store-shots', 'data', allow_duplicate=True),  # ✅ aquí está el fix
        Input('btn-cerrar-carta', 'n_clicks'),
        State('store-active-card', 'data'),
        State('store-shots', 'data'),
        State('store-current-round-shots', 'data'),
        State('store-players', 'data'),
        prevent_initial_call=True
    )
    def cerrar_carta(n, carta, shots, round_shots, jugadores):
        if not n or not carta or "id" not in carta:
            raise PreventUpdate

        id_carta = carta["id"]
        jugador = carta.get("jugador") or carta.get("jugador_actual")

        # CREAMOS UNA COPIA para evitar modificar directamente el state original
        new_shots = shots.copy()

        if id_carta == "todos_1_shot":
            for j in jugadores:
                new_shots[j] = new_shots.get(j, 0) + 1

        elif id_carta == "toma_2_shots":
            new_shots[jugador] = new_shots.get(jugador, 0) + 2

        elif id_carta == "todos_menos_yo":
            for j in jugadores:
                if j != jugador:
                    new_shots[j] = new_shots.get(j, 0) + 2

        elif id_carta == "justiciero":
            try:
                # Solo consideramos jugadores que existen en `store-shots`
                if not new_shots or not isinstance(new_shots, dict):
                    raise PreventUpdate

                menor = min(new_shots.values())
                candidatos = [j for j, v in new_shots.items() if v == menor]

                if not candidatos:
                    raise PreventUpdate

                elegido = random.choice(candidatos)
                new_shots[elegido] = new_shots.get(elegido, 0) + 5
            except Exception as e:
                print(f"[ERROR Justiciero]: {e}")
                # Cierra carta, pero deja shots sin cambios
                return {}, shots

        elif id_carta == "shot_por_letra":
            inicial = jugador[0].lower()
            for j in jugadores:
                if j[0].lower() == inicial:
                    new_shots[j] = new_shots.get(j, 0) + 1

        elif id_carta == "se_libra":
            # Quita sus shots de la ronda (solo en stats)
            quitar = round_shots.get(jugador, 0)
            new_shots[jugador] = max(0, new_shots.get(jugador, 0) - quitar)

        # Limpiar carta y devolver nuevos shots
        return {}, new_shots



    @app.callback(
        Output('store-active-card', 'data', allow_duplicate=True),
        Output('store-shots', 'data', allow_duplicate=True),
        Input('btn-confirmar-carta', 'n_clicks'),
        State('dropdown-carta', 'value'),
        State('store-active-card', 'data'),
        State('store-current-round-shots', 'data'),
        State('store-shots', 'data'),
        prevent_initial_call=True
    )
    def confirmar_carta_dropdown(n, elegido, carta, shots_ronda, shots):
        if not n or not elegido or not carta:
            raise PreventUpdate

        jugador = carta.get("jugador")
        id_carta = carta.get("id")
        new_shots = shots.copy()

        if id_carta == "intercambio_shots":
            s1 = shots_ronda.get(jugador, 0)
            s2 = shots_ronda.get(elegido, 0)

            new_shots[jugador] = new_shots.get(jugador, 0) - s1 + s2
            new_shots[elegido] = new_shots.get(elegido, 0) - s2 + s1

        elif id_carta == "elige_quien_bebe":
            new_shots[elegido] = new_shots.get(elegido, 0) + 1

        else:
            raise PreventUpdate

        return {}, new_shots

    @app.callback(
        Output('store-active-card', 'data', allow_duplicate=True),
        Output('store-flexiones-tiempo', 'data', allow_duplicate=True),
        Input('btn-flexiones-si', 'n_clicks'),
        prevent_initial_call=True
    )
    def flexiones_si(n):
        if not n:
            raise PreventUpdate
        return {},0


    @app.callback(
        Output('store-active-card', 'data', allow_duplicate=True),
        Output('store-shots', 'data', allow_duplicate=True),
        Output('store-flexiones-tiempo', 'data', allow_duplicate=True),
        Input('btn-flexiones-no', 'n_clicks'),
        State('store-active-card', 'data'),
        State('store-shots', 'data'),
        prevent_initial_call=True
    )
    def flexiones_no(n, carta, shots):
        if not n or not carta or carta.get("id") != "flexiones_o_shots":
            raise PreventUpdate

        jugador = carta.get("jugador")
        new_shots = shots.copy()
        new_shots[jugador] = new_shots.get(jugador, 0) + 2
        return {}, new_shots,0

    @app.callback(
        Output('store-active-card', 'data', allow_duplicate=True),
        Output('store-shots', 'data', allow_duplicate=True),
        Input('interval-flexiones', 'n_intervals'),
        State('store-active-card', 'data'),
        State('store-shots', 'data'),
        prevent_initial_call=True
    )
    def flexiones_timeout(n, carta, shots):
        if n < 40 or not carta or carta.get("id") != "flexiones_o_shots":
            raise PreventUpdate

        jugador = carta.get("jugador")
        new_shots = shots.copy()
        new_shots[jugador] = new_shots.get(jugador, 0) + 2
        return {}, new_shots


    @app.callback(
        Output('flexiones-timer', 'children'),
        Output('store-flexiones-tiempo', 'data', allow_duplicate=True),
        Input('interval-flexiones', 'n_intervals'),
        prevent_initial_call=True
    )
    def actualizar_timer_flexiones(n):
        restante = 40 - n
        if restante < 0:
            restante = 0
        return f"⏳ Tiempo restante: {restante} segundos", restante
    
    @app.callback(
        Output('cara-cruz-resultado', 'children'),
        Input('interval-moneda', 'n_intervals'),
        prevent_initial_call=True
    )
    def actualizar_animacion_moneda(n):
        if n is None:
            raise PreventUpdate

        if n < 6:
            return "🪙 Girando..." if n % 2 == 0 else "Cara" if n % 3 == 0 else "Cruz"
        elif n == 6:
            resultado = random.choice(["Cara", "Cruz"])
            return f"🎉 Resultado: {resultado}"
        else:
            return dash.no_update


    @app.callback(
        Output('store-active-card', 'data', allow_duplicate=True),
        Output('store-shots', 'data', allow_duplicate=True),
        Input('interval-moneda', 'n_intervals'),
        State('store-active-card', 'data'),
        State('store-current-round-shots', 'data'),
        State('store-shots', 'data'),
        prevent_initial_call=True
    )
    def resolver_moneda(n, carta, round_shots, total_shots):
        if n is None or n < 12 or not carta or carta.get("id") != "cara_o_cruz":
            raise PreventUpdate

        jugador = carta.get("jugador")
        resultado = random.choice(["cara", "cruz"])

        new_shots = total_shots.copy()

        if resultado == "cara":
            new_shots[jugador] = new_shots.get(jugador, 0) + 2
        else:
            mitad = round_shots.get(jugador, 0) // 2
            new_shots[jugador] = max(0, new_shots.get(jugador, 0) - mitad)

        return {}, new_shots
