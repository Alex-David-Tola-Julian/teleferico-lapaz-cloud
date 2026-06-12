# Informe del Proyecto — Teleférico La Paz Cloud Analytics

## I. Primera Parte

### Carátula
- Nombre del proyecto: Análisis de Datos del Mi Teleférico de La Paz
- Grupo: 19
- Materia: Computación en la Nube
- Universidad: Universidad Mayor de San Andrés (UMSA)
- Año: 2026

### Introducción
El proyecto consiste en un dashboard de análisis de datos del sistema de teleférico de La Paz. Se utiliza un dataset sintético con patrones de demanda reales para demostrar análisis de flujos de pasajeros, picos horarios, saturación y predicciones de demanda.

### Marco teórico
- Computación en la Nube: uso de servicios PaaS para despliegue y almacenamiento (frontend y backend + Supabase).
- Visualización de datos: dashboard interactivo con React, Plotly y mapas.
- Análisis de datos: procesamiento con Pandas y generación de métricas agregadas.
- Modelos de predicción: Prophet y regresión lineal para pronosticar demanda.
- Datos geoespaciales: trazado de líneas y estaciones sobre un mapa de La Paz.

### Objetivo
Construir una solución de análisis y monitoreo del Mi Teleférico de La Paz que sirva para:
- Visualizar flujos de pasajeros por línea y estación.
- Identificar picos de demanda diarios y semanales.
- Predecir el comportamiento de pasajeros en los próximos días.
- Presentar un dashboard interactivo desplegado en la nube.

### Estrategia del Proyecto
#### Modelo de Servicio
- PaaS: despliegue de frontend y backend como servicios independientes.
- DBaaS: Supabase para almacenamiento de datos y futura integración.
- Computación en la nube: uso de Python en un entorno gestionado para análisis y predicción.

#### Modelo de Implementación
- Implementación híbrida: datos generados localmente y consumidos por la app web.
- Posible despliegue en la nube usando GitHub + plataformas para React/FastAPI.

### Evaluación de la Infraestructura
#### a. Selección del proveedor
- Plataforma de frontend (React/Vite): interfaz web interactiva.
- Supabase: base de datos PostgreSQL en la nube con API REST y autenticación gratuita.

#### b. Diseño de la Arquitectura
- `data_generator.py` genera dataset sintético.
- `api.py` procesa y expone datos mediante endpoints REST.
- `frontend/` consume la API y visualiza métricas.
- `README.md` documenta el proyecto.
- `data/teleferico_lapaz.csv` almacena el dataset.

#### c. Lista de servicios y descripción
- FastAPI: backend para exponer métricas y consultas del dataset.
- React + Vite: frontend del dashboard como aplicación web.
- Supabase: almacenamiento y consulta de datos en la nube.
- GitHub: control de versiones y despliegue automático.

### Seguridad
- Uso de `.gitignore` para evitar subir entornos o datos sensibles.
- Para la versión final con Supabase: usar variables de entorno para credenciales.
- Aplicación de estándares ISO: gestión de datos, disponibilidad y confidencialidad (ISO/IEC 27001 como referencia general).

### Ventajas y Desventajas
#### Ventajas
- Contexto local boliviano y relevante.
- Dashboard visual e interactivo.
- Uso de datos simulados realistas, válido para demo.
- Escalable hacia una solución real con Supabase.

#### Desventajas
- Datos no 100% reales, aunque son consistentes con patrones de demanda.
- El proyecto depende de un dataset generado y no de una API real.
- Reto de integrar datos geoespaciales precisos de estaciones reales.

### Conclusiones
El proyecto demuestra un caso práctico de análisis de datos en la nube mediante visualizaciones, métricas y pronósticos. Es adecuado para la entrega académica y puede escalarse a un sistema real con datos oficiales y almacenamiento en Supabase.

### Referencias Bibliográficas
- Supabase: https://supabase.com
- Prophet: https://facebook.github.io/prophet/
- Folium: https://python-visualization.github.io/folium/
- FastAPI: https://fastapi.tiangolo.com
- React: https://react.dev
- Datos del teleférico de La Paz (fuentes oficiales y reportes históricos, cuando estén disponibles)

## II. Desarrollo Práctico

### Avance preliminar
- a. Consultas: revisadas y seleccionadas las métricas principales del dataset.
- b. Avance al 75%: dashboard con mapa, análisis temporal, heatmap, ranking y predicción.
- c. Documentado en digital: informe y README preparados.
- d. Fecha: 30 de abril de 2026.

### Entrega final
- a. Al 100%: dashboard completo y documentación final.
- b. Documento digital con todos los detalles técnicos.
- c. Fecha: 15 de mayo de 2026.

### Defensa del proyecto
- Presentar la arquitectura en la nube.
- Mostrar la app en vivo con mapa, gráficos y predicción.
- Explicar cómo los datos se generaron y cómo se podría mover a Supabase.
- Resaltar el valor local del proyecto y su relevancia para La Paz.

## III. Arquitectura del Proyecto

### Tipo de arquitectura
- Arquitectura en capas (frontend, backend, base de datos).
- Estilo cliente-servidor con API REST.

### Diagrama de Arquitectura

```mermaid
graph TB
    subgraph USUARIO
        U[Navegador Web]
    end

    subgraph FRONTEND["Frontend — React + Vite"]
        UI[Dashboard Interactivo]
        MAP[Mapa de Estaciones]
        GRAF[Gráficas Plotly]
        TICK[Simulador de Tickets]
        PRED[Predicción de Demanda]
        RANK[Ranking de Estaciones]
    end

    subgraph BACKEND["Backend — FastAPI + Python"]
        API[API REST /api/*]
        DS[Data Service — Pandas]
        ML[ML Service — Prophet / Scikit-learn]
        DG[Data Generator]
    end

    subgraph DATOS["Almacenamiento de Datos"]
        CSV[(CSV Local)]
        SUP[(Supabase — PostgreSQL)]
    end

    U --> UI
    UI --> MAP
    UI --> GRAF
    UI --> TICK
    UI --> PRED
    UI --> RANK

    MAP --> API
    GRAF --> API
    TICK --> API
    PRED --> API
    RANK --> API

    API --> DS
    API --> ML
    DS --> CSV
    DS --> SUP
    DG --> CSV

    ML --> DS

    style USUARIO fill:#1a1a2e,stroke:#00B4FF,color:#E8EAF0
    style FRONTEND fill:#0d2137,stroke:#3B82F6,color:#E8EAF0
    style BACKEND fill:#1a2a1a,stroke:#2DC653,color:#E8EAF0
    style DATOS fill:#2a1a1a,stroke:#E63946,color:#E8EAF0
```

### Flujo de Registro de Tickets

```mermaid
sequenceDiagram
    actor U as Usuario
    participant F as Frontend
    participant A as API FastAPI
    participant D as Data Service
    participant C as CSV Local
    participant S as Supabase

    U->>F: Selecciona línea e ingresa pasajeros
    F->>A: POST /api/registrar-ticket
    A->>D: registrar_ticket(linea, pasajeros)
    D->>D: Generar registro con fecha, hora, estación, saturación
    D->>C: Guardar nueva fila en CSV
    D->>D: Actualizar DataFrame en memoria
    D->>S: POST a Supabase (solo el registro nuevo)
    D-->>A: Retorna registro
    A-->>F: Respuesta JSON con el registro
    F-->>U: Muestra confirmación verde
```

### Flujo de Predicción

```mermaid
sequenceDiagram
    actor U as Usuario
    participant F as Frontend
    participant A as API FastAPI
    participant ML as ML Service
    participant P as Prophet / Scikit-learn

    U->>F: Selecciona línea y días a predecir
    F->>A: POST /api/predict
    A->>A: Filtrar datos por línea y fecha
    A->>ML: generar_prediccion(df, linea, dias)
    ML->>P: Entrenar modelo y predecir
    P-->>ML: Predicciones + intervalos
    ML-->>A: history + prediction + kpi
    A-->>F: Respuesta JSON
    F-->>U: Gráfica con histórico y proyección
```

### Capas del sistema
#### Frontend (React + Vite)
- Interfaz gráfica del dashboard.
- Consume la API con Axios.
- Visualiza mapas, gráficos, ranking, tickets y predicciones.

#### Backend (FastAPI + Python)
- Expone los endpoints REST.
- Procesa datos con Pandas.
- Genera predicciones con Prophet y regresión lineal.
- Registra tickets nuevos en CSV y en Supabase.

#### Base de datos (Supabase)
- Almacena registros de pasajeros en PostgreSQL.
- Permite consultas SQL y acceso REST.

### Diagrama de Estructura de Carpetas

```mermaid
graph TB
    ROOT[teleferico-lapaz-cloud]

    ROOT --> APP[app/]
    ROOT --> FE[frontend/]
    ROOT --> DATA[data/]
    ROOT --> TESTS[tests/]
    ROOT --> FILES[archivos raíz]

    APP --> API[api/endpoints.py]
    APP --> MAIN[main.py]
    APP --> CORE[core/config.py]
    APP --> SERVICES[services/]
    APP --> SCHEMAS[schemas/teleferico.py]

    SERVICES --> DS[data_service.py]
    SERVICES --> ML[ml_service.py]

    FE --> SRC[src/]
    SRC --> COMP[components/]
    SRC --> APIJS[api.js]
    SRC --> APPJSX[App.jsx]
    SRC --> MAINJSX[main.jsx]

    COMP --> MAPVIEW[MapView.jsx]
    COMP --> TEMPVIEW[TemporalView.jsx]
    COMP --> HEATVIEW[HeatmapView.jsx]
    COMP --> RANKVIEW[RankingView.jsx]
    COMP --> PREDVIEW[PredictView.jsx]
    COMP --> TICKVIEW[TicketDashboard.jsx]
    COMP --> SIDEBAR[Sidebar.jsx]

    FILES --> APIPY[api.py]
    FILES --> GEN[data_generator.py]
    FILES --> REQ[requirements.txt]
    FILES --> ENV[.env]
    FILES --> CSV[teleferico_lapaz.csv]

    style ROOT fill:#1a1a2e,stroke:#00B4FF,color:#E8EAF0
    style APP fill:#1a2a1a,stroke:#2DC653,color:#E8EAF0
    style FE fill:#0d2137,stroke:#3B82F6,color:#E8EAF0
    style DATA fill:#2a1a1a,stroke:#E63946,color:#E8EAF0
    style TESTS fill:#2a2a1a,stroke:#FFB703,color:#E8EAF0
    style FILES fill:#1a1a2e,stroke:#7209B7,color:#E8EAF0
```

### Diagrama de Base de Datos (Schema)

```mermaid
erDiagram
    TELEFERICO {
        varchar fecha PK
        int hora
        varchar dia_semana
        varchar linea
        varchar color_linea
        varchar estacion
        float latitud
        float longitud
        int pasajeros
        float saturacion
        boolean calibrado
        float factor_escala
    }

    LINEAS {
        varchar nombre PK
        varchar color
        varchar estaciones[]
    }

    ESTACIONES {
        varchar nombre PK
        varchar linea FK
        float latitud
        float longitud
    }

    LINEAS ||--o{ ESTACIONES : "tiene"
    ESTACIONES ||--o{ TELEFERICO : "registra"
```

### Diagrama de Componentes del Frontend

```mermaid
graph TB
    subgraph APP["App.jsx — Router Principal"]
        NAV[Navbar]
        HERO[Hero Section]
        TICKET[TicketDashboard]
    end

    subgraph ROUTES["Rutas"]
        HOME["Home — Inicio"]
        MAP["Mapa"]
        TEMP["Temporal"]
        HEAT["Heatmap"]
        RANK["Ranking"]
        PRED["Predicciones"]
    end

    subgraph COMPONENTS["Componentes"]
        MAPC[MapView]
        TEMPC[TemporalView]
        HEATC[HeatmapView]
        RANKC[RankingView]
        PREDC[PredictView]
        SIDEBAR[Sidebar]
    end

    subgraph SHARED["Servicios Compartidos"]
        API[api.js — Axios]
        RQ[React Query]
    end

    NAV --> HOME
    NAV --> MAP
    NAV --> TEMP
    NAV --> HEAT
    NAV --> RANK
    NAV --> PRED

    HOME --> HERO
    HOME --> TICKET
    MAP --> MAPC
    TEMP --> TEMPC
    HEAT --> HEATC
    RANK --> RANKC
    PRED --> PREDC

    MAPC --> API
    TEMPC --> API
    HEATC --> API
    RANKC --> API
    PREDC --> API
    TICKET --> API

    API --> RQ

    style APP fill:#0d2137,stroke:#3B82F6,color:#E8EAF0
    style ROUTES fill:#1a2a1a,stroke:#2DC653,color:#E8EAF0
    style COMPONENTS fill:#2a1a1a,stroke:#E63946,color:#E8EAF0
    style SHARED fill:#2a2a1a,stroke:#FFB703,color:#E8EAF0
```

### Diagrama de Endpoints de la API

```mermaid
graph LR
    subgraph GET["Método GET"]
        CONFIG["GET api/config"]
        CLOUD["GET api/cloud-status"]
    end

    subgraph POST["Método POST"]
        METRICS["POST api/metrics"]
        MAPAPI["POST api/map"]
        TEMPAPI["POST api/temporal"]
        HEATAPI["POST api/heatmap"]
        RANKAPI["POST api/ranking"]
        PREDAPI["POST api/predict"]
        TICKAPI["POST api/registrar-ticket"]
    end

    CONFIG --> |"Configuración general"| FE[Frontend]
    CLOUD --> |"Estado del sistema"| FE
    METRICS --> |"Métricas agregadas"| FE
    MAPAPI --> |"Datos geográficos"| FE
    TEMPAPI --> |"Análisis temporal"| FE
    HEATAPI --> |"Heatmap demanda"| FE
    RANKAPI --> |"Ranking estaciones"| FE
    PREDAPI --> |"Predicción demanda"| FE
    TICKAPI --> |"Registrar ticket"| FE

    style GET fill:#1a2a1a,stroke:#2DC653,color:#E8EAF0
    style POST fill:#0d2137,stroke:#3B82F6,color:#E8EAF0
```

### Diagrama de Flujo de Datos del Heatmap

```mermaid
graph TB
    CSV[(CSV / Supabase)] --> FILTER[Filtrar por fecha, línea, hora]
    FILTER --> GROUP[GroupBy día_semana + hora]
    GROUP --> PIVOT[Pivot Table: días × horas]
    PIVOT --> Z[Matriz Z de pasajeros promedio]
    Z --> HEATMAP[Heatmap Plotly]
    Z --> INSIGHT[Insight: día y hora pico]

    style CSV fill:#2a1a1a,stroke:#E63946,color:#E8EAF0
    style HEATMAP fill:#0d2137,stroke:#3B82F6,color:#E8EAF0
    style INSIGHT fill:#1a2a1a,stroke:#2DC653,color:#E8EAF0
```

### Diagrama de Flujo del Ranking

```mermaid
graph TB
    CSV[(CSV / Supabase)] --> FILTER[Filtrar datos]
    FILTER --> GROUP[GroupBy estación + línea]
    GROUP --> SUM[Sumar pasajeros totales]
    SUM --> SORT[Ordenar de mayor a menor]
    SORT --> TOP[Top 10 más concurridas]
    SORT --> BOTTOM[Bottom 10 menos concurridas]
    TOP --> UI[Mostrar en frontend]
    BOTTOM --> UI

    style CSV fill:#2a1a1a,stroke:#E63946,color:#E8EAF0
    style TOP fill:#1a2a1a,stroke:#2DC653,color:#E8EAF0
    style BOTTOM fill:#2a2a1a,stroke:#FFB703,color:#E8EAF0
```

### Diagrama de Predicción con Prophet

```mermaid
graph TB
    DATA[Datos históricos] --> TRAIN[Entrenar Prophet]
    TRAIN --> MODEL[Modelo con estacionalidad semanal]
    MODEL --> FUTURE[Crear dataframe futuro]
    FUTURE --> PRED[Predicción yhat]
    PRED --> UPPER[Intervalo superior yhat_upper]
    PRED --> LOWER[Intervalo inferior yhat_lower]
    UPPER --> GRAPH[Gráfica con banda de confianza]
    LOWER --> GRAPH
    PRED --> KPI[KPIs: total, promedio, pico]

    style DATA fill:#2a1a1a,stroke:#E63946,color:#E8EAF0
    style MODEL fill:#1a2a1a,stroke:#2DC653,color:#E8EAF0
    style GRAPH fill:#0d2137,stroke:#3B82F6,color:#E8EAF0
    style KPI fill:#2a2a1a,stroke:#FFB703,color:#E8EAF0
```

### Diagrama de Despliegue

```mermaid
graph TB
    subgraph CLOUD["Nube"]
        VERCEL[Vercel — Frontend]
        RENDER[Render / Railway — Backend]
        SUPABASE[Supabase — PostgreSQL]
    end

    subgraph LOCAL["Desarrollo Local"]
        VITE[npm run dev — Vite]
        UVICORN[uvicorn — FastAPI]
        CSVLOCAL[(CSV Local)]
    end

    subgraph DEV["Desarrollador"]
        PC[PC del desarrollador]
        VSCODE[VS Code]
        GITHUB[GitHub]
    end

    PC --> VSCODE
    VSCODE --> GITHUB
    GITHUB --> VERCEL
    GITHUB --> RENDER

    VERCEL --> |"HTTP requests"| RENDER
    RENDER --> |"REST API"| SUPABASE
    RENDER --> |"Lee/escribe"| CSVLOCAL

    UVICORN --> CSVLOCAL
    VITE --> |"proxy /api"| UVICORN

    style CLOUD fill:#0d2137,stroke:#3B82F6,color:#E8EAF0
    style LOCAL fill:#1a2a1a,stroke:#2DC653,color:#E8EAF0
    style DEV fill:#2a2a1a,stroke:#FFB703,color:#E8EAF0
```

### Diagrama de Pipeline de Datos

```mermaid
graph LR
    A[Fuente INE] --> B[data_generator.py]
    B --> C[Dataset calibrado]
    C --> D[CSV teleferico_lapaz.csv]
    D --> E[upload_to_supabase.py]
    E --> F[Supabase PostgreSQL]
    D --> G[FastAPI carga en memoria]
    F --> G
    G --> H[Pandas procesa]
    H --> I[Métricas, Ranking, Heatmap]
    H --> J[Prophet predice]
    I --> K[Frontend visualiza]
    J --> K

    style A fill:#2a2a1a,stroke:#FFB703,color:#E8EAF0
    style C fill:#1a2a1a,stroke:#2DC653,color:#E8EAF0
    style F fill:#0d2137,stroke:#3B82F6,color:#E8EAF0
    style K fill:#2a1a1a,stroke:#E63946,color:#E8EAF0
```

### Diagrama de Interacción del Usuario

```mermaid
stateDiagram-v2
    [*] --> Dashboard
    Dashboard --> Mapa: Click en "Mapa"
    Dashboard --> Temporal: Click en "Temporal"
    Dashboard --> Heatmap: Click en "Heatmap"
    Dashboard --> Ranking: Click en "Ranking"
    Dashboard --> Prediccion: Click en "Predicción"
    Dashboard --> Ticket: Click en "Registrar Ticket"

    Mapa --> Dashboard
    Temporal --> Dashboard
    Heatmap --> Dashboard
    Ranking --> Dashboard
    Prediccion --> Dashboard

    Ticket --> Formulario
    Formulario --> SeleccionarLínea
    SeleccionarLínea --> IngresarPasajeros
    IngresarPasajeros --> Confirmar
    Confirmar --> Éxito
    Éxito --> Dashboard

    Prediccion --> SeleccionarLínea2[Seleccionar línea]
    SeleccionarLínea2 --> DefinirDías[Definir días]
    DefinirDías --> GráficaPred[Ver gráfica]
    GráficaPred --> Dashboard
```

### Diagrama de Comparación: Datos Reales vs Simulados

```mermaid
graph TB
    subgraph REAL["Datos Reales INE"]
        R1[2015: 8.2M pasajeros]
        R2[2019: 12.5M pasajeros]
        R3[2024: 15.1M pasajeros]
    end

    subgraph SIM["Simulación Calibrada"]
        S1[Factor de escala por año]
        S2[Distribución horaria]
        S3[Patrones por línea]
    end

    subgraph RESULT["Dataset Final"]
        D1[Registros con fecha/hora]
        D2[Pasajeros calibrados]
        D3[Saturación simulada]
    end

    R1 --> S1
    R2 --> S1
    R3 --> S1
    S1 --> D1
    S2 --> D2
    S3 --> D3

    style REAL fill:#1a2a1a,stroke:#2DC653,color:#E8EAF0
    style SIM fill:#0d2137,stroke:#3B82F6,color:#E8EAF0
    style RESULT fill:#2a1a1a,stroke:#E63946,color:#E8EAF0
```

### Diagrama de Seguridad y Variables de Entorno

```mermaid
graph TB
    subgraph ENV[".env — Variables sensibles"]
        URL[SUPABASE_URL]
        KEY[SUPABASE_ANON_KEY]
        TABLE[SUPABASE_TABLE]
    end

    subgraph GITIGNORE[".gitignore"]
        GI[Excluye .env del repositorio]
    end

    subgraph CONFIG["config.py — Settings"]
        CS[Settings class]
        LOAD[dotenv load]
    end

    subgraph APP["Aplicación"]
        API2[FastAPI lee settings]
        DS2[Data Service usa settings]
    end

    LOAD --> CS
    CS --> API2
    CS --> DS2
    GI -.-> |"protege"| ENV

    style ENV fill:#2a1a1a,stroke:#E63946,color:#E8EAF0
    style GITIGNORE fill:#2a2a1a,stroke:#FFB703,color:#E8EAF0
    style CONFIG fill:#1a2a1a,stroke:#2DC653,color:#E8EAF0
    style APP fill:#0d2137,stroke:#3B82F6,color:#E8EAF0
```

### Flujo de datos
1. El dataset se genera o carga en el backend.
2. El frontend solicita datos a la API.
3. El backend filtra, agrupa y devuelve métricas.
4. Las predicciones se calculan en el servidor.
5. Los tickets nuevos se guardan localmente y se suben a Supabase.

## IV. Análisis del Proyecto

### Problema que resuelve
- Necesidad de conocer el flujo de pasajeros en el Teleférico de La Paz.
- Falta de información para tomar decisiones sobre horarios, personal y capacidad.

### Solución propuesta
- Dashboard web para visualizar datos en tiempo real.
- Predicción de demanda futura.
- Ranking de estaciones más y menos concurridas.
- Simulador de tickets para probar el sistema con nuevos registros.

### Tipo de datos
- Datos de pasajeros por línea, estación, hora y día.
- Datos geográficos de estaciones.
- Datos de saturación y demanda.

### Modelos utilizados
- Prophet para predicción de series temporales con estacionalidad.
- Regresión lineal como respaldo si Prophet no está disponible.
- Métricas agregadas con Pandas para ranking, promedios y totales.

## V. Diseño del Sistema

### Diseño del backend
- Estructura en módulos: `api.py`, `app/services/`, `app/schemas/`, `app/core/`.
- Endpoints separados por función: métricas, mapa, temporal, heatmap, ranking, predicción y tickets.
- Validación de datos con Pydantic.
- Caché en memoria para mejorar tiempos de respuesta.

### Diseño del frontend
- Componentes por sección: mapa, temporal, heatmap, ranking, predicción, tickets.
- Navegación con React Router.
- Estado global con React Query para Actualización de datos.

### Diseño de datos
- CSV como fuente local principal.
- Supabase como base de datos en la nube.
- Conversión y limpieza de datos en el backend.

## VI. Tipo de Organización del Proyecto

### Organización técnica
- Código separado en carpetas: `app/`, `frontend/`, `data/`, `tests/`.
- Dependencias controladas con `requirements.txt` y `package.json`.
- Variables de entorno en `.env`.

### Organización del trabajo
- Despiegue separado para frontend y backend.
- Uso de GitHub para control de versiones.
- Documentación en README e informe.

## VII. Consulta para ver los datos más recientes en Supabase

### SQL (desde el Editor de Supabase)
```sql
SELECT *
FROM teleferico
ORDER BY fecha DESC, hora DESC
LIMIT 20;
```

### API REST
```http
GET https://<tu-proyecto>.supabase.co/rest/v1/teleferico?order=fecha.desc,hora.desc&limit=20
```

Headers necesarios:
```json
{
  "apikey": "<SUPABASE_ANON_KEY>",
  "Authorization": "Bearer <SUPABASE_ANON_KEY>"
}
```

### Nota
Con la implementación actual, cada ticket registrado desde el simulador se sube automáticamente a Supabase como un solo registro nuevo.
