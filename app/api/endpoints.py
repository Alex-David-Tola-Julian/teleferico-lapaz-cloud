from fastapi import APIRouter
from typing import Optional
import numpy as np
from datetime import timedelta
import pandas as pd

from app.schemas.teleferico import FilterParams, PredictParams
from app.services.data_service import get_data, filter_data, get_data_source, LINEAS_OFICIALES

router = APIRouter(prefix="/api")

@router.get("/config")
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
        "dias_orden": dias_orden,
        "data_source": get_data_source(),
    }

@router.get("/cloud-status")
def get_cloud_status():
    df = get_data()
    return {
        "data_source": get_data_source(),
        "total_registros": int(len(df)),
        "ultima_fecha": df["fecha"].max().date().isoformat() if not df.empty else None,
        "total_lineas": int(df["linea"].nunique()) if "linea" in df.columns else 0,
        "total_estaciones": int(df["estacion"].nunique()) if "estacion" in df.columns else 0,
    }

@router.post("/metrics")
def get_metrics(params: FilterParams):
    dff = filter_data(params)
    if dff.empty:
        return {
            "total_pax": 0,
            "prom_diario": 0,
            "sat_prom": 0,
            "linea_top": "—",
            "registros_filtrados": 0,
            "lineas_activas": 0,
            "estaciones_activas": 0,
        }

    total_pax = int(dff["pasajeros"].sum())
    prom_diario = float(dff.groupby("fecha")["pasajeros"].sum().mean())
    sat_prom = float(dff["saturacion"].mean())
    linea_top = dff.groupby("linea")["pasajeros"].sum().idxmax()

    return {
        "total_pax": total_pax,
        "prom_diario": prom_diario,
        "sat_prom": sat_prom,
        "linea_top": linea_top,
        "registros_filtrados": int(len(dff)),
        "lineas_activas": int(dff["linea"].nunique()),
        "estaciones_activas": int(dff["estacion"].nunique()),
    }

@router.post("/map")
def get_map_data(params: FilterParams):
    dff = filter_data(params)
    if dff.empty:
        return []

    flujo_est = dff.groupby(["estacion", "linea", "latitud", "longitud"]).agg(
        pasajeros=("pasajeros", "sum"),
        saturacion=("saturacion", "mean")
    ).reset_index()

    return flujo_est.to_dict(orient="records")

@router.post("/temporal")
def get_temporal_data(params: FilterParams):
    dff = filter_data(params)
    if dff.empty:
        return {"hourly": [], "daily": [], "dow": []}

    hourly_pivot = dff.groupby(["hora", "linea"])["pasajeros"].mean().unstack("linea", fill_value=0).reset_index()
    hourly_res = hourly_pivot.to_dict(orient="records")

    evol_df = dff.groupby("fecha")["pasajeros"].sum().reset_index().sort_values("fecha")
    evol_df["rolling7"] = evol_df["pasajeros"].rolling(7, min_periods=1).mean()
    evol_df["fecha_str"] = evol_df["fecha"].dt.strftime("%Y-%m-%d")
    daily_res = evol_df[["fecha_str", "pasajeros", "rolling7"]].rename(columns={"fecha_str": "fecha"}).to_dict(orient="records")

    dias_order = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    dow_df = dff.groupby(["dia_semana", "linea"])["pasajeros"].mean().unstack("linea", fill_value=0)
    existing_days = [d for d in dias_order if d in dow_df.index]
    dow_df = dow_df.reindex(existing_days).reset_index()
    dow_res = dow_df.to_dict(orient="records")

    return {"hourly": hourly_res, "daily": daily_res, "dow": dow_res}

@router.post("/heatmap")
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
    z = pivot_table.values.tolist()
    z_clean = [[v if not np.isnan(v) else 0 for v in row] for row in z]

    insight = None
    if not pivot_table.empty:
        arr = np.array(z_clean)
        max_idx = np.unravel_index(np.argmax(arr), arr.shape)
        insight = {
            "dia": y[max_idx[0]],
            "hora": int(pivot_table.columns[max_idx[1]]),
            "valor": float(arr[max_idx[0], max_idx[1]])
        }

    return {"x": x, "y": y, "z": z_clean, "insight": insight}

@router.post("/ranking")
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

@router.post("/predict")
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

        prediction = [{"fecha": fut_dates[i].strftime("%Y-%m-%d"), "yhat": float(fut_y[i])} for i in range(len(fut_dates))]

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