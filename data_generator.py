"""
data_generator.py
Generador de datos calibrados para el sistema Mi Teleférico - La Paz, Bolivia
Grupo 19 - Computación en la Nube - UMSA

Estrategia Opción C:
  - Datos reales anuales del INE como ancla (pasajeros totales por línea/año)
  - Desagregación diaria/horaria mediante simulación calibrada
  - Factor de escala = real_anual / simulado_anual  →  ajusta cada registro
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# ─── Datos reales INE: pasajeros anuales por línea ────────────────────────────
# Fuente: "Vidas transportadas por año y por línea" - INE Bolivia
# Nota: None = línea aún no operaba ese año
PASAJEROS_REALES_INE = {
    #  año:  { Roja,        Amarilla,     Verde,       Azul,        Naranja,     Morada,       Blanca,      Celeste,     Café,    Plateada }
    2015: {"Roja": 7_375_344,  "Amarilla": 13_837_122, "Verde": 4_176_116, "Azul": None,       "Naranja": None,      "Morada": None,        "Blanca": None,      "Celeste": None,      "Café": None,    "Plateada": None},
    2016: {"Roja": 8_510_264,  "Amarilla": 15_163_793, "Verde": 4_287_764, "Azul": None,       "Naranja": None,      "Morada": None,        "Blanca": None,      "Celeste": None,      "Café": None,    "Plateada": None},
    2017: {"Roja": 12_610_026, "Amarilla": 16_489_537, "Verde": 4_288_774, "Azul": 6_455_443,  "Naranja": 2_223_773, "Morada": None,        "Blanca": None,      "Celeste": None,      "Café": None,    "Plateada": None},
    2018: {"Roja": 15_389_914, "Amarilla": 16_852_585, "Verde": 6_230_650, "Azul": 8_057_653,  "Naranja": 9_003_990, "Morada": 5_226_263,   "Blanca": 4_890_884, "Celeste": 3_732_494, "Café": 31_748,  "Plateada": None},
    2019: {"Roja": 12_175_997, "Amarilla": 16_350_645, "Verde": 8_250_354, "Azul": 9_846_997,  "Naranja": 8_845_115, "Morada": 21_078_126,  "Blanca": 6_646_443, "Celeste": 6_529_295, "Café": 892_094, "Plateada": 6_227_126},
    2020: {"Roja": 5_431_097,  "Amarilla": 6_572_117,  "Verde": 2_800_529, "Azul": 5_048_187,  "Naranja": 3_422_031, "Morada": 9_202_360,   "Blanca": 2_321_184, "Celeste": 2_074_146, "Café": 344_479, "Plateada": 3_677_015},
    2021: {"Roja": 7_106_133,  "Amarilla": 8_981_459,  "Verde": 3_243_512, "Azul": 6_857_851,  "Naranja": 3_828_539, "Morada": 13_568_448,  "Blanca": 2_346_010, "Celeste": 2_083_464, "Café": 340_571, "Plateada": 5_035_677},
    2022: {"Roja": 8_117_101,  "Amarilla": 10_846_086, "Verde": 4_123_473, "Azul": 8_504_331,  "Naranja": 4_583_782, "Morada": 17_813_311,  "Blanca": 2_900_774, "Celeste": 2_642_157, "Café": 357_124, "Plateada": 6_469_740},
    2023: {"Roja": 8_503_943,  "Amarilla": 11_521_117, "Verde": 4_392_608, "Azul": 9_100_594,  "Naranja": 4_880_051, "Morada": 20_763_857,  "Blanca": 3_156_497, "Celeste": 2_787_709, "Café": 370_477, "Plateada": 7_448_102},
    2024: {"Roja": 9_527_945,  "Amarilla": 12_353_813, "Verde": 4_699_838, "Azul": 10_364_072, "Naranja": 5_187_834, "Morada": 21_126_549,  "Blanca": 3_350_347, "Celeste": 3_193_582, "Café": 376_352, "Plateada": 8_159_819},
}

# Líneas con datos reales. Dorada no aparece en el INE → se mantiene simulada pura.
LINEAS_CON_DATOS_REALES = set()
for anio_data in PASAJEROS_REALES_INE.values():
    for linea, val in anio_data.items():
        if val is not None:
            LINEAS_CON_DATOS_REALES.add(linea)

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
    "Terminal Rojo Sur":   (-16.530, -68.119),
    "Parque Urbano":       (-16.520, -68.115),
    "Pura Pura":           (-16.504, -68.113),
    "Ceja El Alto Norte":  (-16.497, -68.115),
    "Armonia":             (-16.508, -68.131),
    "Ciudad Satélite":     (-16.503, -68.138),
    "16 de Julio":         (-16.499, -68.143),
    "Villa Adela":         (-16.494, -68.148),
    "San Jorge":           (-16.507, -68.123),
    "Sopocachi":           (-16.513, -68.127),
    "Belén":               (-16.520, -68.130),
    "Achumani":            (-16.535, -68.125),
    "Cementerio":          (-16.490, -68.120),
    "Garita de Lima":      (-16.495, -68.118),
    "Periférica":          (-16.500, -68.116),
    "Villa Fátima":        (-16.505, -68.114),
    "Senkata":             (-16.478, -68.154),
    "El Alto Centro":      (-16.485, -68.148),
    "Mercado Rodríguez":   (-16.497, -68.136),
    "Obrajes":             (-16.530, -68.115),
    "Qhana Punita":        (-16.472, -68.165),
    "Rosas Pampa":         (-16.480, -68.158),
    "5 Esquinas":          (-16.493, -68.142),
    "Miraflores":          (-16.508, -68.110),
    "Jupapina":            (-16.550, -68.105),
    "Cota Cota":           (-16.542, -68.108),
    "Irpavi":              (-16.535, -68.112),
    "Pedregal":            (-16.528, -68.118),
    "Terminal Sur Café":   (-16.555, -68.101),
    "Villarroel":          (-16.545, -68.104),
    "Miraflores Café":     (-16.510, -68.109),
    "Triangulo":           (-16.502, -68.107),
    "El Alto Sur":         (-16.490, -68.145),
    "Senkata Plateada":    (-16.480, -68.150),
    "Los Andes":           (-16.474, -68.156),
    "La Ceja":             (-16.501, -68.133),
    "Terminal Dorada":     (-16.465, -68.170),
    "Río Seco":            (-16.470, -68.162),
    "Ciudad del Niño":     (-16.475, -68.155),
    "Garita":              (-16.483, -68.147),
    "Morada Sur":          (-16.538, -68.108),
    "Pampahasi":           (-16.525, -68.106),
    "Alto Obrajes":        (-16.518, -68.110),
    "Morada Norte":        (-16.510, -68.112),
}


# ─── Curvas de demanda ────────────────────────────────────────────────────────

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


# ─── Calibración: factor de escala por línea y año ───────────────────────────

def calcular_pasajeros_simulados_anuales(linea: str, anio: int, cap: int) -> float:
    """
    Calcula cuántos pasajeros produciría la simulación pura en un año dado,
    sin ruido (valor esperado). Se usa como denominador del factor de escala.
    """
    fecha_inicio = datetime(anio, 1, 1)
    fecha_fin    = datetime(anio, 12, 31)
    total = 0.0
    fecha = fecha_inicio
    while fecha <= fecha_fin:
        fd = factor_dia(fecha.weekday())
        for hora in range(5, 23):
            fh = factor_hora(hora)
            total += cap * fh * fd
        fecha += timedelta(days=1)
    # Los pasajeros del generador son la suma de todas las estaciones (4 estaciones × pesos normalizados = 1×total)
    # pesos [1.4, 0.8, 0.8, 1.4] suman 4.4, cada estacion recibe fraccion → suma total = pasajeros_total (sin cambio neto)
    return total

def construir_factores_escala() -> dict:
    """
    Devuelve dict[año][linea] = factor_escala.
    factor_escala = pasajeros_reales_INE / pasajeros_simulados_esperados
    Si no hay dato real para ese año/linea → factor = 1.0 (simulación pura).
    """
    factores = {}
    for anio, datos_lineas in PASAJEROS_REALES_INE.items():
        factores[anio] = {}
        for linea, real in datos_lineas.items():
            if real is None:
                factores[anio][linea] = None  # línea no operaba
                continue
            cap = LINEAS[linea]["capacidad_hora"]
            simulado = calcular_pasajeros_simulados_anuales(linea, anio, cap)
            factores[anio][linea] = real / simulado if simulado > 0 else 1.0
    return factores


# ─── Generador principal ──────────────────────────────────────────────────────

def generar_dataset(
    fecha_inicio_str: str = None,
    fecha_fin_str: str = None,
    dias: int = None,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Genera dataset calibrado de pasajeros por línea, estación, fecha y hora.

    Parámetros (usa uno de los dos modos):
      - fecha_inicio_str / fecha_fin_str : rango explícito  "YYYY-MM-DD"
      - dias                              : últimos N días desde hoy (modo legado)

    La calibración aplica el factor de escala INE por año y línea.
    Años sin dato real (Dorada, o años fuera del INE) usan simulación pura.
    """
    np.random.seed(seed)
    random.seed(seed)

    # Resolver rango de fechas
    if fecha_inicio_str and fecha_fin_str:
        fecha_ini = datetime.strptime(fecha_inicio_str, "%Y-%m-%d")
        fecha_fin = datetime.strptime(fecha_fin_str,    "%Y-%m-%d")
    else:
        n = dias if dias is not None else 180
        fecha_fin = datetime.now()
        fecha_ini = fecha_fin - timedelta(days=n)

    # Pre-calcular factores de escala
    print("⚙️  Calculando factores de calibración INE...")
    factores_escala = construir_factores_escala()

    # Reporte de factores
    print("\n📊 Factores de escala por año y línea (real / simulado):")
    for anio in sorted(factores_escala.keys()):
        fila = f"  {anio}: "
        partes = []
        for linea, f in factores_escala[anio].items():
            if f is not None:
                partes.append(f"{linea}={f:.3f}")
        print(fila + " | ".join(partes))

    registros = []
    total_dias = (fecha_fin - fecha_ini).days + 1

    for linea, info in LINEAS.items():
        cap      = info["capacidad_hora"]
        estaciones = info["estaciones"]
        pesos    = [1.4, 0.8, 0.8, 1.4] if len(estaciones) == 4 else [1.0] * len(estaciones)
        suma_pesos = sum(pesos)

        for dia_offset in range(total_dias):
            fecha  = fecha_ini + timedelta(days=dia_offset)
            anio   = fecha.year
            dow    = fecha.weekday()
            fd     = factor_dia(dow)

            # Obtener factor de escala para este año/línea
            factor = 1.0  # default: simulación pura
            if anio in factores_escala and linea in factores_escala[anio]:
                f = factores_escala[anio][linea]
                if f is not None:
                    factor = f
                else:
                    # Línea no operaba este año → skip
                    continue

            for hora in range(5, 23):
                fh   = factor_hora(hora)
                base = cap * fh * fd

                # Ruido proporcional + calibración
                ruido = np.random.normal(0, base * 0.08)
                pasajeros_total = max(0, (base + ruido) * factor)

                for i, estacion in enumerate(estaciones):
                    lat, lon = COORDENADAS_ESTACIONES.get(estacion, (-16.5, -68.15))
                    pasajeros_est = int(
                        pasajeros_total
                        * (pesos[i] / suma_pesos)
                        * np.random.uniform(0.85, 1.15)
                    )
                    pasajeros_est = max(0, pasajeros_est)

                    # Saturación: pasajeros / (capacidad_hora × 0.25 por estación)
                    saturacion = min(100, round((pasajeros_est / (cap * 0.25)) * 100, 1))

                    registros.append({
                        "fecha":        fecha.strftime("%Y-%m-%d"),
                        "hora":         hora,
                        "dia_semana":   ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"][dow],
                        "linea":        linea,
                        "color_linea":  info["color"],
                        "estacion":     estacion,
                        "latitud":      lat + np.random.uniform(-0.001, 0.001),
                        "longitud":     lon + np.random.uniform(-0.001, 0.001),
                        "pasajeros":    pasajeros_est,
                        "saturacion":   saturacion,
                        "calibrado":    factor != 1.0,  # útil para auditoría
                        "factor_escala": round(factor, 4),
                    })

    df = pd.DataFrame(registros)
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df


def guardar_datos(df: pd.DataFrame, ruta: str = "data/teleferico_lapaz.csv"):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    df.to_csv(ruta, index=False)
    print(f"\n✅ Dataset guardado: {ruta} ({len(df):,} registros)")
    return ruta


def verificar_calibracion(df: pd.DataFrame):
    """
    Compara totales anuales simulados calibrados vs datos reales INE.
    Imprime tabla de error porcentual por línea y año.
    """
    print("\n" + "="*70)
    print("VERIFICACIÓN DE CALIBRACIÓN — Comparación vs INE")
    print("="*70)

    df_cal = df[df["calibrado"] == True].copy()
    df_cal["anio"] = df_cal["fecha"].dt.year

    # Suma por año/línea (todos los registros de estaciones = pasajeros totales / 4 estaciones aprox.)
    # Para obtener el total de la línea sumamos todas las estaciones y dividimos por número de estaciones
    resumen = (
        df_cal.groupby(["anio", "linea"])["pasajeros"]
        .sum()
        .reset_index()
        .rename(columns={"pasajeros": "simulado_total"})
    )
    # Ajuste: el total sumado es la suma de 4 estaciones con pesos, que ya reflejan pasajeros únicos.
    # Los datos INE son pasajeros totales de la línea (equivalente a la suma ponderada).

    errores = []
    for _, row in resumen.iterrows():
        anio, linea, sim = int(row["anio"]), row["linea"], row["simulado_total"]
        real = PASAJEROS_REALES_INE.get(anio, {}).get(linea)
        if real:
            err_pct = abs(sim - real) / real * 100
            errores.append({"Año": anio, "Línea": linea, "Real INE": real, "Simulado": int(sim), "Error %": round(err_pct, 2)})

    if errores:
        df_err = pd.DataFrame(errores).sort_values(["Año", "Línea"])
        print(df_err.to_string(index=False))
        print(f"\nError promedio: {df_err['Error %'].mean():.2f}%")
        print(f"Error máximo:   {df_err['Error %'].max():.2f}%")
    else:
        print("No se encontraron años calibrados en el dataset generado.")


# ─── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🚡 Generando datos calibrados del Mi Teleférico - La Paz...")
    print("   Modo: datos reales INE (2015-2024) + desagregación horaria simulada\n")

    # Generar los años con datos reales completos (2019-2024)
    df = generar_dataset(fecha_inicio_str="2019-01-01", fecha_fin_str="2024-12-31")

    guardar_datos(df)
    verificar_calibracion(df)

    print("\n📈 Resumen estadístico:")
    print(df[["pasajeros", "saturacion", "factor_escala"]].describe().round(2))