# Teleférico La Paz Cloud Analytics

Proyecto del Grupo 19 para la materia Computación en la Nube (UMSA, 2026).

## Descripción

Plataforma web de análisis de datos del Mi Teleférico de La Paz con:
- Backend API en FastAPI
- Frontend en React + Vite
- Dataset simulado realista para análisis y predicción

El sistema muestra:
- Mapa interactivo con estaciones y líneas del teleférico
- Análisis temporal por hora y por día de la semana
- Heatmap de demanda hora/día
- Predicción de demanda futura con Prophet o regresión lineal
- Ranking de estaciones más y menos concurridas

## Estructura del proyecto

- `api.py` — backend API (FastAPI)
- `frontend/` — dashboard web (React + Vite)
- `data_generator.py` — generador de datos sintéticos para el teleférico
- `data/teleferico_lapaz.csv` — dataset generado
- `requirements.txt` — dependencias Python
- `.gitignore` — exclusiones de repositorio

## Cómo ejecutar localmente

1. Crear un entorno virtual (recomendado):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Instalar dependencias:

```powershell
pip install -r requirements.txt
```

3. Generar el dataset si aún no existe:

```powershell
python data_generator.py
```

4. Levantar backend (FastAPI):

```powershell
uvicorn api:app --reload --host 0.0.0.0 --port 8001
```

5. Levantar frontend (React):

```powershell
cd frontend
npm install
npm run dev
```

6. Abrir el enlace local que muestra Vite (normalmente `http://localhost:5173`).

## Notas importantes

- El proyecto utiliza datos simulados con patrones horarios y de demanda que reflejan el uso del teleférico.
- La API carga datos generados desde `data_generator.py` y sirve métricas al frontend.
- Para la entrega final se puede integrar Supabase como fuente de datos en la nube y para almacenamiento/consulta.

## Ideas de mejora para el despliegue en la nube

- Subir el proyecto a GitHub y desplegar frontend/backend en servicios cloud.
- Guardar los datos generados en Supabase y leerlos desde `api.py`.
- Usar `.env` con `SUPABASE_URL` y `SUPABASE_ANON_KEY` para cargar datos desde la nube.
- Añadir autenticación básica y panel de administración si el tiempo lo permite.

## Dependencias

- pandas
- numpy
- plotly
- folium
- prophet
- scikit-learn
- fastapi
- uvicorn

## Contacto

Grupo 19 · Computación en la Nube · UMSA · 2026
