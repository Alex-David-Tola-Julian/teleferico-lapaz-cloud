import numpy as np
from datetime import timedelta
import pandas as pd
from typing import Dict, Any

# Caché en memoria para evitar reentrenar modelos cada vez que alguien hace una petición
# En un entorno productivo real, esto podría conectarse a Redis o guardar el modelo serializado (.pkl)
_model_cache: Dict[str, Any] = {}

def generar_prediccion(df_filtrado: pd.DataFrame, linea: str, dias_pred: int) -> dict:
    """
    Toma los datos filtrados, aísla la línea específica y genera predicciones
    mediante Prophet o Regresión Lineal. Utiliza caché para mejorar los tiempos de respuesta.
    """
    df_pred_base = df_filtrado[df_filtrado["linea"] == linea].groupby("fecha")["pasajeros"].sum().reset_index()
    df_pred_base.columns = ["ds", "y"]
    df_pred_base = df_pred_base.sort_values("ds")

    if len(df_pred_base) < 10:
        return {"error": "No hay suficientes datos param predecir. Se requieren al menos 10 días de historial."}

    # Intentamos primero con Prophet (mejor para series temporales con estacionalidad)
    try:
        from prophet import Prophet
        
        # Hash simple para la caché
        cache_key = f"prophet_{linea}_{len(df_pred_base)}"
        
        if cache_key in _model_cache:
            model = _model_cache[cache_key]
        else:
            model = Prophet(
                seasonality_mode="multiplicative",
                weekly_seasonality=True,
                daily_seasonality=False,
                yearly_seasonality=False,
                changepoint_prior_scale=0.1,
            )
            model.fit(df_pred_base)
            # Guardamos en caché
            _model_cache[cache_key] = model

        future = model.make_future_dataframe(periods=dias_pred)
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

    # Si Prophet falla, usamos Regresión Lineal como fallback
    except Exception as e:
        from sklearn.linear_model import LinearRegression

        # Preparar variables para ML clásico
        df_pred_base["t"] = np.arange(len(df_pred_base))
        X = df_pred_base[["t"]]
        y = df_pred_base["y"]
        
        cache_key = f"linear_{linea}_{len(df_pred_base)}"
        
        if cache_key in _model_cache:
            reg = _model_cache[cache_key]
        else:
            reg = LinearRegression().fit(X, y)
            _model_cache[cache_key] = reg

        fut_t = np.arange(len(df_pred_base), len(df_pred_base) + dias_pred)
        fut_dates = [df_pred_base["ds"].max() + timedelta(days=i+1) for i in range(dias_pred)]
        fut_y = reg.predict(fut_t.reshape(-1, 1))

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
            "method": "linear_fallback",
            "warning": str(e)
        }
