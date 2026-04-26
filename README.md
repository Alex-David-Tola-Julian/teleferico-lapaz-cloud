# Teleférico La Paz Cloud Analytics

Proyecto del Grupo 19 para la materia Computación en la Nube (UMSA, 2026).

## Descripción

Dashboard interactivo de análisis de datos del Mi Teleférico de La Paz.
El sistema utiliza datos simulados realistas para mostrar:
- Mapa interactivo con estaciones y líneas del teleférico
- Análisis temporal por hora y por día de la semana
- Heatmap de demanda hora/día
- Predicción de demanda futura con Prophet o regresión lineal
- Ranking de estaciones más y menos concurridas

## Estructura del proyecto

- `app.py` — aplicación Streamlit del dashboard
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

4. Ejecutar la app Streamlit:

```powershell
streamlit run app.py
```

5. Abrir el enlace local que muestra Streamlit.

## Notas importantes

- El proyecto utiliza datos simulados con patrones horarios y de demanda que reflejan el uso del teleférico.
- La app carga datos generados desde `data_generator.py` y muestra análisis sobre el rango de fechas seleccionado.
- Para la entrega final se puede integrar Supabase como fuente de datos en la nube y para almacenamiento/consulta.

## Ideas de mejora para el despliegue en la nube

- Subir el proyecto a GitHub y conectar Streamlit Cloud para publicar la app pública.
- Guardar los datos generados en Supabase y leerlos desde `app.py`.
- Añadir autenticación básica y panel de administración si el tiempo lo permite.

## Dependencias

- streamlit
- pandas
- numpy
- plotly
- folium
- streamlit-folium
- prophet
- scikit-learn

## Contacto

Grupo 19 · Computación en la Nube · UMSA · 2026
