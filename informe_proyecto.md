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
- Computación en la Nube: uso de servicios PaaS para despliegue y almacenamiento (Streamlit Cloud, Supabase).
- Visualización de datos: dashboards interactivos con Streamlit, Plotly y Folium.
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
- PaaS: Streamlit Cloud para el dashboard.
- DBaaS: Supabase para almacenamiento de datos y futura integración.
- Computación en la nube: uso de Python en un entorno gestionado para análisis y predicción.

#### Modelo de Implementación
- Implementación híbrida: datos generados localmente y consumidos por la app web.
- Posible despliegue en la nube usando GitHub + Streamlit Cloud.

### Evaluación de la Infraestructura
#### a. Selección del proveedor
- Streamlit Cloud: ideal para apps de datos rápidas y gratuitas.
- Supabase: base de datos PostgreSQL en la nube con API REST y autenticación gratuita.

#### b. Diseño de la Arquitectura
- `data_generator.py` genera dataset sintético.
- `app.py` procesa y visualiza datos.
- `README.md` documenta el proyecto.
- `data/teleferico_lapaz.csv` almacena el dataset.

#### c. Lista de servicios y descripción
- Streamlit Cloud: despliegue del dashboard como servicio web.
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
- Streamlit: https://streamlit.io
- Supabase: https://supabase.com
- Prophet: https://facebook.github.io/prophet/
- Folium: https://python-visualization.github.io/folium/
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
