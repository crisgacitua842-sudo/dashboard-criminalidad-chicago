# Dashboard: Patrones de criminalidad en Chicago (2015-2016)
# Taller de Visualizacion de la Informacion 2026-2 - Version beta 2.1.0

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Criminalidad en Chicago", layout="wide")

ROJO = "#B0262E"
GRIS = "#8E939A"
COLORES_ANIO = {"2015": GRIS, "2016": ROJO}
DIAS = ["Lun", "Mar", "Mie", "Jue", "Vie", "Sab", "Dom"]

# Nombres de las 77 Community Areas de Chicago
AREAS = {
    1: "Rogers Park", 2: "West Ridge", 3: "Uptown", 4: "Lincoln Square", 5: "North Center",
    6: "Lake View", 7: "Lincoln Park", 8: "Near North Side", 9: "Edison Park", 10: "Norwood Park",
    11: "Jefferson Park", 12: "Forest Glen", 13: "North Park", 14: "Albany Park", 15: "Portage Park",
    16: "Irving Park", 17: "Dunning", 18: "Montclare", 19: "Belmont Cragin", 20: "Hermosa",
    21: "Avondale", 22: "Logan Square", 23: "Humboldt Park", 24: "West Town", 25: "Austin",
    26: "West Garfield Park", 27: "East Garfield Park", 28: "Near West Side", 29: "North Lawndale",
    30: "South Lawndale", 31: "Lower West Side", 32: "Loop", 33: "Near South Side", 34: "Armour Square",
    35: "Douglas", 36: "Oakland", 37: "Fuller Park", 38: "Grand Boulevard", 39: "Kenwood",
    40: "Washington Park", 41: "Hyde Park", 42: "Woodlawn", 43: "South Shore", 44: "Chatham",
    45: "Avalon Park", 46: "South Chicago", 47: "Burnside", 48: "Calumet Heights", 49: "Roseland",
    50: "Pullman", 51: "South Deering", 52: "East Side", 53: "West Pullman", 54: "Riverdale",
    55: "Hegewisch", 56: "Garfield Ridge", 57: "Archer Heights", 58: "Brighton Park", 59: "McKinley Park",
    60: "Bridgeport", 61: "New City", 62: "West Elsdon", 63: "Gage Park", 64: "Clearing",
    65: "West Lawn", 66: "Chicago Lawn", 67: "West Englewood", 68: "Englewood",
    69: "Greater Grand Crossing", 70: "Ashburn", 71: "Auburn Gresham", 72: "Beverly",
    73: "Washington Heights", 74: "Mount Greenwood", 75: "Morgan Park", 76: "O'Hare", 77: "Edgewater",
}


def numero(n):
    return f"{n:,}".replace(",", ".")


def pct(x):
    return f"{x:.1f} %".replace(".", ",")


# Carga de datos (datos limpios del Certamen 2)
@st.cache_data
def cargar_datos():
    df = pd.read_csv("data/chicago_2015_2016_limpio.csv.gz", parse_dates=["Date"])
    df["Anio"] = df["Year"].astype(str)
    df["Mes"] = df["Date"].dt.month
    df["Hora"] = df["Date"].dt.hour
    df["Dia"] = df["Date"].dt.dayofweek.map(dict(enumerate(DIAS)))
    df["Area"] = df["Community Area"].map(AREAS)
    df["Arresto"] = df["Arrest"].map({True: "Con arresto", False: "Sin arresto"})
    df["Domestico"] = df["Domestic"].map({True: "Doméstico", False: "No doméstico"})
    return df


df = cargar_datos()

# Encabezado
st.title("Patrones de criminalidad en Chicago, 2015-2016")
st.markdown(
    "**Pregunta del dashboard:** ¿dónde, cuándo y qué tipo de delitos se concentran en Chicago, "
    "y cómo cambió el arresto en 2016?"
)
st.caption(
    "Para equipos de planificación de patrullaje. Datos: Crimes in Chicago (Kaggle), "
    "528.455 delitos limpios del Certamen 2. Versión beta 2.1.0."
)

# Filtros globales
st.sidebar.header("Filtros")
anios = st.sidebar.multiselect("Año", ["2015", "2016"], default=["2015", "2016"])
lista_tipos = df["Primary Type"].value_counts().index.tolist()
tipos = st.sidebar.multiselect(
    "Tipo de delito", lista_tipos, placeholder="Todos los tipos",
    help="Si lo dejas vacío se muestran todos los tipos."
)
horas = st.sidebar.slider("Hora del día", 0, 23, (0, 23))

df_f = df[df["Anio"].isin(anios) & df["Hora"].between(horas[0], horas[1])]
if tipos:
    df_f = df_f[df_f["Primary Type"].isin(tipos)]

if df_f.empty:
    st.warning("No hay delitos con esos filtros. Cambia la selección en el panel lateral.")
    st.stop()

st.sidebar.caption(f"{numero(len(df_f))} delitos seleccionados de {numero(len(df))}.")

# KPIs
arresto_total = df["Arrest"].mean() * 100
domestico_total = df["Domestic"].mean() * 100
arresto_f = df_f["Arrest"].mean() * 100
domestico_f = df_f["Domestic"].mean() * 100

k1, k2, k3, k4 = st.columns(4)
k1.metric("Delitos", numero(len(df_f)), delta=f"{pct(len(df_f) / len(df) * 100)} del total", delta_color="off")
k2.metric("Con arresto", pct(arresto_f), delta=f"{arresto_f - arresto_total:+.1f} pp frente al total".replace(".", ","))
k3.metric("Violencia doméstica", pct(domestico_f),
          delta=f"{domestico_f - domestico_total:+.1f} pp frente al total".replace(".", ","), delta_color="inverse")
k4.metric("Tipo más frecuente", df_f["Primary Type"].mode()[0])

tab1, tab2, tab3, tab4 = st.tabs(["Qué delitos", "Cuándo", "Dónde", "Relaciones"])

# ---------------- Que delitos ----------------
with tab1:
    c1, c2 = st.columns([3, 2])
    with c1:
        # Control local: solo afecta a este grafico
        ver_por = st.selectbox("Ver el top 10 por", ["Tipo de delito", "Lugar del delito"])
        col = "Primary Type" if ver_por == "Tipo de delito" else "Location Description"
        top = df_f[col].value_counts().head(10).reset_index()
        top.columns = [ver_por, "Delitos"]
        top["Porcentaje"] = (top["Delitos"] / len(df_f) * 100).round(2)
        fig = px.bar(top, x="Delitos", y=ver_por, orientation="h", text="Delitos",
                     hover_data={"Porcentaje": ":.2f"}, color_discrete_sequence=[ROJO],
                     title=f"Top 10 por {ver_por.lower()}")
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, xaxis_title="Cantidad de delitos", yaxis_title="")
        st.plotly_chart(fig)
    with c2:
        top8 = df_f["Primary Type"].value_counts().head(8).index
        arbol = df_f[df_f["Primary Type"].isin(top8)].groupby(["Primary Type", "Arresto"]).size().reset_index(name="Delitos")
        fig = px.treemap(arbol, path=["Primary Type", "Arresto"], values="Delitos", color="Arresto",
                         color_discrete_map={"Con arresto": ROJO, "Sin arresto": "#D9D5CF", "(?)": "#F4F2EE"},
                         title="Arresto dentro de los 8 tipos más frecuentes")
        fig.update_traces(hovertemplate="%{label}<br>Delitos: %{value:,}<br>%{percentParent:.1%} de su tipo<extra></extra>")
        st.plotly_chart(fig)

# ---------------- Cuando ----------------
with tab2:
    c1, c2 = st.columns(2)
    with c1:
        por_mes = df_f.groupby(["Anio", "Mes"]).size().reset_index(name="Delitos")
        fig = px.line(por_mes, x="Mes", y="Delitos", color="Anio", markers=True, color_discrete_map=COLORES_ANIO,
                      labels={"Anio": "Año", "Mes": "Mes (1 = enero)", "Delitos": "Cantidad de delitos"},
                      title="Delitos por mes")
        fig.update_xaxes(dtick=1)
        st.plotly_chart(fig)
    with c2:
        arresto_mes = (df_f.groupby(["Anio", "Mes"])["Arrest"].mean() * 100).round(2).reset_index(name="Arresto")
        fig = px.line(arresto_mes, x="Mes", y="Arresto", color="Anio", markers=True, color_discrete_map=COLORES_ANIO,
                      labels={"Anio": "Año", "Mes": "Mes (1 = enero)", "Arresto": "Delitos con arresto (%)"},
                      title="Porcentaje de delitos con arresto por mes")
        fig.update_xaxes(dtick=1)
        st.plotly_chart(fig)

    tabla = pd.crosstab(df_f["Dia"], df_f["Hora"]).reindex(DIAS).fillna(0)
    fig = px.imshow(tabla, color_continuous_scale="Reds", aspect="auto",
                    labels={"x": "Hora del día (0 a 23)", "y": "Día de la semana", "color": "Delitos"},
                    title="Delitos por día de la semana y hora")
    fig.update_xaxes(dtick=1)
    st.plotly_chart(fig)

# ---------------- Donde ----------------
with tab3:
    nulos = df_f["Latitude"].isnull().sum()
    ceros = ((df_f["Latitude"] == 0) | (df_f["Longitude"] == 0)).sum()
    fuera = ((df_f["Latitude"] < 41.6) | (df_f["Latitude"] > 42.1) | (df_f["Longitude"] < -88) | (df_f["Longitude"] > -87.5)).sum()
    df_mapa = df_f.dropna(subset=["Latitude", "Longitude"])
    st.caption(
        f"Coordenadas inválidas: {numero(nulos)} sin ubicación, {numero(ceros)} en cero y {numero(fuera)} fuera de Chicago. "
        f"Se excluyen solo de los mapas; quedan {numero(len(df_mapa))} delitos con ubicación."
    )

    centro = {"lat": 41.835, "lon": -87.70}
    # Control local: color de los puntos
    color_por = st.selectbox("Color de los puntos", ["Tipo de delito", "Arresto", "Violencia doméstica"])
    muestra = df_mapa.sample(min(30000, len(df_mapa)), random_state=42).copy()
    top8_mapa = df_mapa["Primary Type"].value_counts().head(8).index
    muestra["Tipo de delito"] = muestra["Primary Type"].where(muestra["Primary Type"].isin(top8_mapa), "OTRO")
    muestra["Violencia doméstica"] = muestra["Domestico"]
    orden = {"Tipo de delito": list(top8_mapa) + ["OTRO"], "Arresto": ["Con arresto", "Sin arresto"],
             "Violencia doméstica": ["Doméstico", "No doméstico"]}
    fig = px.scatter_map(muestra, lat="Latitude", lon="Longitude", color=color_por,
                         category_orders=orden, hover_name="Primary Type",
                         hover_data={"Area": True, "Location Description": True, "Date": "|%d-%m-%Y %H:%M",
                                     "Latitude": False, "Longitude": False, color_por: False},
                         labels={"Area": "Community Area", "Location Description": "Lugar", "Date": "Fecha"},
                         center=centro, zoom=9.5, height=750, opacity=0.5, map_style="carto-positron",
                         title=f"Mapa de puntos (muestra de {numero(len(muestra))}, random_state=42)")
    fig.update_traces(marker={"size": 4})
    st.plotly_chart(fig)

    # Se agrupan los delitos en celdas de 0,001 grados para no dibujar medio millon de puntos
    grilla = df_mapa.assign(Latitud=df_mapa["Latitude"].round(3), Longitud=df_mapa["Longitude"].round(3))
    grilla = grilla.groupby(["Latitud", "Longitud"]).size().reset_index(name="Delitos")
    fig = px.density_map(grilla, lat="Latitud", lon="Longitud", z="Delitos", radius=8,
                         hover_data={"Delitos": True, "Latitud": ":.3f", "Longitud": ":.3f"},
                         center=centro, zoom=9.5, height=750, map_style="carto-positron",
                         color_continuous_scale="Reds",
                         title="Mapa de densidad (delitos por celda de 0,001 grados)")
    st.plotly_chart(fig)

    st.markdown(
        "**Interpretación (con todos los datos).** Los delitos se concentran en dos núcleos a la misma latitud, cerca de 41,88: "
        "el centro (Loop y Near North Side), compacto y con la mayor densidad, y el oeste (Austin, West Garfield Park y "
        "Humboldt Park), que es la zona más extensa. En el sur hay focos más débiles entre 41,74 y 41,80 (Englewood, "
        "Greater Grand Crossing y South Shore). El norte tiene poca actividad y O'Hare aparece como un punto aislado al noroeste. "
        "Esto implica que el patrullaje no debería repartirse de forma pareja: el centro concentra hurtos y el oeste y el sur, "
        "violencia, casos domésticos y narcóticos."
    )

# ---------------- Relaciones ----------------
with tab4:
    areas = df_f.groupby("Area").agg(
        Delitos=("Primary Type", "size"),
        Arresto=("Arrest", "mean"),
        Narcoticos=("Primary Type", lambda s: (s == "NARCOTICS").mean()),
        Domestico=("Domestic", "mean"),
    ).reset_index()
    for c in ["Arresto", "Narcoticos", "Domestico"]:
        areas[c] = (areas[c] * 100).round(1)
    fig = px.scatter(areas, x="Narcoticos", y="Arresto", size="Delitos", color="Domestico",
                     hover_name="Area", hover_data={"Delitos": ":,", "Domestico": ":.1f"},
                     color_continuous_scale="Reds", size_max=40,
                     labels={"Narcoticos": "Delitos de narcóticos en el área (%)",
                             "Arresto": "Delitos con arresto en el área (%)",
                             "Domestico": "Domésticos (%)"},
                     title="Arresto y narcóticos en las 77 Community Areas (tamaño = cantidad de delitos)")
    st.plotly_chart(fig)
    if len(areas) > 2:
        r = areas["Narcoticos"].corr(areas["Arresto"])
        st.caption(f"Correlación de Pearson entre % de narcóticos y % de arresto con los filtros actuales: {r:.2f}".replace(".", ","))
    st.caption("Si filtras por tipo de delito, los porcentajes se calculan dentro de los tipos elegidos.")

# Hallazgos
st.subheader("Hallazgos principales (Certamen 2)")
h1, h2, h3 = st.columns(3)
h1.markdown("**Dos perfiles de ciudad.** El centro y el norte concentran hurtos (53,4 % en el Loop); "
            "el oeste y el sur, violencia, casos domésticos y narcóticos.")
h2.markdown("**El quiebre de 2016.** El total casi no cambia (+0,9 %), pero los homicidios suben 55,3 % "
            "y el arresto baja de 26,4 % a 19,0 %.")
h3.markdown("**El arresto depende del delito.** Narcóticos tiene 99,9 % de arresto y robo a vivienda 4,4 %. "
            "El % de arresto de un área refleja sus casos de drogas.")

# Datos filtrados
with st.expander("Ver datos filtrados"):
    st.dataframe(df_f[["Date", "Primary Type", "Location Description", "Arresto", "Domestico", "District",
                       "Area", "Latitude", "Longitude"]].head(1000), hide_index=True)
    st.caption(f"Primeras 1.000 filas de {numero(len(df_f))}.")
