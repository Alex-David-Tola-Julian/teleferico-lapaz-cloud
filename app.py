"""
app.py — Dashboard: Análisis de Datos del Mi Teleférico
Grupo 19 · Computación en la Nube · UMSA · 2026
"""

import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
import requests
from streamlit_folium import st_folium
from datetime import datetime, timedelta
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore")
load_dotenv()

# ─── Configuración de página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Mi Teleférico · Análisis Cloud",
    page_icon="🚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Estilos personalizados ───────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Barlow:wght@300;400;600;800&display=swap');

  html, body, [class*="css"] {
    font-family: 'Barlow', sans-serif;
    background-color: #0A0E1A;
    color: #E8EAF0;
  }
  .main { background-color: #0A0E1A; }

  /* Header principal */
  .hero-header {
    background: linear-gradient(135deg, #0D1B2A 0%, #1B2838 50%, #0A1628 100%);
    border: 1px solid #1E3A5F;
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
  }
  .hero-header::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(0,180,255,0.08) 0%, transparent 70%);
    border-radius: 50%;
  }
  .hero-title {
    font-family: 'Space Mono', monospace;
    font-size: 2.2rem;
    font-weight: 700;
    color: #00B4FF;
    margin: 0;
    letter-spacing: -1px;
  }
  .hero-subtitle {
    font-size: 1rem;
    color: #7A8FA6;
    margin: 0.4rem 0 0 0;
    font-weight: 300;
    letter-spacing: 0.5px;
  }
  .hero-badge {
    display: inline-block;
    background: rgba(0,180,255,0.12);
    border: 1px solid rgba(0,180,255,0.3);
    color: #00B4FF;
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    margin-top: 0.8rem;
  }

  /* Métricas */
  .metric-card {
    background: linear-gradient(145deg, #111827, #1A2332);
    border: 1px solid #1E3A5F;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    text-align: center;
    transition: border-color 0.2s;
  }
  .metric-card:hover { border-color: #00B4FF; }
  .metric-value {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: #00B4FF;
    margin: 0;
  }
  .metric-label {
    font-size: 0.8rem;
    color: #7A8FA6;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 0.3rem 0 0 0;
  }
  .metric-delta {
    font-size: 0.85rem;
    color: #2DC653;
    font-weight: 600;
    margin: 0.2rem 0 0 0;
  }

  /* Sección título */
  .section-title {
    font-family: 'Space Mono', monospace;
    font-size: 1.1rem;
    color: #00B4FF;
    border-left: 3px solid #00B4FF;
    padding-left: 0.8rem;
    margin: 1.5rem 0 1rem 0;
    letter-spacing: 0.5px;
  }

  /* Sidebar */
  [data-testid="stSidebar"] {
    background: #0D1420 !important;
    border-right: 1px solid #1E3A5F;
  }
  [data-testid="stSidebar"] .css-1d391kg { padding: 1.5rem 1rem; }

  /* Chips de línea */
  .linea-chip {
    display: inline-block;
    border-radius: 20px;
    padding: 0.2rem 0.7rem;
    font-size: 0.78rem;
    font-weight: 600;
    margin: 0.15rem;
    font-family: 'Space Mono', monospace;
  }

  /* Tabs */
  .stTabs [data-baseweb="tab"] {
    font-family: 'Space Mono', monospace;
    font-size: 0.85rem;
    color: #7A8FA6;
  }
  .stTabs [aria-selected="true"] { color: #00B4FF !important; }

  /* Plotly chart background */
  .js-plotly-plot { border-radius: 12px; }

  /* Scrollbar */
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: #0A0E1A; }
  ::-webkit-scrollbar-thumb { background: #1E3A5F; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ─── Colores de líneas ─────────────────────────────────────────────────────────
COLOR_LINEAS = {
    "Roja": "#E63946", "Amarilla": "#FFB703", "Verde": "#2DC653",
    "Azul": "#0077B6", "Naranja": "#FB8500", "Celeste": "#48CAE4",
    "Blanca": "#CED4DA", "Café": "#8B5E3C", "Plateada": "#ADB5BD",
    "Dorada": "#D4AF37", "Morada": "#7209B7",
}

# ─── Carga de datos ────────────────────────────────────────────────────────────
CSV_RUTA = os.path.join(os.path.dirname(__file__), "data", "teleferico_lapaz.csv")

def cargar_datos_supabase():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    table_name = os.getenv("SUPABASE_TABLE", "teleferico")

    if not url or not key:
        raise RuntimeError("Supabase no configurado. Revisa .env")

    rest_url = f"{url.rstrip('/')}/rest/v1/{table_name}?select=*"
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Accept": "application/json",
    }

    response = requests.get(rest_url, headers=headers)
    if response.status_code != 200:
        raise RuntimeError(f"Supabase request fallida: {response.status_code} - {response.text}")

    data = response.json()
    if not isinstance(data, list) or not data:
        raise RuntimeError("No se encontraron registros en Supabase.")

    df = pd.DataFrame(data)
    return df

@st.cache_data(ttl=300, show_spinner=False)
def cargar_datos():
    use_supabase = os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_ANON_KEY")
    if use_supabase:
        try:
            df = cargar_datos_supabase()
            st.info("🔌 Datos cargados desde Supabase.")
            if "fecha" in df.columns:
                df["fecha"] = pd.to_datetime(df["fecha"])
                df["fecha"] = df["fecha"].dt.tz_localize(None)
            return df
        except Exception as error:
            st.warning(f"⚠️ No se pudo cargar Supabase. Usando datos locales. {error}")

    if os.path.exists(CSV_RUTA):
        df = pd.read_csv(CSV_RUTA)
    else:
        from data_generator import generar_dataset
        df = generar_dataset(dias=180)
        os.makedirs(os.path.dirname(CSV_RUTA), exist_ok=True)
        df.to_csv(CSV_RUTA, index=False)

    df["fecha"] = pd.to_datetime(df["fecha"])
    return df

with st.spinner("🚡 Cargando datos del teleférico..."):
    df = cargar_datos()

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0 1.5rem 0;'>
      <span style='font-family: Space Mono, monospace; font-size: 1.5rem; color: #00B4FF;'>🚡</span>
      <p style='font-family: Space Mono, monospace; font-size: 0.9rem; color: #00B4FF; margin:0.3rem 0 0;'>Mi Teleférico</p>
      <p style='font-size: 0.72rem; color: #7A8FA6; margin:0;'>Dashboard Analytics · La Paz</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**🗓 Rango de fechas**")
    fecha_min = df["fecha"].min().date()
    fecha_max = df["fecha"].max().date()
    fechas = st.date_input(
        "Período",
        value=(fecha_max - timedelta(days=30), fecha_max),
        min_value=fecha_min, max_value=fecha_max,
        label_visibility="collapsed"
    )
    if isinstance(fechas, tuple) and len(fechas) == 2:
        fecha_inicio, fecha_fin = fechas
    else:
        fecha_inicio = fechas[0] if isinstance(fechas, tuple) else fechas
        fecha_fin = fecha_inicio

    st.markdown("**🚡 Líneas**")
    lineas_disp = sorted(df["linea"].unique())

    if st.button("Seleccionar todo"):
        for linea in lineas_disp:
            st.session_state[f"chk_{linea}"] = True
        st.experimental_rerun()

    lineas_sel = []
    st.markdown("Selecciona las líneas visibles:")
    for linea in lineas_disp:
        if f"chk_{linea}" not in st.session_state:
            st.session_state[f"chk_{linea}"] = True
        checked = st.checkbox(
            linea,
            key=f"chk_{linea}"
        )
        if checked:
            lineas_sel.append(linea)

    if not lineas_sel:
        st.warning("⚠️ No hay líneas seleccionadas. Marca al menos una línea.")

    st.markdown("**⏰ Horario**")
    hora_range = st.slider("Rango de horas", 5, 22, (5, 22))

    st.markdown("**📅 Días de la semana**")
    dias_orden = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]

    if st.button("Seleccionar todos los días"):
        for dia in dias_orden:
            st.session_state[f"chk_{dia}"] = True
        st.experimental_rerun()

    dias_sel = []
    st.markdown("Selecciona los días visibles:")
    for dia in dias_orden:
        if f"chk_{dia}" not in st.session_state:
            st.session_state[f"chk_{dia}"] = True
        checked = st.checkbox(
            dia,
            key=f"chk_{dia}"
        )
        if checked:
            dias_sel.append(dia)

    if not dias_sel:
        st.warning("⚠️ No hay días seleccionados. Marca al menos un día.")

    st.markdown("---")
    st.markdown(f"""
    """, unsafe_allow_html=True)

# ─── Filtrado ─────────────────────────────────────────────────────────────────
mask = (
    (df["fecha"].dt.date >= fecha_inicio) &
    (df["fecha"].dt.date <= fecha_fin) &
    (df["linea"].isin(lineas_sel)) &
    (df["hora"] >= hora_range[0]) &
    (df["hora"] <= hora_range[1]) &
    (df["dia_semana"].isin(dias_sel))
)
dff = df[mask].copy()

if dff.empty:
    st.warning("⚠️ No hay datos con los filtros actuales. Ajusta las líneas, días o rango de fechas.")

with st.expander("🔍 Depuración de filtros", expanded=True):
    st.write("**Filtrado activo:**")
    st.write({
        "Fecha inicio": fecha_inicio,
        "Fecha fin": fecha_fin,
        "Líneas seleccionadas": lineas_sel,
        "Días seleccionados": dias_sel,
        "Rango de horas": f"{hora_range[0]} - {hora_range[1]}",
        "Filas resultantes": len(dff),
    })
    st.write("**Primeros registros filtrados**")
    st.dataframe(dff.head(10))

# ─── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
  <p class="hero-title">🚡 Mi Teleférico · Análisis de datos</p>
  <p class="hero-subtitle">Sistema de Monitoreo y Predicción de Pasajeros — La Paz, Bolivia</p>
  <span class="hero-badge">GRUPO 19 · COMPUTACIÓN EN LA NUBE · UMSA 2026</span>
</div>
""", unsafe_allow_html=True)

# ─── MÉTRICAS RESUMEN ─────────────────────────────────────────────────────────
total_pax    = dff["pasajeros"].sum()
prom_diario  = dff.groupby("fecha")["pasajeros"].sum().mean()
sat_prom     = dff["saturacion"].mean()
linea_top    = dff.groupby("linea")["pasajeros"].sum().idxmax() if not dff.empty else "—"

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""<div class="metric-card">
      <p class="metric-value">{total_pax/1_000_000:.2f}M</p>
      <p class="metric-label">Total Pasajeros</p>
      <p class="metric-delta">↑ período seleccionado</p>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="metric-card">
      <p class="metric-value">{prom_diario/1000:.1f}K</p>
      <p class="metric-label">Promedio Diario</p>
      <p class="metric-delta">por día</p>
    </div>""", unsafe_allow_html=True)
with c3:
    color_sat = "#E63946" if sat_prom > 75 else "#FFB703" if sat_prom > 50 else "#2DC653"
    st.markdown(f"""<div class="metric-card">
      <p class="metric-value" style="color:{color_sat}">{sat_prom:.1f}%</p>
      <p class="metric-label">Saturación Promedio</p>
      <p class="metric-delta">de capacidad</p>
    </div>""", unsafe_allow_html=True)
with c4:
    color_linea = COLOR_LINEAS.get(linea_top, "#00B4FF")
    st.markdown(f"""<div class="metric-card">
      <p class="metric-value" style="color:{color_linea}; font-size:1.5rem;">{linea_top}</p>
      <p class="metric-label">Línea Más Demandada</p>
      <p class="metric-delta">mayor flujo de pasajeros</p>
    </div>""", unsafe_allow_html=True)

# ─── TABS PRINCIPALES ─────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🗺️  Mapa Interactivo",
    "📈  Análisis Temporal",
    "🌡️  Heatmap de Demanda",
    "🔮  Predicción",
    "🏆  Ranking Estaciones",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — MAPA INTERACTIVO
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<p class="section-title">Mapa de Flujo de Pasajeros — La Paz</p>', unsafe_allow_html=True)
    st.markdown('<span style="color:#7A8FA6; font-size:0.85rem;">debug: tab1 cargado</span>', unsafe_allow_html=True)

    col_mapa, col_info = st.columns([3, 1])

    with col_mapa:
        try:
            # Calcular flujo por estación
            flujo_est = dff.groupby(["estacion","linea","latitud","longitud"]).agg(
                pasajeros=("pasajeros","sum"),
                saturacion=("saturacion","mean")
            ).reset_index()

            m = folium.Map(
                location=[-16.505, -68.128],
                zoom_start=13,
                tiles="CartoDB dark_matter",
            )

            # Dibujar rutas por línea
            lineas_rutas = {
                "Roja":     [(-16.530,-68.119),(-16.520,-68.115),(-16.504,-68.113),(-16.497,-68.115)],
                "Amarilla": [(-16.508,-68.131),(-16.503,-68.138),(-16.499,-68.143),(-16.494,-68.148)],
                "Verde":    [(-16.507,-68.123),(-16.513,-68.127),(-16.520,-68.130),(-16.535,-68.125)],
                "Azul":     [(-16.490,-68.120),(-16.495,-68.118),(-16.500,-68.116),(-16.505,-68.114)],
                "Naranja":  [(-16.478,-68.154),(-16.485,-68.148),(-16.497,-68.136),(-16.530,-68.115)],
                "Celeste":  [(-16.472,-68.165),(-16.480,-68.158),(-16.493,-68.142),(-16.508,-68.110)],
                "Blanca":   [(-16.550,-68.105),(-16.542,-68.108),(-16.535,-68.112),(-16.528,-68.118)],
                "Café":     [(-16.555,-68.101),(-16.545,-68.104),(-16.510,-68.109),(-16.502,-68.107)],
                "Plateada": [(-16.490,-68.145),(-16.480,-68.150),(-16.474,-68.156),(-16.501,-68.133)],
                "Dorada":   [(-16.465,-68.170),(-16.470,-68.162),(-16.475,-68.155),(-16.483,-68.147)],
                "Morada":   [(-16.538,-68.108),(-16.525,-68.106),(-16.518,-68.110),(-16.510,-68.112)],
            }

            for linea, coords in lineas_rutas.items():
                if linea in lineas_sel:
                    color = COLOR_LINEAS.get(linea, "#FFFFFF")
                    folium.PolyLine(
                        coords, color=color, weight=4, opacity=0.85,
                        tooltip=f"Línea {linea}"
                    ).add_to(m)

            # Marcadores de estaciones
            for _, row in flujo_est.iterrows():
                color = COLOR_LINEAS.get(row["linea"], "#FFFFFF")
                sat = row["saturacion"]
                radio = 6 + int(sat / 15)
                fill_color = "#E63946" if sat > 75 else "#FFB703" if sat > 50 else "#2DC653"

                popup_html = f"""
                <div style='font-family:monospace; font-size:12px; min-width:160px;'>
                  <b style='color:{color};'>● {row['estacion']}</b><br>
                  <span>Línea <b>{row['linea']}</b></span><br>
                  <span>Pasajeros: <b>{int(row['pasajeros']):,}</b></span><br>
                  <span>Saturación: <b style='color:{fill_color};'>{sat:.1f}%</b></span>
                </div>
                """
                folium.CircleMarker(
                    location=[row["latitud"], row["longitud"]],
                    radius=radio,
                    color=color,
                    fill=True,
                    fill_color=fill_color,
                    fill_opacity=0.85,
                    popup=folium.Popup(popup_html, max_width=220),
                    tooltip=f"{row['estacion']} — {sat:.0f}% saturación",
                ).add_to(m)

            # Usar componentes HTML directamente suele ser más estable que st_folium en tabs/columnas
            import streamlit.components.v1 as components
            components.html(m._repr_html_(), height=500)
        except Exception as e:
            st.error(f"Error generando el mapa: {str(e)}")
    with col_info:
        st.markdown("**Leyenda de líneas**")
        for linea in lineas_sel:
            color = COLOR_LINEAS.get(linea, "#FFF")
            pax_linea = dff[dff["linea"]==linea]["pasajeros"].sum()
            st.markdown(f"""
            <div style='display:flex; align-items:center; gap:8px; margin:6px 0;'>
              <div style='width:14px;height:14px;border-radius:50%;background:{color};flex-shrink:0;'></div>
              <div>
                <div style='font-size:0.85rem; font-weight:600;'>{linea}</div>
                <div style='font-size:0.72rem; color:#7A8FA6;'>{pax_linea/1000:.0f}K pax</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("**Saturación**")
        st.markdown("""
        <div style='font-size:0.8rem; line-height:2;'>
          <span style='color:#2DC653;'>●</span> Verde — &lt;50%<br>
          <span style='color:#FFB703;'>●</span> Amarillo — 50-75%<br>
          <span style='color:#E63946;'>●</span> Rojo — &gt;75%
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — ANÁLISIS TEMPORAL
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<p class="section-title">Análisis Temporal de Pasajeros</p>', unsafe_allow_html=True)
    st.markdown('<span style="color:#7A8FA6; font-size:0.85rem;">debug: tab2 cargado</span>', unsafe_allow_html=True)
    col_a, col_b = st.columns(2)

    # Gráfica de pasajeros por hora (perfil diario)
    with col_a:
        st.markdown("**Perfil de demanda por hora del día**")
        hora_df = dff.groupby(["hora","linea"])["pasajeros"].mean().reset_index()
        fig_hora = px.line(
            hora_df, x="hora", y="pasajeros", color="linea",
            color_discrete_map=COLOR_LINEAS,
            labels={"hora":"Hora", "pasajeros":"Pasajeros promedio", "linea":"Línea"},
            template="plotly_dark",
        )
        fig_hora.update_layout(
            paper_bgcolor="#111827", plot_bgcolor="#111827",
            font_color="#E8EAF0", legend_title="Línea",
            margin=dict(l=10,r=10,t=10,b=10),
            xaxis=dict(tickmode="linear", dtick=1, gridcolor="#1E3A5F"),
            yaxis=dict(gridcolor="#1E3A5F"),
        )
        fig_hora.update_traces(line_width=2)
        st.plotly_chart(fig_hora, use_container_width=True)

    # Evolución diaria
    with col_b:
        st.markdown("**Evolución diaria de pasajeros**")
        evol_df = dff.groupby("fecha")["pasajeros"].sum().reset_index()
        evol_df["rolling7"] = evol_df["pasajeros"].rolling(7, min_periods=1).mean()
        fig_evol = go.Figure()
        fig_evol.add_trace(go.Scatter(
            x=evol_df["fecha"], y=evol_df["pasajeros"],
            mode="lines", name="Diario",
            line=dict(color="#1E3A5F", width=1),
            fill="tozeroy", fillcolor="rgba(0,100,180,0.1)",
        ))
        fig_evol.add_trace(go.Scatter(
            x=evol_df["fecha"], y=evol_df["rolling7"],
            mode="lines", name="Media móvil 7d",
            line=dict(color="#00B4FF", width=2.5),
        ))
        fig_evol.update_layout(
            paper_bgcolor="#111827", plot_bgcolor="#111827",
            font_color="#E8EAF0",
            margin=dict(l=10,r=10,t=10,b=10),
            xaxis=dict(gridcolor="#1E3A5F"),
            yaxis=dict(gridcolor="#1E3A5F"),
            legend=dict(x=0, y=1),
        )
        st.plotly_chart(fig_evol, use_container_width=True)

    # Pasajeros por día de la semana
    st.markdown("**Demanda promedio por día de la semana**")
    dias_order = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
    dow_df = dff.groupby(["dia_semana","linea"])["pasajeros"].mean().reset_index()
    dow_df["dia_semana"] = pd.Categorical(dow_df["dia_semana"], categories=dias_order, ordered=True)
    dow_df = dow_df.sort_values("dia_semana")
    fig_dow = px.bar(
        dow_df, x="dia_semana", y="pasajeros", color="linea",
        color_discrete_map=COLOR_LINEAS, barmode="group",
        labels={"dia_semana":"Día","pasajeros":"Pasajeros promedio","linea":"Línea"},
        template="plotly_dark",
    )
    fig_dow.update_layout(
        paper_bgcolor="#111827", plot_bgcolor="#111827",
        font_color="#E8EAF0",
        margin=dict(l=10,r=10,t=10,b=10),
        xaxis=dict(gridcolor="#1E3A5F"),
        yaxis=dict(gridcolor="#1E3A5F"),
    )
    st.plotly_chart(fig_dow, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — HEATMAP
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<p class="section-title">Mapa de Calor — Demanda por Hora y Día</p>', unsafe_allow_html=True)
    st.markdown('<span style="color:#7A8FA6; font-size:0.85rem;">debug: tab3 cargado</span>', unsafe_allow_html=True)

    linea_hm = st.selectbox("Seleccionar línea para el heatmap", options=["Todas"] + lineas_sel)

    df_hm = dff if linea_hm == "Todas" else dff[dff["linea"] == linea_hm]
    dias_ord = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]

    pivot = df_hm.groupby(["dia_semana","hora"])["pasajeros"].mean().reset_index()
    pivot_table = pivot.pivot(index="dia_semana", columns="hora", values="pasajeros").reindex(dias_ord)

    fig_hm = go.Figure(data=go.Heatmap(
        z=pivot_table.values,
        x=[f"{h:02d}:00" for h in pivot_table.columns],
        y=pivot_table.index,
        colorscale=[
            [0.0, "#0A0E1A"], [0.2, "#0D3B6B"], [0.5, "#0077B6"],
            [0.75, "#FFB703"], [1.0, "#E63946"]
        ],
        hovertemplate="<b>%{y}</b> — %{x}<br>Pasajeros: %{z:,.0f}<extra></extra>",
        colorbar=dict(
            title=dict(text="Pasajeros", font=dict(color="#E8EAF0")),
            tickfont=dict(color="#E8EAF0"),
            bgcolor="#111827",
        )
    ))
    fig_hm.update_layout(
        paper_bgcolor="#111827", plot_bgcolor="#111827",
        font_color="#E8EAF0",
        height=380,
        margin=dict(l=10,r=10,t=10,b=10),
        xaxis=dict(title="Hora del día", tickfont=dict(size=11)),
        yaxis=dict(title="", tickfont=dict(size=12)),
    )
    st.plotly_chart(fig_hm, use_container_width=True)

    # Insight automático
    if not pivot_table.empty:
        max_idx = np.unravel_index(np.nanargmax(pivot_table.values), pivot_table.values.shape)
        dia_pico = pivot_table.index[max_idx[0]]
        hora_pico = pivot_table.columns[max_idx[1]]
        valor_pico = pivot_table.values[max_idx[0], max_idx[1]]
        st.markdown(f"""
        <div style='background:rgba(0,180,255,0.08); border:1px solid rgba(0,180,255,0.25);
             border-radius:10px; padding:1rem 1.5rem; margin-top:0.5rem;'>
          <span style='color:#00B4FF; font-family:Space Mono,monospace; font-size:0.85rem;'>
            💡 INSIGHT
          </span><br>
          <span style='font-size:0.95rem;'>
            El pico máximo de demanda ocurre los <b style='color:#FFB703;'>{dia_pico}</b>
            a las <b style='color:#FFB703;'>{hora_pico:02d}:00h</b>
            con un promedio de <b style='color:#E63946;'>{valor_pico:,.0f}</b> pasajeros.
          </span>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — PREDICCIÓN
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<p class="section-title">Predicción de Demanda — Próximos 30 días</p>', unsafe_allow_html=True)
    st.markdown('<span style="color:#7A8FA6; font-size:0.85rem;">debug: tab4 cargado</span>', unsafe_allow_html=True)

    linea_pred = st.selectbox("Línea a predecir", options=lineas_sel, key="pred_linea")
    dias_pred  = st.slider("Días a predecir", 7, 60, 30)

    df_pred_base = dff[dff["linea"] == linea_pred].groupby("fecha")["pasajeros"].sum().reset_index()
    df_pred_base.columns = ["ds", "y"]
    df_pred_base = df_pred_base.sort_values("ds")

    if len(df_pred_base) < 10:
        st.warning("⚠️ No hay suficientes datos para predecir. Amplía el rango de fechas.")
    else:
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
            future = model.make_future_dataframe(periods=dias_pred)
            forecast = model.predict(future)

            fig_pred = go.Figure()
            # Histórico
            fig_pred.add_trace(go.Scatter(
                x=df_pred_base["ds"], y=df_pred_base["y"],
                mode="lines+markers", name="Histórico",
                line=dict(color="#00B4FF", width=2),
                marker=dict(size=3),
            ))
            # Predicción
            future_only = forecast[forecast["ds"] > df_pred_base["ds"].max()]
            fig_pred.add_trace(go.Scatter(
                x=future_only["ds"], y=future_only["yhat"],
                mode="lines", name="Predicción",
                line=dict(color="#FFB703", width=2.5, dash="dash"),
            ))
            # Intervalo de confianza
            fig_pred.add_trace(go.Scatter(
                x=pd.concat([future_only["ds"], future_only["ds"][::-1]]),
                y=pd.concat([future_only["yhat_upper"], future_only["yhat_lower"][::-1]]),
                fill="toself",
                fillcolor="rgba(255,183,3,0.1)",
                line=dict(color="rgba(0,0,0,0)"),
                name="Intervalo 95%",
            ))
            fig_pred.update_layout(
                paper_bgcolor="#111827", plot_bgcolor="#111827",
                font_color="#E8EAF0", height=400,
                margin=dict(l=10,r=10,t=10,b=10),
                xaxis=dict(gridcolor="#1E3A5F"),
                yaxis=dict(gridcolor="#1E3A5F", title="Pasajeros"),
                legend=dict(x=0, y=1),
            )
            st.plotly_chart(fig_pred, use_container_width=True)

            # KPIs de predicción
            pred_total = future_only["yhat"].sum()
            pred_prom  = future_only["yhat"].mean()
            pred_max   = future_only["yhat"].max()
            c1, c2, c3 = st.columns(3)
            c1.metric("Total proyectado", f"{pred_total/1000:.1f}K pax")
            c2.metric("Promedio diario", f"{pred_prom/1000:.1f}K pax")
            c3.metric("Pico proyectado", f"{pred_max/1000:.1f}K pax")

        except ImportError:
            # Fallback si Prophet no está instalado: predicción con tendencia simple
            st.info("ℹ️ Prophet no instalado. Mostrando proyección con tendencia lineal.")
            from sklearn.linear_model import LinearRegression

            df_pred_base["t"] = np.arange(len(df_pred_base))
            X = df_pred_base[["t"]]
            y = df_pred_base["y"]
            reg = LinearRegression().fit(X, y)

            fut_t = np.arange(len(df_pred_base), len(df_pred_base) + dias_pred)
            fut_dates = [df_pred_base["ds"].max() + timedelta(days=i+1) for i in range(dias_pred)]
            fut_y = reg.predict(fut_t.reshape(-1,1))

            fig_pred = go.Figure()
            fig_pred.add_trace(go.Scatter(
                x=df_pred_base["ds"], y=df_pred_base["y"],
                mode="lines", name="Histórico",
                line=dict(color="#00B4FF", width=2),
            ))
            fig_pred.add_trace(go.Scatter(
                x=fut_dates, y=fut_y,
                mode="lines", name="Proyección (tendencia lineal)",
                line=dict(color="#FFB703", width=2.5, dash="dash"),
            ))
            fig_pred.update_layout(
                paper_bgcolor="#111827", plot_bgcolor="#111827",
                font_color="#E8EAF0", height=400,
                margin=dict(l=10,r=10,t=10,b=10),
                xaxis=dict(gridcolor="#1E3A5F"),
                yaxis=dict(gridcolor="#1E3A5F"),
            )
            st.plotly_chart(fig_pred, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — RANKING ESTACIONES
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<p class="section-title">Ranking de Estaciones por Flujo de Pasajeros</p>', unsafe_allow_html=True)
    st.markdown('<span style="color:#7A8FA6; font-size:0.85rem;">debug: tab5 cargado</span>', unsafe_allow_html=True)

    col_top, col_bot = st.columns(2)

    ranking = dff.groupby(["estacion","linea"]).agg(
        total=("pasajeros","sum"),
        saturacion=("saturacion","mean"),
    ).reset_index().sort_values("total", ascending=False)

    with col_top:
        st.markdown("**🏆 Top 10 — Más concurridas**")
        top10 = ranking.head(10)
        for i, row in enumerate(top10.itertuples(), 1):
            color = COLOR_LINEAS.get(row.linea, "#00B4FF")
            pct = (row.total / ranking["total"].max()) * 100
            st.markdown(f"""
            <div style='margin:8px 0; padding:10px 14px;
                 background:linear-gradient(90deg, rgba(0,180,255,0.06) 0%, transparent 100%);
                 border-left:3px solid {color}; border-radius:4px;'>
              <div style='display:flex; justify-content:space-between; align-items:center;'>
                <div>
                  <span style='font-family:Space Mono,monospace; color:{color}; font-size:0.78rem;'>#{i:02d}</span>
                  <span style='font-size:0.92rem; font-weight:600; margin-left:8px;'>{row.estacion}</span>
                  <span style='font-size:0.75rem; color:#7A8FA6; margin-left:6px;'>· {row.linea}</span>
                </div>
                <span style='font-family:Space Mono,monospace; color:#00B4FF; font-size:0.85rem;'>{row.total/1000:.0f}K</span>
              </div>
              <div style='margin-top:5px; background:#1E3A5F; border-radius:3px; height:4px;'>
                <div style='width:{pct:.0f}%; height:4px; background:{color}; border-radius:3px;'></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    with col_bot:
        st.markdown("**📉 Bottom 10 — Menos concurridas**")
        bot10 = ranking.tail(10).iloc[::-1]
        max_val = ranking["total"].max()
        for i, row in enumerate(bot10.itertuples(), 1):
            color = COLOR_LINEAS.get(row.linea, "#7A8FA6")
            pct = (row.total / max_val) * 100
            st.markdown(f"""
            <div style='margin:8px 0; padding:10px 14px;
                 background:linear-gradient(90deg, rgba(122,143,166,0.06) 0%, transparent 100%);
                 border-left:3px solid {color}; border-radius:4px;'>
              <div style='display:flex; justify-content:space-between; align-items:center;'>
                <div>
                  <span style='font-family:Space Mono,monospace; color:{color}; font-size:0.78rem;'>#{i:02d}</span>
                  <span style='font-size:0.92rem; font-weight:600; margin-left:8px;'>{row.estacion}</span>
                  <span style='font-size:0.75rem; color:#7A8FA6; margin-left:6px;'>· {row.linea}</span>
                </div>
                <span style='font-family:Space Mono,monospace; color:#7A8FA6; font-size:0.85rem;'>{row.total/1000:.0f}K</span>
              </div>
              <div style='margin-top:5px; background:#1E3A5F; border-radius:3px; height:4px;'>
                <div style='width:{pct:.0f}%; height:4px; background:{color}; border-radius:3px;'></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    # Gráfico comparativo completo
    st.markdown('<p class="section-title">Comparativa general por línea</p>', unsafe_allow_html=True)
    linea_totales = dff.groupby("linea")["pasajeros"].sum().reset_index().sort_values("pasajeros", ascending=True)
    colors_bar = [COLOR_LINEAS.get(l,"#00B4FF") for l in linea_totales["linea"]]
    fig_bar = go.Figure(go.Bar(
        x=linea_totales["pasajeros"],
        y=linea_totales["linea"],
        orientation="h",
        marker_color=colors_bar,
        text=[f"{v/1_000_000:.2f}M" for v in linea_totales["pasajeros"]],
        textposition="outside",
        textfont=dict(color="#E8EAF0", size=11),
    ))
    fig_bar.update_layout(
        paper_bgcolor="#111827", plot_bgcolor="#111827",
        font_color="#E8EAF0", height=380,
        margin=dict(l=10,r=60,t=10,b=10),
        xaxis=dict(gridcolor="#1E3A5F", title="Total pasajeros"),
        yaxis=dict(gridcolor="#1E3A5F"),
    )
    st.plotly_chart(fig_bar, use_container_width=True)
