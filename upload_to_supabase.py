"""
upload_to_supabase.py
Sube el dataset calibrado del teleférico a Supabase via REST API.
Grupo 19 · Computación en la Nube · UMSA · 2026

Dataset: datos reales INE (2019-2024) + desagregación horaria simulada
Registros esperados: ~1,736,064
"""

import os, sys, json, requests, time
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
TABLE        = os.getenv("SUPABASE_TABLE", "teleferico_lapaz")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ ERROR: Faltan credenciales en .env")
    print("   Verifica que existan SUPABASE_URL y SUPABASE_ANON_KEY")
    sys.exit(1)

HEADERS = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
    "Prefer":        "return=minimal",
}
REST = f"{SUPABASE_URL.rstrip('/')}/rest/v1/{TABLE}"

# ─── Verificar conexión ───────────────────────────────────────────────────────
print(f"🔌 Conectando a Supabase — tabla: {TABLE}")
r = requests.get(REST + "?select=id&limit=1", headers=HEADERS)
if r.status_code not in (200, 206):
    print(f"❌ Error de conexión: {r.status_code} — {r.text}")
    sys.exit(1)
print("✅ Conexión OK\n")

# ─── Cargar o generar CSV ─────────────────────────────────────────────────────
CSV_RUTA = os.path.join(os.path.dirname(__file__), "data", "teleferico_lapaz.csv")

if not os.path.exists(CSV_RUTA):
    print("⚠️  CSV no encontrado. Generando datos calibrados (puede tardar ~2 min)...")
    from data_generator import generar_dataset, guardar_datos
    df = generar_dataset(fecha_inicio_str="2019-01-01", fecha_fin_str="2024-12-31")
    guardar_datos(df, CSV_RUTA)
else:
    print(f"📂 Cargando CSV: {CSV_RUTA}")
    df = pd.read_csv(CSV_RUTA)

print(f"📊 Dataset cargado: {len(df):,} registros\n")

# ─── Verificar registros existentes ──────────────────────────────────────────
r_count = requests.get(
    REST + "?select=id",
    headers={**HEADERS, "Prefer": "count=exact", "Range": "0-0"}
)
content_range = r_count.headers.get("Content-Range", "0/0")
total_existente = int(content_range.split("/")[-1]) if "/" in content_range else 0

if total_existente > 0:
    print(f"⚠️  Ya hay {total_existente:,} registros en la tabla.")
    resp = input("   ¿Borrar y resubir todo? (s/n): ").strip().lower()
    if resp == "s":
        print("   🗑️  Limpiando tabla...")
        # Supabase requiere un filtro para DELETE; usamos fecha >= fecha_minima
        r_del = requests.delete(REST + "?hora=gte.0", headers=HEADERS)
        if r_del.status_code in (200, 204):
            print("   ✅ Tabla limpiada\n")
        else:
            print(f"   ❌ Error al limpiar: {r_del.status_code} — {r_del.text}")
            sys.exit(1)
    else:
        print("   ℹ️  Subida cancelada.")
        sys.exit(0)

# ─── Preparar DataFrame ───────────────────────────────────────────────────────
df_up = df.copy()
df_up["fecha"] = pd.to_datetime(df_up["fecha"]).dt.strftime("%Y-%m-%d")

# Eliminar columnas que no existen en Supabase (si vienen del CSV viejo)
columnas_supabase = [
    "fecha", "hora", "dia_semana", "linea", "color_linea",
    "estacion", "latitud", "longitud", "pasajeros", "saturacion",
    "calibrado", "factor_escala"
]
# Solo incluir columnas que existen en el DataFrame
cols_presentes = [c for c in columnas_supabase if c in df_up.columns]
df_up = df_up[cols_presentes]

# Convertir tipos problemáticos
if "calibrado" in df_up.columns:
    df_up["calibrado"] = df_up["calibrado"].astype(bool)
if "factor_escala" in df_up.columns:
    df_up["factor_escala"] = df_up["factor_escala"].round(4)

# Eliminar columna id si existe
if "id" in df_up.columns:
    df_up = df_up.drop(columns=["id"])

print(f"📋 Columnas a subir: {list(df_up.columns)}\n")

# ─── Subir en lotes ───────────────────────────────────────────────────────────
# Con 1.7M registros usamos lotes más grandes y mostramos ETA
BATCH   = 1000   # Supabase acepta hasta ~2000 por lote
total   = len(df_up)
subidos = 0
errores = 0
reintentos_totales = 0
t_inicio = time.time()

print(f"🚀 Subiendo {total:,} registros en lotes de {BATCH}...")
print(f"   Estimado: ~{total // BATCH // 3} minutos con buena conexión.\n")

for i in range(0, total, BATCH):
    lote = df_up.iloc[i:i + BATCH].to_dict(orient="records")

    # Reintento automático hasta 3 veces
    exito = False
    for intento in range(3):
        r_ins = requests.post(REST, headers=HEADERS, data=json.dumps(lote, default=str))
        if r_ins.status_code in (200, 201, 204):
            subidos += len(lote)
            exito = True
            break
        else:
            reintentos_totales += 1
            time.sleep(1 + intento)  # backoff

    if not exito:
        errores += len(lote)
        print(f"\n   ⚠️  Error lote {i // BATCH + 1}: {r_ins.status_code} — {r_ins.text[:120]}")

    # Barra de progreso con ETA
    pct      = subidos / total * 100
    elapsed  = time.time() - t_inicio
    eta_seg  = (elapsed / max(subidos, 1)) * (total - subidos)
    eta_min  = eta_seg / 60
    barra    = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
    print(f"   [{barra}] {pct:5.1f}%  {subidos:,}/{total:,}  ETA: {eta_min:.1f} min", end="\r")

# ─── Resultado ────────────────────────────────────────────────────────────────
elapsed_total = (time.time() - t_inicio) / 60
print(f"\n\n{'='*60}")
print(f"✅ Subidos:    {subidos:,}")
print(f"❌ Errores:    {errores:,}")
print(f"🔄 Reintentos: {reintentos_totales}")
print(f"⏱️  Tiempo:     {elapsed_total:.1f} minutos")

# Verificación final en Supabase
r_f = requests.get(
    REST + "?select=id",
    headers={**HEADERS, "Prefer": "count=exact", "Range": "0-0"}
)
cf = r_f.headers.get("Content-Range", "0/0")
total_final = int(cf.split("/")[-1]) if "/" in cf else "?"
print(f"📦 Registros en Supabase: {total_final:,}")

# Muestra de datos
r_s = requests.get(
    REST + "?select=fecha,linea,estacion,pasajeros,factor_escala&limit=5&order=fecha.asc",
    headers=HEADERS
)
if r_s.status_code == 200:
    print("\n   Muestra (primeros registros):")
    for row in r_s.json():
        fe = row.get("factor_escala", "N/A")
        print(f"     {row['fecha']}  {row['linea']:10} · {row['estacion']:25} · {row['pasajeros']:4} pax  · escala={fe}")

print(f"\n🎉 ¡Listo! Ahora corre: streamlit run app.py")