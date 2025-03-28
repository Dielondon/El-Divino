import random
from typing import List, Dict, Tuple

def generar_ronda(jugadores: List[str], tipo_trago: str) -> Tuple[int, Dict[str, int]]:
    if not jugadores:
        return 0, {}

    # Paso 1: calcular tiempo
    tiempos_base = [10, 20, 30, 40, 50, 60]
    tiempo_base = random.choice(tiempos_base)

    if tipo_trago == 'soft':
        factor = random.uniform(0.6, 1.1)
    elif tipo_trago == 'strong':
        factor = random.uniform(1.1, 1.6)
    else:  # random
        factor = random.uniform(0.6, 1.6)

    tiempo_total = int(len(jugadores) * tiempo_base * factor)

    # Paso 2: asignar shots hasta que todos salgan al menos una vez
    shots = {jugador: 0 for jugador in jugadores}
    jugadores_ya_salieron = set()

    while len(jugadores_ya_salieron) < len(jugadores):
        jugador = random.choice(jugadores)
        shot = random.randint(0, 2)

        shots[jugador] += shot
        jugadores_ya_salieron.add(jugador)

    return tiempo_total, shots


def generar_carta(jugador_actual, jugadores):
    cartas = [
        {
            "id": "todos_1_shot",
            "nombre": "🥃 Todos toman 1 shot",
            "descripcion": "¡Salud! Todos los jugadores deben tomar 1 shot.",
            "tipo": "auto",
            "imagen": "todos_1_shot.png"
        },
        {
            "id": "intercambio_shots",
            "nombre": "🔄 Intercambio de shots",
            "descripcion": "Elige a un jugador para intercambiar los shots de esta ronda.",
            "tipo": "dropdown",
            "imagen": "intercambio_shots.png"
        },
        {
            "id": "toma_2_shots",
            "nombre": "🍺 Toma 2 shots",
            "descripcion": "Sin quejarse. Te tocan 2 shots más.",
            "tipo": "auto",
            "imagen": "toma_2_shots.png"
        },
        {
            "id": "se_libra",
            "nombre": "🛡️ Se libra de beber",
            "descripcion": "Te salvas de los shots de esta ronda. Qué suerte.",
            "tipo": "auto",
            "imagen": "se_libra.png"
        },
        {
            "id": "elige_quien_bebe",
            "nombre": "🎯 Elige a alguien para beber",
            "descripcion": "Selecciona a alguien que deba tomar 1 shot.",
            "tipo": "dropdown",
            "imagen": "elige_quien_bebe.png"
        },
        {
            "id": "flexiones_o_shots",
            "nombre": "💪 10 flexiones o 2 shots",
            "descripcion": "¿Haces las 10 flexiones? Si no, te tocan 2 shots.",
            "tipo": "confirmacion",
            "imagen": "flexiones_o_shots.png"
        },
        {
            "id": "shot_por_letra",
            "nombre": "🔤 Shot por nombre",
            "descripcion": "Todos los que tienen un nombre que empieza como el tuyo toman 1 shot.",
            "tipo": "auto",
            "imagen": "shot_por_letra.png"
        },
        {
            "id": "justiciero",
            "nombre": "⚖️ Justiciero",
            "descripcion": "El jugador con menos shots debe tomar 5 más.",
            "tipo": "auto",
            "imagen": "justiciero.png"
        },
        {
            "id": "todos_menos_yo",
            "nombre": "🚫 Todos menos yo",
            "descripcion": "Todos beben 2 shots... menos tú.",
            "tipo": "auto",
            "imagen": "todos_menos_yo.png"
        },
        {
            "id": "cara_o_cruz",
            "nombre": "🪙 Cara o Cruz",
            "descripcion": "Si sale cara, bebes 2 shots. Si sale cruz, tus shots de esta ronda se reducen a la mitad.",
            "tipo": "animacion",
            "imagen": "cara_o_cruz.png"
        }
    ]
    carta = random.choice(cartas)
    carta["jugador"] = jugador_actual  # 🔥 necesario para efectos personalizados
    return carta
