import pandas as pd
import streamlit as st
import plotly.express as px

# =====================
# CONFIGURACIÓN GENERAL
# =====================
st.set_page_config(
    page_title="FlowState Dashboard",
    page_icon="🎧",
    layout="wide"
)

# =====================
# CARGAR DATOS
# =====================
@st.cache_data
def load_data():
    return pd.read_csv("playlist.csv")

df = load_data()

if df.empty:
    st.error("No hay datos en playlist.csv. Ejecuta main.py primero.")
    st.stop()

# =====================
# CABECERA: TÍTULO Y COVER PRINCIPAL
# =====================
st.markdown("## 🎵 *FlowState* — Mi Playlist en Spotify")
st.markdown("---")

# Mostrar carátulas (solo primeras 6)
st.subheader("🎨 Portadas destacadas")
cols = st.columns(6)
for i, col in enumerate(cols):
    if i < len(df):
        img = df.loc[i, "album_cover"]
        if pd.notna(img) and img:
            col.image(img, width=150)

st.markdown("---")

# =====================
# KPIs
# =====================
total_songs = len(df)
artists_unique = df["artist"].nunique()
albums_unique = df["album"].nunique()
avg_duration = round(df["duration_min"].mean(), 2)
explicit_percent = round((df["Explícita"].eq("Sí").sum() / total_songs) * 100, 1)

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("🎶 Canciones", total_songs)
col2.metric("🎤 Artistas únicos", artists_unique)
col3.metric("💽 Álbumes únicos", albums_unique)
col4.metric("⏱️ Duración media (min)", avg_duration)
col5.metric("🚫 % Explícitas", f"{explicit_percent}%")

st.markdown("---")

# =====================
# GRÁFICOS
# =====================

# Canciones por artista (Top 10)
st.subheader("🏆 Artistas con más canciones en la playlist (Top 10)")
top_artists = (
    df.groupby("artist")["track_name"]
    .count()
    .sort_values(ascending=False)
    .head(10)
    .reset_index(name="song_count")
)

top_artists["tooltip_text"] = top_artists["song_count"].apply(
    lambda x: f"{x} canción" if x == 1 else f"{x} canciones"
)

fig_artists = px.bar(
    top_artists, x="song_count", y="artist",
    orientation="h",
    color="song_count",
    labels={"song_count": "Canciones"},
    color_continuous_scale="viridis",
    custom_data=["artist", "tooltip_text"]
)

fig_artists.update_traces(
    hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<extra></extra>"
)

fig_artists.update_layout(
    hoverlabel=dict(
        bgcolor="rgba(180, 60, 180, 0.9)",
        bordercolor="rgba(255, 100, 255, 0.8)",
        font=dict(size=14, color="white", family="Arial Black")
    )
)

st.plotly_chart(fig_artists, use_container_width=True)

# =====================
# Porcentaje de explícitas
# =====================
st.subheader("🚫 Canciones explícitas / no explícitas")

explicit_counts = df["Explícita"].value_counts().reset_index()
explicit_counts.columns = ["Explícita", "count"]

fig_explicit = px.pie(
    explicit_counts, 
    names="Explícita", 
    values="count",
    color="Explícita",
    color_discrete_map={"Sí": "#FF006E", "No": "#8338EC"},
    hole=0.4
)

fig_explicit.update_traces(
    pull=[0.05, 0.05],
    textposition="outside",
    textinfo="label+percent+value",
    textfont=dict(size=14, color="white"),
    marker=dict(line=dict(color="white", width=3)),
    rotation=45,
    hovertemplate="<b>%{label}</b><br>%{value} canciones<br>%{percent}<extra></extra>"
)

fig_explicit.update_layout(
    hoverlabel=dict(
        bgcolor="rgba(30, 30, 30, 0.9)",
        bordercolor="rgba(255, 255, 255, 0.3)",
        font=dict(size=14, color="white")
    ),
    showlegend=True,
    legend=dict(font=dict(size=12, color="white"), bgcolor="rgba(0,0,0,0)"),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    annotations=[
        dict(
            text="Explícitas",
            x=0.5, y=0.5,
            font=dict(size=18, color="white", family="Arial Black"),
            showarrow=False
        )
    ]
)

st.plotly_chart(fig_explicit, use_container_width=True)

# =====================
# Canciones por año de lanzamiento
# =====================
st.subheader("📅 Canciones por año de lanzamiento")
df["release_year"] = df["release_date"].astype(str).str[:4]

songs_by_year = (
    df.groupby("release_year")
    .agg(
        songs=("track_name", "count"),
        canciones_lista=("track_name", lambda x: "<br>• " + "<br>• ".join(x))
    )
    .reset_index()
)

fig_years = px.bar(
    songs_by_year, 
    x="release_year", 
    y="songs",
    color="songs", 
    color_continuous_scale="Blues",
    custom_data=["canciones_lista"]
)

fig_years.update_traces(
    hovertemplate="<b>Año: %{x}</b><br>Total: %{y} canciones<br><br><b>Canciones:</b>%{customdata[0]}<extra></extra>"
)

fig_years.update_layout(
    hoverlabel=dict(
        bgcolor="rgba(255, 182, 193, 0.95)",
        bordercolor="rgba(255, 105, 180, 0.9)",
        font=dict(size=12, color="#333333", family="Arial")
    )
)

st.plotly_chart(fig_years, use_container_width=True)

# =====================
# Artistas por actualidad
# =====================
st.subheader("📊 Artistas según actualidad de sus canciones")

artista_año_max = df.groupby("artist")["release_year"].apply(lambda x: x.astype(int).max()).reset_index()
artista_año_max.columns = ["artist", "año_mas_reciente"]

artista_año_max["categoria"] = artista_año_max["año_mas_reciente"].apply(
    lambda y: "Actual (2020+)" if y >= 2020 else "Anterior a 2020"
)

canciones_por_artista = df.groupby("artist")["track_name"].count().reset_index(name="canciones")
artistas_clasificados = artista_año_max.merge(canciones_por_artista, on="artist")

artistas_actuales = (
    artistas_clasificados[artistas_clasificados["categoria"] == "Actual (2020+)"]
    .sort_values("canciones", ascending=False)
)

artistas_antiguos = (
    artistas_clasificados[artistas_clasificados["categoria"] == "Anterior a 2020"]
    .sort_values("canciones", ascending=False)
)

col_act, col_ant = st.columns(2)

with col_act:
    st.markdown("### 🟢 Artistas actuales (2020+)")
    if not artistas_actuales.empty:
        fig_act = px.bar(
            artistas_actuales,
            x="canciones",
            y="artist",
            orientation="h",
            color="canciones",
            color_continuous_scale="Greens"
        )
        fig_act.update_layout(yaxis={"categoryorder": "total ascending"}, showlegend=False)
        st.plotly_chart(fig_act, use_container_width=True)
    else:
        st.info("No hay artistas en esta categoría")

with col_ant:
    st.markdown("### ⚫ Artistas anteriores a 2020")
    if not artistas_antiguos.empty:
        fig_ant = px.bar(
            artistas_antiguos,
            x="canciones",
            y="artist",
            orientation="h",
            color="canciones",
            color_continuous_scale="Greys"
        )
        fig_ant.update_layout(yaxis={"categoryorder": "total ascending"}, showlegend=False)
        st.plotly_chart(fig_ant, use_container_width=True)
    else:
        st.info("No hay artistas en esta categoría")

# =====================
# Álbumes con más canciones
# =====================
st.subheader("💿 Álbumes con más canciones en mi playlist (Top 10)")
album_counts = (
    df.groupby("album")["track_name"]
    .count()
    .sort_values(ascending=False)
    .head(10)
    .reset_index(name="canciones")
)

fig_album = px.bar(
    album_counts, 
    x="canciones", 
    y="album",
    orientation="h",
    color="canciones", 
    color_continuous_scale="Purples"
)
fig_album.update_layout(yaxis={"categoryorder": "total ascending"})
st.plotly_chart(fig_album, use_container_width=True)

# =====================
# TABLA FINAL CON MINIATURAS
# =====================
st.subheader("📋 Lista de canciones")

df["cover_img"] = df["album_cover"].apply(
    lambda url: f'<img src="{url}" width="50">' if pd.notna(url) and url else ""
)

df["track_link"] = df["track_url"].apply(
    lambda url: f'<a href="{url}" target="_blank">🔗 Abrir</a>' if pd.notna(url) and url else ""
)

table_df = df[["cover_img", "track_name", "artist", "album", "release_date", "duration_min", "Explícita", "track_link"]].copy()
table_df.columns = ["Portada", "Canción", "Artista", "Álbum", "Fecha", "Duración (min)", "Explícita", "Spotify"]

st.markdown(
    table_df.to_html(escape=False, index=False),
    unsafe_allow_html=True
)




