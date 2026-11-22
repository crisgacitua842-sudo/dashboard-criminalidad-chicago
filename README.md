# Patrones de criminalidad en Chicago (2015-2016)

Dashboard interactivo del examen de Taller de Visualización de la Información 2026-2 (UDD). Toma el análisis exploratorio del Certamen 2 y lo convierte en una app donde el usuario elige qué ver.

**Pregunta que responde:** ¿dónde, cuándo y qué tipo de delitos se concentran en Chicago, y cómo cambió el arresto en 2016?

**Usuario objetivo:** equipos de planificación de patrullaje (policía o municipio) que necesitan decidir en qué zonas y horarios poner recursos.

**App publicada:** ENLACE_APP

**Versión actual:** beta 2.1.0 (Hito 1)

![Captura del dashboard](docs/captura_beta.png)

## Qué tiene la app

- Filtros globales en el panel lateral: año, tipo de delito y rango de horas. Si el filtro deja la tabla vacía, la app avisa y se detiene.
- KPIs con `st.metric`: cantidad de delitos, % con arresto y % de violencia doméstica (comparados contra el total sin filtros) y tipo más frecuente.
- Pestañas:
  - **Qué delitos:** top 10 por tipo o por lugar (control local) y treemap de arresto dentro de los 8 tipos más frecuentes.
  - **Cuándo:** delitos por mes, % de arresto por mes y heatmap de día de la semana y hora.
  - **Dónde:** mapa de puntos (`px.scatter_map`) con una muestra de 30.000 delitos (`random_state=42`) y color elegible, mapa de densidad (`px.density_map`) y su interpretación.
  - **Relaciones:** % de narcóticos contra % de arresto en las 77 Community Areas.
- Hallazgos principales del Certamen 2 y tabla de datos filtrados en un `st.expander`.

Todos los gráficos están hechos con Plotly Express y se muestran con `st.plotly_chart`.

## Datos

Crimes in Chicago (Kaggle, usuario currie32), archivo `Chicago_Crimes_2012_to_2017.csv`: https://www.kaggle.com/datasets/currie32/crimes-in-chicago

Se usan los datos limpios del Certamen 2: años 2015 y 2016, Location Description vacía como "Sin dato", sin las 2 filas sin Ward y con NON-CRIMINAL unificado. Quedan 528.455 delitos y 10 columnas en `data/chicago_2015_2016_limpio.csv.gz` (7 MB comprimido, bajo el límite de 25 MB), así que la app trabaja con todos los registros. Solo el mapa de puntos usa una muestra de 30.000 con `random_state=42`, y el mapa de densidad agrupa los delitos en celdas de 0,001 grados.

Los 17.389 delitos sin coordenadas se mantienen en la base y se excluyen solo de los mapas.

## Cómo correrla en tu computador

```
pip install -r requirements.txt
streamlit run app.py
```

## Estructura

```
app.py                       la app
requirements.txt             librerías
.streamlit/config.toml       colores de la app
data/chicago_2015_2016_limpio.csv.gz   datos limpios del Certamen 2
preparar_datos.py            limpieza del CSV de Kaggle (igual al Certamen 2)
docs/captura_beta.png        captura para este README
```

## Integrantes

Diego Sabando, Julio Cerda y Cristóbal Gacitúa.
