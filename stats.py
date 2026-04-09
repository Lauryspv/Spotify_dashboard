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
# PALETA DE COLORES
# =====================
COLOR_PRIMARY = "#661650"
COLOR_SECONDARY = "#8C2A6E"
COLOR_LIGHT = "#B84A8C"
COLOR_DARK = "#4A0E3A"
COLOR_ACCENT = "#D96FAA"

# NUEVO: Color complementario y su escala
COLOR_COMPLEMENTARY = "#16662C" 
COLOR_SCALE_COMPLEMENTARY = [
    [0, "#0A2912"],   # Verde muy oscuro
    [0.5, "#16662C"], # Tu color complementario
    [1, "#3DA65E"]    # Verde más claro para brillo
]

COLOR_BG_TOOLTIP = "rgba(20, 20, 20, 0.95)" # Fondo neutro oscuro para mejor lectura
COLOR_BORDER_TOOLTIP = "rgba(102, 22, 80, 0.9)"
COLOR_BORDER_TOOLTIP_COMP = "rgba(22, 102, 44, 0.9)" # Borde verde para gráficas verdes

# Escala original de púrpuras
COLOR_SCALE = [
    [0, "#4A0E3A"],
    [0.25, "#661650"],
    [0.5, "#8C2A6E"],
    [0.75, "#B84A8C"],
    [1, "#D96FAA"]
]

# =====================
# CARGAR DATOS
# =====================
@st.cache_data
def load_data():
    # Asegúrate de que el archivo existe o usa un try-except
    try:
        return pd.read_csv("playlist.csv")
    except FileNotFoundError:
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.error("No hay datos en playlist.csv. Ejecuta main.py primero.")
    st.stop()

# =====================
# CABECERA PERSONALIZADA
# =====================
st.markdown(
    f"""
    <style>
    .main-title {{
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        color: {COLOR_ACCENT};
        font-size: 42px;
        font-weight: 800;
        margin-bottom: -10px;
    }}
    .subtitle {{
        color: #888888;
        font-size: 18px;
        font-style: italic;
    }}
    </style>
    <div class="main-title">🎵 FlowState</div>
    <div class="subtitle"Mi playlist en Spotify"</div>
    """, 
    unsafe_allow_html=True
)
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
# TOOLTIP ESTILOS
# =====================
def get_hover_style(border_color):
    return dict(
        bgcolor=COLOR_BG_TOOLTIP,
        bordercolor=border_color,
        font=dict(size=13, color="white", family="Arial")
    )

# =====================
# Artistas con más canciones (Top 10)
# =====================
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
    color_continuous_scale=COLOR_SCALE,
    custom_data=["artist", "tooltip_text"]
)

fig_artists.update_traces(
    hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<extra></extra>"
)
fig_artists.update_layout(hoverlabel=get_hover_style(COLOR_BORDER_TOOLTIP), coloraxis_showscale=False)
st.plotly_chart(fig_artists, use_container_width=True)

# =====================
# Canciones por año
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
    color_continuous_scale=COLOR_SCALE,
    custom_data=["canciones_lista"]
)

fig_years.update_traces(
    hovertemplate="<b>Año: %{x}</b><br>Total: %{y} canciones<br><br><b>Canciones:</b>%{customdata[0]}<extra></extra>"
)
fig_years.update_layout(hoverlabel=get_hover_style(COLOR_BORDER_TOOLTIP), coloraxis_showscale=False)
st.plotly_chart(fig_years, use_container_width=True)

# =====================
# Artistas por actualidad
# =====================
st.subheader("📊 Comparativa de Catálogo: Actual vs. Clásico")

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
    st.markdown("### 🟣 Artistas actuales (2020+)")
    if not artistas_actuales.empty:
        fig_act = px.bar(
            artistas_actuales,
            x="canciones",
            y="artist",
            orientation="h",
            color="canciones",
            color_continuous_scale=COLOR_SCALE
        )
        fig_act.update_layout(
            yaxis={"categoryorder": "total ascending"}, 
            hoverlabel=get_hover_style(COLOR_BORDER_TOOLTIP),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_act, use_container_width=True)
    else:
        st.info("No hay artistas en esta categoría")

with col_ant:
    # APLICACIÓN DEL COLOR COMPLEMENTARIO AQUÍ
    st.markdown(f"### 🟢 Artistas anteriores a 2020")
    if not artistas_antiguos.empty:
        fig_ant = px.bar(
            artistas_antiguos,
            x="canciones",
            y="artist",
            orientation="h",
            color="canciones",
            # Usamos la escala verde para resaltar el contraste
            color_continuous_scale=COLOR_SCALE_COMPLEMENTARY 
        )
        fig_ant.update_layout(
            yaxis={"categoryorder": "total ascending"}, 
            hoverlabel=get_hover_style(COLOR_BORDER_TOOLTIP_COMP), # Borde verde en el tooltip
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_ant, use_container_width=True)
    else:
        st.info("No hay artistas en esta categoría")

# =====================
# Canciones explícitas (Movido abajo para mejor flujo visual)
# =====================
st.subheader("🚫 Análisis de contenido explícito")

explicit_counts = df["Explícita"].value_counts().reset_index()
explicit_counts.columns = ["Explícita", "count"]

fig_explicit = px.pie(
    explicit_counts, 
    names="Explícita", 
    values="count",
    color="Explícita",
    # Usamos el color principal y el complementario para máximo contraste en el pie
    color_discrete_map={"Sí": COLOR_PRIMARY, "No": COLOR_COMPLEMENTARY},
    hole=0.4
)

fig_explicit.update_traces(
    pull=[0.05, 0],
    textposition="outside",
    textinfo="label+percent",
    marker=dict(line=dict(color="#1E1E1E", width=2)),
    hovertemplate="<b>%{label}</b><br>%{value} canciones<extra></extra>"
)

fig_explicit.update_layout(
    hoverlabel=get_hover_style(COLOR_PRIMARY),
    showlegend=True,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)"
)
st.plotly_chart(fig_explicit, use_container_width=True)

# =====================
# Álbumes con más canciones (LO QUE FALTABA)
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
    color_continuous_scale=COLOR_SCALE # Mantenemos la escala púrpura para coherencia
)
fig_album.update_layout(
    yaxis={"categoryorder": "total ascending"},
    hoverlabel=get_hover_style(COLOR_BORDER_TOOLTIP),
    coloraxis_showscale=False
)
st.plotly_chart(fig_album, use_container_width=True)

st.markdown("---")

# =====================
# TABLA FINAL
# =====================
st.subheader("📋 Lista detallada de canciones")

df["cover_img"] = df["album_cover"].apply(
    lambda url: f'<img src="{url}" width="50">' if pd.notna(url) and url else ""
)

df["track_link"] = df["track_url"].apply(
    lambda url: f'<a href="{url}" target="_blank" style="color: #B84A8C; text-decoration: none;">🎧 Escuchar</a>' if pd.notna(url) and url else ""
)

table_df = df[["cover_img", "track_name", "artist", "album", "release_year", "duration_min", "Explícita", "track_link"]].copy()
table_df.columns = ["Portada", "Canción", "Artista", "Álbum", "Año", "Minutos", "Explícita", "Spotify"]

st.markdown(
    table_df.to_html(escape=False, index=False),
    unsafe_allow_html=True
)