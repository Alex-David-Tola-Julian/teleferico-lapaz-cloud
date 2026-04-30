from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import numpy as np
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pandas.errors import ParserError
import warnings
warnings.filterwarnings("ignore")

load_dotenv()

app = FastAPI(title="Teleférico La Paz Cloud Analytics API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Carga de datos ────────────────────────────────────────────────────────────
CSV_RUTA = os.path.join(os.path.dirname(__file__), "data", "teleferico_lapaz.csv")
LINEAS_OFICIALES = [
    "Roja",
    "Amarilla",
    "Verde",
    "Azul",
    "Naranja",
    "Blanca",
    "Celeste",
    "Morada",
    "Café",
    "Plateada",
]


def normalizar_lineas(df: pd.DataFrame) -> pd.DataFrame:
    if "linea" not in df.columns:
        return df

    aliases = {
        "Cafe": "Café",
        "CAFÉ": "Café",
        "cafÃ©": "Café",
    }

    df = df.copy()
    df["linea"] = df["linea"].astype(str).str.strip().replace(aliases)
    # Keep only official Mi Teleférico lines to avoid malformed CSV/Supabase values.
    df = df[df["linea"].isin(LINEAS_OFICIALES)]
    return df


def normalizar_dias_semana(df: pd.DataFrame) -> pd.DataFrame:
    if "dia_semana" not in df.columns:
        return df

    aliases = {
        "Miercoles": "Miércoles",
        "Sabado": "Sábado",
        "MiÃ©rcoles": "Miércoles",
        "SÃ¡bado": "Sábado",
    }

    df = df.copy()
    df["dia_semana"] = df["dia_semana"].astype(str).str.strip().replace(aliases)
    dias_validos = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    df = df[df["dia_semana"].isin(dias_validos)]
    return df

def cargar_datos_supabase():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    table_name = os.getenv("SUPABASE_TABLE", "teleferico")

    if not url or not key:
        return None

    rest_url = f"{url.rstrip('/')}/rest/v1/{table_name}?select=*"
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Accept": "application/json",
    }

    response = requests.get(rest_url, headers=headers)
    if response.status_code != 200:
        return None

    data = response.json()
    if not isinstance(data, list) or not data:
        return None

    df = pd.DataFrame(data)
    return df

# Global cache for data
_global_df = None

def get_data():
    global _global_df
    if _global_df is not None:
        return _global_df

    df = cargar_datos_supabase()
    if df is not None:
        df = normalizar_lineas(df)
        df = normalizar_dias_semana(df)
        if "fecha" in df.columns:
            df["fecha"] = pd.to_datetime(df["fecha"])
            df["fecha"] = df["fecha"].dt.tz_localize(None)
        _global_df = df
        return df

    if os.path.exists(CSV_RUTA):
        try:
            df = pd.read_csv(CSV_RUTA)
        except (ParserError, UnicodeDecodeError):
            # Some rows/bytes in the dataset may be malformed; keep the service
            # available by skipping invalid lines and tolerating encoding issues.
            df = pd.read_csv(
                CSV_RUTA,
                engine="python",
                on_bad_lines="skip",
                encoding="latin-1",
            )
    else:
        from data_generator import generar_dataset
        df = generar_dataset(fecha_inicio_str="2022-01-01", fecha_fin_str="2024-12-31")
        os.makedirs(os.path.dirname(CSV_RUTA), exist_ok=True)
        df.to_csv(CSV_RUTA, index=False)

    # Normalize types and drop malformed rows that can appear in CSV files.
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

# Modelos Pydantic
class FilterParams(BaseModel):
    fecha_inicio: str
    fecha_fin: str
    lineas: List[str]
    hora_min: int
    hora_max: int
    dias_semana: List[str]

def filter_data(params: FilterParams):
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

@app.get("/api/config")
def get_config():
    df = get_data()
    fecha_min = df["fecha"].min().date().isoformat()
    fecha_max = df["fecha"].max().date().isoformat()
    lineas_disp = LINEAS_OFICIALES
    dias_orden = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    return {
        "fecha_min": fecha_min,
        "fecha_max": fecha_max,
        "lineas_disp": lineas_disp,
        "dias_orden": dias_orden
    }

@app.post("/api/metrics")
def get_metrics(params: FilterParams):
    dff = filter_data(params)
    if dff.empty:
        return {"total_pax": 0, "prom_diario": 0, "sat_prom": 0, "linea_top": "—"}

    total_pax = int(dff["pasajeros"].sum())
    prom_diario = float(dff.groupby("fecha")["pasajeros"].sum().mean())
    sat_prom = float(dff["saturacion"].mean())
    linea_top = dff.groupby("linea")["pasajeros"].sum().idxmax()

    return {
        "total_pax": total_pax,
        "prom_diario": prom_diario,
        "sat_prom": sat_prom,
        "linea_top": linea_top
    }

@app.post("/api/map")
def get_map_data(params: FilterParams):
    dff = filter_data(params)
    if dff.empty:
        return []

    flujo_est = dff.groupby(["estacion", "linea", "latitud", "longitud"]).agg(
        pasajeros=("pasajeros", "sum"),
        saturacion=("saturacion", "mean")
    ).reset_index()

    return flujo_est.to_dict(orient="records")

@app.post("/api/temporal")
def get_temporal_data(params: FilterParams):
    dff = filter_data(params)
    if dff.empty:
        return {"hourly": [], "daily": [], "dow": []}

    # Hourly profile
    hourly_pivot = dff.groupby(["hora", "linea"])["pasajeros"].mean().unstack("linea", fill_value=0).reset_index()
    hourly_res = hourly_pivot.to_dict(orient="records")

    # Daily evolution
    evol_df = dff.groupby("fecha")["pasajeros"].sum().reset_index()
    evol_df = evol_df.sort_values("fecha")
    evol_df["rolling7"] = evol_df["pasajeros"].rolling(7, min_periods=1).mean()
    evol_df["fecha_str"] = evol_df["fecha"].dt.strftime("%Y-%m-%d")
    daily_res = evol_df[["fecha_str", "pasajeros", "rolling7"]].rename(columns={"fecha_str": "fecha"}).to_dict(orient="records")

    # Day of week
    dias_order = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    # Group and reindex
    dow_df = dff.groupby(["dia_semana", "linea"])["pasajeros"].mean().unstack("linea", fill_value=0)
    # Ensure dias_order are present
    existing_days = [d for d in dias_order if d in dow_df.index]
    dow_df = dow_df.reindex(existing_days).reset_index()
    dow_res = dow_df.to_dict(orient="records")

    return {
        "hourly": hourly_res,
        "daily": daily_res,
        "dow": dow_res
    }

@app.post("/api/heatmap")
def get_heatmap(params: FilterParams, linea: Optional[str] = None):
    dff = filter_data(params)
    if linea and linea != "Todas":
        dff = dff[dff["linea"] == linea]

    if dff.empty:
        return {"x": [], "y": [], "z": []}

    dias_ord = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    pivot = dff.groupby(["dia_semana", "hora"])["pasajeros"].mean().reset_index()
    pivot_table = pivot.pivot(index="dia_semana", columns="hora", values="pasajeros").reindex(dias_ord)

    x = [f"{h:02d}:00" for h in pivot_table.columns]
    y = list(pivot_table.index)
    # Recharts o Plotly esperan datos de cierta forma. Devolvemos la matriz Z para react-plotly.js
    z = pivot_table.values.tolist()
    # Replace nan with 0 or None
    z_clean = [[v if not np.isnan(v) else 0 for v in row] for row in z]

    # Insight
    insight = None
    if not pivot_table.empty:
        arr = np.array(z_clean)
        max_idx = np.unravel_index(np.argmax(arr), arr.shape)
        dia_pico = y[max_idx[0]]
        hora_pico = pivot_table.columns[max_idx[1]]
        valor_pico = float(arr[max_idx[0], max_idx[1]])
        insight = {
            "dia": dia_pico,
            "hora": int(hora_pico),
            "valor": valor_pico
        }

    return {"x": x, "y": y, "z": z_clean, "insight": insight}

@app.post("/api/ranking")
def get_ranking(params: FilterParams):
    dff = filter_data(params)
    if dff.empty:
        return {"top": [], "bottom": []}

    ranking = dff.groupby(["estacion", "linea"]).agg(
        total=("pasajeros", "sum"),
        saturacion=("saturacion", "mean")
    ).reset_index().sort_values("total", ascending=False)

    top = ranking.head(10).to_dict(orient="records")
    bottom = ranking.tail(10).iloc[::-1].to_dict(orient="records")
    max_val = float(ranking["total"].max()) if not ranking.empty else 0

    return {"top": top, "bottom": bottom, "max_total": max_val}

class PredictParams(BaseModel):
    filters: FilterParams
    linea: str
    dias_pred: int

@app.post("/api/predict")
def get_prediction(params: PredictParams):
    dff = filter_data(params.filters)
    df_pred_base = dff[dff["linea"] == params.linea].groupby("fecha")["pasajeros"].sum().reset_index()
    df_pred_base.columns = ["ds", "y"]
    df_pred_base = df_pred_base.sort_values("ds")

    if len(df_pred_base) < 10:
        return {"error": "No hay suficientes datos para predecir."}

    try:
        from prophet import Prophet
        model = Prophet(
            seasonality_mode="multiplicative",
            weekly_seasonality=True,
            daily_seasonality=False,
            yearly_seasonality=False,
            changepoint_prior_scale=0.1,
        )
        model.fit(df_pred_base)
        future = model.make_future_dataframe(periods=params.dias_pred)
        forecast = model.predict(future)

        future_only = forecast[forecast["ds"] > df_pred_base["ds"].max()]

        history = df_pred_base.rename(columns={"ds": "fecha", "y": "pasajeros"}).copy()
        history["fecha"] = history["fecha"].dt.strftime("%Y-%m-%d")

        prediction = future_only[["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()
        prediction["ds"] = prediction["ds"].dt.strftime("%Y-%m-%d")

        return {
            "history": history.to_dict(orient="records"),
            "prediction": prediction.rename(columns={"ds": "fecha"}).to_dict(orient="records"),
            "kpi": {
                "total": float(future_only["yhat"].sum()),
                "promedio": float(future_only["yhat"].mean()),
                "pico": float(future_only["yhat"].max())
            },
            "method": "prophet"
        }

    except ImportError:
        from sklearn.linear_model import LinearRegression

        df_pred_base["t"] = np.arange(len(df_pred_base))
        X = df_pred_base[["t"]]
        y = df_pred_base["y"]
        reg = LinearRegression().fit(X, y)

        fut_t = np.arange(len(df_pred_base), len(df_pred_base) + params.dias_pred)
        fut_dates = [df_pred_base["ds"].max() + timedelta(days=i+1) for i in range(params.dias_pred)]
        fut_y = reg.predict(fut_t.reshape(-1,1))

        history = df_pred_base.rename(columns={"ds": "fecha", "y": "pasajeros"}).copy()
        history["fecha"] = history["fecha"].dt.strftime("%Y-%m-%d")

        prediction = []
        for i in range(len(fut_dates)):
            prediction.append({
                "fecha": fut_dates[i].strftime("%Y-%m-%d"),
                "yhat": float(fut_y[i])
            })

        return {
            "history": history.to_dict(orient="records"),
            "prediction": prediction,
            "kpi": {
                "total": float(sum(fut_y)),
                "promedio": float(np.mean(fut_y)),
                "pico": float(np.max(fut_y))
            },
            "method": "linear"
        }
