# Teleférico La Paz Cloud Analytics

Proyecto del Grupo 19 para la materia Computación en la Nube (UMSA, 2026).

Plataforma web de análisis, monitoreo y predicción de demanda del Mi Teleférico de La Paz, Bolivia.

---

## Descripción

Sistema completo de análisis de datos del transporte por teleférico de La Paz que incluye:

- **Dashboard interactivo** con métricas en tiempo real
- **Mapa de estaciones** con líneas y marcadores geográficos
- **Análisis temporal** de demanda por hora y día de semana
- **Heatmap de demanda** para identificar picos de saturación
- **Ranking de estaciones** más y menos concurridas
- **Predicción de demanda** futura con Prophet o regresión lineal
- **Simulador de tickets** para registrar pasajeros en tiempo real
- **Integración con Supabase** como base de datos en la nube

---

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                    NAVEGADOR WEB                         │
│              http://localhost:5173                       │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP
┌──────────────────────▼──────────────────────────────────┐
│                  FRONTEND                                │
│            React + Vite + Plotly + Leaflet               │
│                                                          │
│  ┌──────────┬──────────┬──────────┬──────────┐          │
│  │   Mapa   │ Temporal │ Heatmap  │ Ranking  │          │
│  └──────────┴──────────┴──────────┴──────────┘          │
│  ┌──────────┬──────────┐                                │
│  │ Predicción│ Tickets │                                │
│  └──────────┴──────────┘                                │
└──────────────────────┬──────────────────────────────────┘
                       │ /api/*
┌──────────────────────▼──────────────────────────────────┐
│                  BACKEND                                 │
│            FastAPI + Python + Pandas                     │
│                                                          │
│  ┌────────────────────┬────────────────────┐            │
│  │   Data Service     │    ML Service      │            │
│  │  (caché en mem.)   │ (Prophet/Sklearn)  │            │
│  └────────┬───────────┴────────┬───────────┘            │
└───────────┼────────────────────┼────────────────────────┘
            │                    │
┌───────────▼──────┐  ┌─────────▼────────────────┐
│   CSV Local      │  │   Supabase (PostgreSQL)  │
│ teleferico_lapaz │  │   REST API + Dashboard   │
└──────────────────┘  └──────────────────────────┘
```

---

## Estructura del Proyecto

```
teleferico-lapaz-cloud/
│
├── app/                          # Backend Python
│   ├── api/
│   │   └── endpoints.py          # Endpoints REST de la API
│   ├── core/
│   │   └── config.py             # Variables de entorno (Supabase)
│   ├── schemas/
│   │   └── teleferico.py         # Modelos Pydantic (FilterParams, PredictParams)
│   ├── services/
│   │   ├── data_service.py       # Carga, filtrado y registro de datos
│   │   └── ml_service.py         # Predicción con Prophet / Regresión Lineal
│   └── main.py                   # Configuración FastAPI + CORS
│
├── frontend/                     # Frontend React
│   └── src/
│       ├── components/
│       │   ├── MapView.jsx       # Mapa interactivo con Leaflet
│       │   ├── TemporalView.jsx  # Análisis temporal con Plotly
│       │   ├── HeatmapView.jsx   # Heatmap de demanda
│       │   ├── RankingView.jsx   # Ranking de estaciones
│       │   ├── PredictView.jsx   # Predicción de demanda
│       │   ├── TicketDashboard.jsx # Simulador de tickets
│       │   └── Sidebar.jsx       # Navegación lateral
│       ├── api.js                # Cliente API con Axios
│       ├── App.jsx               # Router principal
│       └── main.jsx              # Entry point
│
├── data/
│   └── teleferico_lapaz.csv      # Dataset generado
│
├── tests/
│   └── test_api.py               # Tests del backend
│
├── api.py                        # Entrypoint uvicorn (compatibilidad)
├── data_generator.py             # Generador de datos sintéticos
├── upload_to_supabase.py         # Script para subir CSV a Supabase
├── requirements.txt              # Dependencias Python
├── informe_proyecto.md           # Informe del proyecto con diagramas UML
└── .env                          # Variables de entorno (no subir a git)
```

---


## Tecnologías Utilizadas

### Backend
| Tecnología | Uso |
|-----------|-----|
| **Python 3.13** | Lenguaje principal del backend |
| **FastAPI** | Framework web para API REST |
| **Pandas** | Procesamiento y análisis de datos |
| **NumPy** | Operaciones numéricas |
| **Prophet** | Predicción de series temporales |
| **Scikit-learn** | Regresión lineal (respaldo) |
| **Requests** | Comunicación con Supabase REST API |
| **Uvicorn** | Servidor ASGI para FastAPI |
| **Pydantic** | Validación de datos |

### Frontend
| Tecnología | Uso |
|-----------|-----|
| **React 19** | Framework de UI |
| **Vite 8** | Build tool y servidor de desarrollo |
| **Axios** | Cliente HTTP para consumir la API |
| **React Router 7** | Navegación entre páginas |
| **React Query** | Gestión de estado y caché |
| **Plotly.js** | Gráficas interactivas |
| **Leaflet** | Mapas interactivos |
| **Lucide React** | Iconos |

### Base de Datos
| Tecnología | Uso |
|-----------|-----|
| **Supabase** | PostgreSQL en la nube |
| **CSV** | Almacenamiento local alternativo |

---

## Cómo Ejecutar

### Prerrequisitos
- Python 3.10+
- Node.js 18+
- npm

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/teleferico-lapaz-cloud.git
cd teleferico-lapaz-cloud
```

### 2. Configurar entorno virtual

```bash
python -m venv .venv
# Windows
.\.venv\Scripts\Activate.ps1
# Linux/Mac
source .venv/bin/activate
```

### 3. Instalar dependencias del backend

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crear archivo `.env` en la raíz:

```env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_ANON_KEY=tu-clave-anon
SUPABASE_TABLE=teleferico
```

> Si no configurás Supabase, el sistema usa el CSV local automáticamente.

### 5. Generar el dataset (si no existe)

```bash
python data_generator.py
```

### 6. Levantar el backend

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### 7. Levantar el frontend

```bash
cd frontend
npm install
npm run dev
```

### 8. Abrir en el navegador

```
http://localhost:5173
```

---

## Endpoints de la API

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/config` | Configuración general del sistema |
| GET | `/api/cloud-status` | Estado de la conexión con Supabase |
| POST | `/api/metrics` | Métricas agregadas (totales, promedios) |
| POST | `/api/mapa` | Datos geográficos de estaciones |
| POST | `/api/temporal` | Análisis temporal por hora y día |
| POST | `/api/heatmap` | Heatmap de demanda hora × día |
| POST | `/api/ranking` | Ranking Top 10 y Bottom 10 estaciones |
| POST | `/api/predict` | Predicción de demanda futura |
| POST | `/api/registrar-ticket` | Registrar ticket nuevo |

---

## Funcionalidades Principales

### Predicción de Demanda
- Usa **Prophet** para series temporales con estacionalidad semanal
- Si Prophet no está disponible, usa **Regresión Lineal** como respaldo
- Muestra intervalos de confianza del 95%
- Permite predecir de 7 a 60 días

### Ranking de Estaciones
- Agrupa pasajeros por estación y línea
- Muestra Top 10 más concurridas y Bottom 10 menos concurridas
- Barras de progreso con colores por línea

### Simulador de Tickets
- Registra pasajeros en tiempo real
- Guarda en CSV local y sube a Supabase automáticamente
- Actualiza métricas del dashboard con React Query
- Historial de registros de la sesión

### Heatmap de Demanda
- Matriz día de semana × hora
- Identifica automáticamente el pico de demanda
- Colores de intensidad de pasajeros

---

## Configuración de Supabase

### Subir datos existentes a Supabase

```bash
python upload_to_supabase.py
```

### Verificar datos en Supabase

```sql
SELECT *
FROM teleferico
ORDER BY fecha DESC, hora DESC
LIMIT 20;
```

### Nota importante
El nombre de la tabla debe ser consistente. Verificar en `.env`:

```env
SUPABASE_TABLE=teleferico
```

---

## Comandos Útiles

```bash
# Backend
uvicorn api:app --reload                    # Iniciar backend en desarrollo
uvicorn api:app --host 0.0.0.0 --port 8000  # Iniciar backend en producción

# Frontend
cd frontend
npm run dev      # Servidor de desarrollo
npm run build    # Build para producción
npm run lint     # Verificar código

# Tests
pytest tests/    # Ejecutar tests del backend

# Datos
python data_generator.py        # Regenerar dataset
python upload_to_supabase.py    # Subir CSV a Supabase
```

---

## Diagramas del Proyecto

El archivo `informe_proyecto.md` contiene **37 diagramas** incluyendo:

- Arquitectura general del sistema
- Diagramas UML (casos de uso, componentes, clases, actividad, secuencia)
- Flujo de datos y procesos
- Estructura de carpetas
- Schema de base de datos
- Cronograma del proyecto

Para renderizar los diagramas, copiar el código Mermaid a [mermaid.live](https://mermaid.live).

---

## Autores

**Grupo 19** — Computación en la Nube  
Universidad Mayor de San Andrés (UMSA)  
Año 2026
