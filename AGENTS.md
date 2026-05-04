# AGENTS
# A
## Estructura del repo (entrypoints reales)
- El entrypoint del backend es `api.py` (objeto FastAPI: `app`).
- El entrypoint del frontend es `frontend/src/main.jsx` (Vite + React).
- El cliente API del frontend usa `/api` relativo en `frontend/src/api.js`; las peticiones dependen del proxy de Vite, no de una URL fija del backend.

## Comandos que sí coinciden con la configuración actual
- Backend para desarrollo local con frontend: `uvicorn api:app --reload --host 0.0.0.0 --port 8000`.
- Frontend dev: `cd frontend && npm install && npm run dev`.
- Checks de frontend (únicos scripts JS definidos): `cd frontend && npm run lint` y `npm run build`.

## Desajuste crítico a evitar
- `README.md` y algunos docs todavía mencionan el puerto `8001`, pero `frontend/vite.config.js` hace proxy de `/api` a `http://localhost:8000`; si el backend corre en `8001`, fallan las llamadas del frontend salvo que actualices el proxy.

## Comportamiento de la fuente de datos (backend)
- `api.py` carga primero desde Supabase solo cuando existen `SUPABASE_URL` y `SUPABASE_ANON_KEY`; si no, usa `data/teleferico_lapaz.csv`.
- Si falta el CSV, el backend lo genera automáticamente al iniciar con `data_generator.generar_dataset("2022-01-01", "2024-12-31")`.
- Los datos quedan en caché en memoria (`_global_df`), así que cambiar CSV/env en caliente requiere reiniciar el backend.

## Detalle clave del nombre de tabla en Supabase
- La tabla por defecto en backend es `SUPABASE_TABLE=teleferico` (`api.py`).
- La tabla por defecto del script de subida es `SUPABASE_TABLE=teleferico_lapaz` (`upload_to_supabase.py`).
- Define `SUPABASE_TABLE` explícitamente en `.env` para que subida y API apunten a la misma tabla.

## Límites de alcance
- Las dependencias de Python se gestionan desde `requirements.txt` en la raíz.
- Las dependencias/scripts de Node viven solo en `frontend/package.json` (no hay workspace ni tooling npm en la raíz).
