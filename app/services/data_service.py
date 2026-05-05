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

    df = cargar_datos_supabase()
    if df is not None:
        df = normalizar_lineas(df)
        df = normalizar_dias_semana(df)
        if "fecha" in df.columns:
            df["fecha"] = pd.to_datetime(df["fecha"])
            df["fecha"] = df["fecha"].dt.tz_localize(None)
        _data_source = "supabase"
        _global_df = df
        return df

    if os.path.exists(CSV_RUTA):
        try:
            df = pd.read_csv(CSV_RUTA)
        except (ParserError, UnicodeDecodeError):
            df = pd.read_csv(CSV_RUTA, engine="python", on_bad_lines="skip", encoding="latin-1")
        _data_source = "csv"
    else:
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
