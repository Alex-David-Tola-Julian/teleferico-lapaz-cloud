# Guía rápida para generar `teleferico_lapaz.csv`


## 1) Preparar entorno (una sola vez)

En la raíz del proyecto:

```powershell
cd C:\Users\VILLA\teleferico-lapaz-cloud
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 2) Generar el dataset

```powershell
python data_generator.py
```

Esto crea (o reemplaza) el archivo:

- `data/teleferico_lapaz.csv`

## 3) Verificar que se generó bien

```powershell
python -c "import pandas as pd; df=pd.read_csv('data/teleferico_lapaz.csv', engine='python', on_bad_lines='skip', encoding='latin-1'); print('rows=', len(df)); print('lineas=', sorted(df['linea'].dropna().astype(str).unique().tolist()))"
```

## 4) Ejecutar backend + frontend

Backend (FastAPI):

```powershell
uvicorn api:app --reload --host 0.0.0.0 --port 8001
```

Frontend (otra terminal):

```powershell
cd frontend
npm install
npm run dev
```

## 5) Importante para GitHub

- El CSV es grande y **no se debe subir al repo**.
- Ya está ignorado en `.gitignore`:
  - `data/teleferico_lapaz.csv`
- Cada integrante debe generarlo localmente con `python data_generator.py`.

## 6) Si algo falla

- Si no reconoce paquetes, activa el entorno: `.\.venv\Scripts\Activate.ps1`
- Si el puerto 8001 está ocupado, mata el proceso o usa otro puerto en backend y en `frontend/vite.config.js`.
- Si salen gráficos vacíos, regenerar CSV y reiniciar backend/frontend.
