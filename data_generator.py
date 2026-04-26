"""
data_generator.py
Generador de datos simulados para el sistema Mi Teleférico - La Paz, Bolivia
Grupo 19 - Computación en la Nube - UMSA
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# ─── Configuración de líneas del teleférico ───────────────────────────────────
LINEAS = {
    "Roja":     {"capacidad_hora": 3200, "estaciones": ["Terminal Rojo Sur", "Parque Urbano", "Pura Pura", "Ceja El Alto Norte"], "color": "#E63946"},
    "Amarilla": {"capacidad_hora": 2800, "estaciones": ["Armonia", "Ciudad Satélite", "16 de Julio", "Villa Adela"], "color": "#FFB703"},
    "Verde":    {"capacidad_hora": 3000, "estaciones": ["San Jorge", "Sopocachi", "Belén", "Achumani"], "color": "#2DC653"},
    "Azul":     {"capacidad_hora": 2600, "estaciones": ["Cementerio", "Garita de Lima", "Periférica", "Villa Fátima"], "color": "#0077B6"},
    "Naranja":  {"capacidad_hora": 2400, "estaciones": ["Senkata", "El Alto Centro", "Mercado Rodríguez", "Obrajes"], "color": "#FB8500"},
    "Celeste":  {"capacidad_hora": 2200, "estaciones": ["Qhana Punita", "Rosas Pampa", "5 Esquinas", "Miraflores"], "color": "#48CAE4"},
    "Blanca":   {"capacidad_hora": 2000, "estaciones": ["Jupapina", "Cota Cota", "Irpavi", "Pedregal"], "color": "#F1FAEE"},
    "Café":     {"capacidad_hora": 1800, "estaciones": ["Terminal Sur Café", "Villarroel", "Miraflores Café", "Triangulo"], "color": "#8B5E3C"},
    "Plateada": {"capacidad_hora": 3400, "estaciones": ["El Alto Sur", "Senkata Plateada", "Los Andes", "La Ceja"], "color": "#ADB5BD"},
    "Dorada":   {"capacidad_hora": 3100, "estaciones": ["Terminal Dorada", "Río Seco", "Ciudad del Niño", "Garita"], "color": "#D4AF37"},
    "Morada":   {"capacidad_hora": 2900, "estaciones": ["Morada Sur", "Pampahasi", "Alto Obrajes", "Morada Norte"], "color": "#7209B7"},
}

# Coordenadas reales aproximadas de La Paz / El Alto para el mapa
COORDENADAS_ESTACIONES = {
    # Roja
    "Terminal Rojo Sur":   (-16.530, -68.119),
    "Parque Urbano":       (-16.520, -68.115),
    "Pura Pura":           (-16.504, -68.113),
    "Ceja El Alto Norte":  (-16.497, -68.115),
    # Amarilla
    "Armonia":             (-16.508, -68.131),
    "Ciudad Satélite":     (-16.503, -68.138),
    "16 de Julio":         (-16.499, -68.143),
    "Villa Adela":         (-16.494, -68.148),
    # Verde
    "San Jorge":           (-16.507, -68.123),
    "Sopocachi":           (-16.513, -68.127),
    "Belén":               (-16.520, -68.130),
    "Achumani":            (-16.535, -68.125),
    # Azul
    "Cementerio":          (-16.490, -68.120),
    "Garita de Lima":      (-16.495, -68.118),
    "Periférica":          (-16.500, -68.116),
    "Villa Fátima":        (-16.505, -68.114),
    # Naranja
    "Senkata":             (-16.478, -68.154),
    "El Alto Centro":      (-16.485, -68.148),
    "Mercado Rodríguez":   (-16.497, -68.136),
    "Obrajes":             (-16.530, -68.115),
    # Celeste
    "Qhana Punita":        (-16.472, -68.165),
    "Rosas Pampa":         (-16.480, -68.158),
    "5 Esquinas":          (-16.493, -68.142),
    "Miraflores":          (-16.508, -68.110),
    # Blanca
    "Jupapina":            (-16.550, -68.105),
    "Cota Cota":           (-16.542, -68.108),
    "Irpavi":              (-16.535, -68.112),
    "Pedregal":            (-16.528, -68.118),
    # Café
    "Terminal Sur Café":   (-16.555, -68.101),
    "Villarroel":          (-16.545, -68.104),
    "Miraflores Café":     (-16.510, -68.109),
    "Triangulo":           (-16.502, -68.107),
    # Plateada
    "El Alto Sur":         (-16.490, -68.145),
    "Senkata Plateada":    (-16.480, -68.150),
    "Los Andes":           (-16.474, -68.156),
    "La Ceja":             (-16.501, -68.133),
    # Dorada
    "Terminal Dorada":     (-16.465, -68.170),
    "Río Seco":            (-16.470, -68.162),
    "Ciudad del Niño":     (-16.475, -68.155),
    "Garita":              (-16.483, -68.147),
    # Morada
    "Morada Sur":          (-16.538, -68.108),
    "Pampahasi":           (-16.525, -68.106),
    "Alto Obrajes":        (-16.518, -68.110),
    "Morada Norte":        (-16.510, -68.112),
}

def factor_hora(hora: int) -> float:
    """Curva de demanda realista por hora del día."""
    factores = {
        0: 0.02, 1: 0.01, 2: 0.01, 3: 0.01, 4: 0.02, 5: 0.08,
        6: 0.45, 7: 0.90, 8: 1.00, 9: 0.75, 10: 0.55, 11: 0.50,
        12: 0.65, 13: 0.70, 14: 0.60, 15: 0.55, 16: 0.65, 17: 0.85,
        18: 0.95, 19: 0.80, 20: 0.55, 21: 0.35, 22: 0.18, 23: 0.07,
    }
    return factores.get(hora, 0.5)

def factor_dia(dia_semana: int) -> float:
    """Factor por día de la semana (0=Lunes, 6=Domingo)."""
    factores = {0: 1.0, 1: 0.98, 2: 0.97, 3: 0.99, 4: 1.05, 5: 0.80, 6: 0.55}
    return factores.get(dia_semana, 1.0)

def generar_dataset(dias: int = 180, seed: int = 42) -> pd.DataFrame:
    """
    Genera dataset de pasajeros por línea, estación, fecha y hora.
    Por defecto 6 meses de datos históricos.
    """
    np.random.seed(seed)
    random.seed(seed)

    fecha_inicio = datetime.now() - timedelta(days=dias)
    registros = []

    for linea, info in LINEAS.items():
        cap = info["capacidad_hora"]
        estaciones = info["estaciones"]

        for dia_offset in range(dias):
            fecha = fecha_inicio + timedelta(days=dia_offset)
            dow = fecha.weekday()
            fd = factor_dia(dow)

            for hora in range(5, 23):  # Operación 05:00 - 22:59
                fh = factor_hora(hora)
                base = cap * fh * fd
                ruido = np.random.normal(0, base * 0.08)
                pasajeros_total = max(0, int(base + ruido))

                # Distribuir por estación (más tráfico en extremos)
                pesos = [1.4, 0.8, 0.8, 1.4] if len(estaciones) == 4 else [1.0] * len(estaciones)
                suma_pesos = sum(pesos)

                for i, estacion in enumerate(estaciones):
                    lat, lon = COORDENADAS_ESTACIONES.get(estacion, (-16.5, -68.15))
                    pasajeros_est = int(pasajeros_total * (pesos[i] / suma_pesos) * np.random.uniform(0.85, 1.15))
                    saturacion = min(100, round((pasajeros_est / (cap * 0.25)) * 100, 1))

                    registros.append({
                        "fecha":       fecha.strftime("%Y-%m-%d"),
                        "hora":        hora,
                        "dia_semana":  ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"][dow],
                        "linea":       linea,
                        "color_linea": info["color"],
                        "estacion":    estacion,
                        "latitud":     lat + np.random.uniform(-0.001, 0.001),
                        "longitud":    lon + np.random.uniform(-0.001, 0.001),
                        "pasajeros":   max(0, pasajeros_est),
                        "saturacion":  saturacion,
                    })

    df = pd.DataFrame(registros)
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df

def guardar_datos(df: pd.DataFrame, ruta: str = "data/teleferico_lapaz.csv"):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    df.to_csv(ruta, index=False)
    print(f"✅ Dataset guardado: {ruta} ({len(df):,} registros)")
    return ruta

if __name__ == "__main__":
    print("🚡 Generando datos del Mi Teleférico - La Paz...")
    df = generar_dataset(dias=180)
    guardar_datos(df)
    print(df.describe())