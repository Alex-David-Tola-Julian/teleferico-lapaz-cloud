import os
import requests
import pandas as pd
import numpy as np
from pandas.errors import ParserError
from app.core.config import settings

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
CSV_RUTA = os.path.join(ROOT_DIR, "data", "teleferico_lapaz.csv")

LINEAS_OFICIALES = [
    "Roja", "Amarilla", "Verde", "Azul", "Naranja",
    "Blanca", "Celeste", "Morada", "Café", "Plateada",
]

def normalizar_lineas(df: pd.DataFrame) -> pd.DataFrame:
    if "linea" not in df.columns:
        return df

    aliases = {
        "Cafe": "Café",
        "CAFÉ": "Café",
        "café": "Café",
    }

    df = df.copy()
    df["linea"] = df["linea"].astype(str).str.strip().replace(aliases)
    df = df[df["linea"].isin(LINEAS_OFICIALES)]
    return df

def normalizar_dias_semana(df: pd.DataFrame) -> pd.DataFrame:
    if "dia_semana" not in df.columns:
        return df

    aliases = {
        "Miercoles": "Miércoles",
        "Sabado": "Sábado",
        "Miércoles": "Miércoles",
        "Sábado": "Sábado",
    }

    df = df.copy()
    df["dia_semana"] = df["dia_semana"].astype(str).str.strip().replace(aliases)
    dias_validos = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    df = df[df["dia_semana"].isin(dias_validos)]
    return df

def cargar_datos_supabase():
    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        return None

    rest_url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/{settings.SUPABASE_TABLE}?select=*"
    headers = {
        "apikey": settings.SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_ANON_KEY}",
        "Accept": "application/json",
    }

    response = requests.get(rest_url, headers=headers)
    if response.status_code != 200:
        return None

    data = response.json()
    if not isinstance(data, list) or not data:
        return None

    return pd.DataFrame(data)

_global_df = None
_data_source = "csv"

def get_data():
    global _global_df, _data_source
    if _global_df is not None:
        return _global_df

    # Intentar cargar desde CSV local primero (rápido)
    if os.path.exists(CSV_RUTA):
        try:
            df = pd.read_csv(CSV_RUTA)
        except (ParserError, UnicodeDecodeError):
            df = pd.read_csv(CSV_RUTA, engine="python", on_bad_lines="skip", encoding="latin-1")
        _data_source = "csv"
    elif os.path.exists(CSV_RUTA + ".gz"):
        try:
            df = pd.read_csv(CSV_RUTA + ".gz", compression="gzip")
        except (ParserError, UnicodeDecodeError):
            df = pd.read_csv(CSV_RUTA + ".gz", engine="python", on_bad_lines="skip", encoding="latin-1", compression="gzip")
        _data_source = "csv.gz"
    # Si no hay CSV, intentar Supabase como fallback
    else:
        df_supabase = cargar_datos_supabase()
        if df_supabase is not None:
            df = df_supabase
            _data_source = "supabase"
        else:
            # Si todo falla, generar dataset
            import sys
            sys.path.append(ROOT_DIR)
            from data_generator import generar_dataset
            df = generar_dataset(fecha_inicio_str="2022-01-01", fecha_fin_str="2024-12-31")
            os.makedirs(os.path.dirname(CSV_RUTA), exist_ok=True)
            df.to_csv(CSV_RUTA, index=False)
            _data_source = "csv"

    df = normalizar_lineas(df)
    df = normalizar_dias_semana(df)
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df["hora"] = pd.to_numeric(df.get("hora"), errors="coerce")
    df["pasajeros"] = pd.to_numeric(df.get("pasajeros"), errors="coerce")
    df["saturacion"] = pd.to_numeric(df.get("saturacion"), errors="coerce")
    df = df.dropna(subset=["fecha", "hora", "pasajeros", "saturacion"])
    df["hora"] = df["hora"].astype(int)
    _global_df = df
    return df

def get_data_source() -> str:
    global _data_source
    return _data_source

def invalidate_cache():
    """Fuerza recarga del DataFrame en la próxima llamada a get_data()."""
    global _global_df
    _global_df = None

# Mapa de estaciones reales por línea para los tickets simulados
_ESTACIONES_POR_LINEA = {
    "Roja":     ["Taypi Uta (Estación Central)", "Ajayuni (Cementerio)", "Jach'a Qhathu (16 de Julio)"],
    "Amarilla": ["Sopocachi", "Miraflores", "Terminal"],
    "Verde":    ["Alto Obrajes", "Obrajes", "Irpavi"],
    "Azul":     ["El Alto", "Ciudad Satélite", "16 de Julio"],
    "Naranja":  ["Periférica", "Garita de Lima", "Cementerio", "Ceja"],
    "Blanca":   ["Villa Adela", "Senkata", "El Tejar"],
    "Celeste":  ["Pura Pura", "Villa Fátima", "Achacachi"],
    "Morada":   ["El Kenko", "Parque Urbano", "Mi Teleférico Central"],
    "Café":     ["Kupini", "Seguencoma", "Calacoto"],
    "Plateada": ["Libertad", "San Juan", "Río Seco"],
}

_COLORES_LINEA = {
    "Roja": "#E63946", "Amarilla": "#FFD700", "Verde": "#2DC653",
    "Azul": "#0077B6", "Naranja": "#FB8500", "Blanca": "#E8EAF0",
    "Celeste": "#48CAE4", "Morada": "#7B2FBE", "Café": "#8B5E3C", "Plateada": "#B0B0B0",
}

_COORDS_LINEA = {
    "Roja":     (-16.5000, -68.1500), "Amarilla": (-16.5100, -68.1400),
    "Verde":    (-16.5200, -68.1300), "Azul":     (-16.4900, -68.1600),
    "Naranja":  (-16.4913, -68.1384), "Blanca":   (-16.5300, -68.1200),
    "Celeste":  (-16.5050, -68.1450), "Morada":   (-16.5150, -68.1350),
    "Café":     (-16.5250, -68.1250), "Plateada": (-16.4800, -68.1700),
}

_DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

def registrar_ticket(linea: str, pasajeros: int) -> dict:
    """Añade un nuevo registro al CSV y recarga el cache."""
    import random
    from datetime import datetime

    if linea not in LINEAS_OFICIALES:
        raise ValueError(f"Línea inválida: {linea}")
    if pasajeros <= 0:
        raise ValueError("El número de pasajeros debe ser > 0")

    now = datetime.now()
    dia_idx = now.weekday()  # 0=lunes
    dia_semana = _DIAS_SEMANA[dia_idx]
    fecha_str = now.strftime("%Y-%m-%d")
    hora = now.hour

    estaciones = _ESTACIONES_POR_LINEA.get(linea, ["Estación Central"])
    estacion = random.choice(estaciones)
    lat, lon = _COORDS_LINEA.get(linea, (-16.5, -68.15))
    color_linea = _COLORES_LINEA.get(linea, "#FFFFFF")
    saturacion = min(100.0, round(random.uniform(30, 95), 2))

    nuevo = {
        "fecha": fecha_str,
        "hora": hora,
        "dia_semana": dia_semana,
        "linea": linea,
        "color_linea": color_linea,
        "estacion": estacion,
        "latitud": lat,
        "longitud": lon,
        "pasajeros": pasajeros,
        "saturacion": saturacion,
        "calibrado": True,
        "factor_escala": 1.0,
    }

    # Añadir al CSV
    nueva_fila = pd.DataFrame([nuevo])
    csv_existe = os.path.exists(CSV_RUTA)
    nueva_fila.to_csv(CSV_RUTA, mode="a", header=not csv_existe, index=False)

    # Añadir también al DataFrame en memoria sin recargar todo el CSV
    global _global_df
    if _global_df is not None:
        nueva_fila["fecha"] = pd.to_datetime(nueva_fila["fecha"])
        nueva_fila["hora"] = nueva_fila["hora"].astype(int)
        _global_df = pd.concat([_global_df, nueva_fila], ignore_index=True)

    # Subir solo el registro nuevo a Supabase (si está configurado)
    try:
        supabase_url = settings.SUPABASE_URL
        supabase_key = settings.SUPABASE_ANON_KEY
        supabase_table = settings.SUPABASE_TABLE

        if supabase_url and supabase_key and supabase_table:
            rest_url = f"{supabase_url.rstrip('/')}/rest/v1/{supabase_table}"
            headers = {
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal",
            }
            requests.post(rest_url, json=nuevo, headers=headers)
    except Exception:
        pass

    return nuevo

def filter_data(params):
    df = get_data()
    start_dt = pd.to_datetime(params.fecha_inicio)
    end_dt = pd.to_datetime(params.fecha_fin) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

    mask = (
        (df["fecha"] >= start_dt) &
        (df["fecha"] <= end_dt) &
        (df["linea"].isin(params.lineas)) &
        (df["hora"] >= params.hora_min) &
        (df["hora"] <= params.hora_max) &
        (df["dia_semana"].isin(params.dias_semana))
    )
    return df[mask].copy()
