import pandas as pd
import streamlit as st
import plotly.express as px

# ==========================================
# 1. CONFIGURACIÓN Y PALETA DE COLORES
# ==========================================
st.set_page_config(page_title="FlowState Dashboard", page_icon="🎧", layout="wide")

COLOR_PRIMARY = "#661650"      # Púrpura Base
COLOR_ACCENT = "#D96FAA"       # Púrpura Brillante
COLOR_COMPLEMENTARY = "#16662C" # Verde Bosque (Complementario)

# Escalas para degradados
SCALE_PURPLE = [[0, "#4A0E3A"], [0.5, "#8C2A6E"], [1, "#D96FAA"]]
SCALE_GREEN = [[0, "#0A2912"], [0.5, "#16662C"], [1, "#3DA65E"]]

COLOR_BG_TOOLTIP = "rgba(20, 20, 20, 0.95)"
COLOR_BORDER_PURPLE = "rgba(217, 111, 170, 0.8)"
COLOR_BORDER_GREEN = "rgba(61, 166, 94, 0.8)"

# ==========================================
# 2. ESTILOS CSS PERSONALIZADOS
# ==========================================
def apply_custom_styles():
    st.markdown(f"""
        <style>
        .main-title {{
            font-family: 'Helvetica Neue', Helvetica, sans-serif;
            color: {COLOR_ACCENT};
            font-size: 48px; font-weight: 800; margin-bottom: -10px;
        }}
        .subtitle {{
            color: #888888; font-size: 18px; font-style: italic; margin-bottom: 20px;
        }}
        [data-testid="stMetricValue"] {{ color: {COLOR_ACCENT}; font-size: 32px; }}
        table {{ width: 100%; border-collapse: collapse; color: white; background-color: #1A1A1A; border-radius: 10px; }}
        th {{ background-color: {COLOR_PRIMARY}; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #333; }}
        tr:hover {{ background-color: #262626; }}
        img {{ border-radius: 5px; }}
        </style>
    """, unsafe_allow_html=True)

apply_custom_styles()

# ==========================================
# 3. CARGA Y PROCESAMIENTO DE DATOS
# ==========================================
@st.cache_data
def load_data():
    try:
        data = pd.read_csv("playlist.csv")
        data["release_year"] = data["release_date"].astype(str).str[:4]
        return data
    except:
        return pd.DataFrame()

df = load_data()
if df.empty:
    st.error("Error: No se encontró playlist.csv")
    st.stop()

def update_fig_style(fig, border_color):
    fig.update_layout(
        hoverlabel=dict(
            bgcolor=COLOR_BG_TOOLTIP,
            bordercolor=border_color,
            font=dict(size=13, color="white", family="Arial")
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False
    )

# ==========================================
# 4. CABECERA Y KPIs
# ==========================================
st.markdown('<div class="main-title">🎵 FlowState</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Análisis visual de mi playlist en Spotify</div>', unsafe_allow_html=True)
st.markdown("---")

total_songs = len(df)
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("🎶 Canciones", total_songs)
col2.metric("🎤 Artistas", df["artist"].nunique())
col3.metric("💽 Álbumes", df["album"].nunique())
col4.metric("⏱️ Media (min)", round(df["duration_min"].mean(), 2))
col5.metric("🚫 % Explícitas", f"{round((df['Explícita'].eq('Sí').sum()/total_songs)*100,1)}%")

st.markdown("---")

# ==========================================
# SECCIÓN 1: IDENTIDAD MUSICAL
# ==========================================
st.header("👤 Perfil de la Playlist: Artistas y Álbumes")
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("🏆 Top Artistas")
    top_artists = df.groupby("artist")["track_name"].count().sort_values(ascending=False).head(10).reset_index(name="songs")
    fig_art = px.bar(top_artists, x="songs", y="artist", orientation="h",
                     color="songs", color_continuous_scale=SCALE_PURPLE)
    fig_art.update_traces(hovertemplate="<b>%{y}</b><br>%{x} canciones<extra></extra>")
    update_fig_style(fig_art, COLOR_BORDER_PURPLE)
    st.plotly_chart(fig_art, use_container_width=True)

with col_b:
    st.subheader("💿 Top Álbumes")
    top_albums = df.groupby("album")["track_name"].count().sort_values(ascending=False).head(10).reset_index(name="songs")
    fig_alb = px.bar(top_albums, x="songs", y="album", orientation="h",
                     color="songs", color_continuous_scale=SCALE_GREEN)
    fig_alb.update_traces(hovertemplate="<b>%{y}</b><br>%{x} canciones<extra></extra>")
    update_fig_style(fig_alb, COLOR_BORDER_GREEN)
    st.plotly_chart(fig_alb, use_container_width=True)

# ==========================================
# SECCIÓN 2: LÍNEA DEL TIEMPO
# ==========================================
st.markdown("---")
st.header("📅 Cronología del Catálogo")

artista_año_max = df.groupby("artist")["release_year"].apply(lambda x: x.astype(int).max()).reset_index()
artista_año_max["categoria"] = artista_año_max["release_year"].apply(lambda y: "Actual (2020+)" if y >= 2020 else "Anterior a 2020")
canciones_counts = df.groupby("artist")["track_name"].count().reset_index(name="count")
clasificados = artista_año_max.merge(canciones_counts, on="artist")

c1, c2 = st.columns(2)
with c1:
    st.markdown("#### 🟣 Artistas Actuales (2020+)")
    df_act = clasificados[clasificados["categoria"]=="Actual (2020+)"].sort_values("count", ascending=False).head(10)
    fig_act = px.bar(df_act, x="count", y="artist", orientation="h", color="count", color_continuous_scale=SCALE_PURPLE)
    fig_act.update_traces(hovertemplate="<b>%{y}</b><br>%{x} canciones<extra></extra>")
    update_fig_style(fig_act, COLOR_BORDER_PURPLE)
    st.plotly_chart(fig_act, use_container_width=True)

with c2:
    st.markdown("#### 🟢 Artistas Clásicos (< 2020)")
    df_ant = clasificados[clasificados["categoria"]=="Anterior a 2020"].sort_values("count", ascending=False).head(10)
    fig_ant = px.bar(df_ant, x="count", y="artist", orientation="h", color="count", color_continuous_scale=SCALE_GREEN)
    fig_ant.update_traces(hovertemplate="<b>%{y}</b><br>%{x} canciones<extra></extra>")
    update_fig_style(fig_ant, COLOR_BORDER_GREEN)
    st.plotly_chart(fig_ant, use_container_width=True)

st.subheader("📈 Lanzamientos por Año")
songs_year = df.groupby("release_year").agg(count=("track_name", "count"), lista=("track_name", lambda x: "<br>• " + "<br>• ".join(x[:5]))).reset_index()
fig_yr = px.bar(songs_year, x="release_year", y="count", color="count", color_continuous_scale=SCALE_PURPLE, custom_data=["lista"])
fig_yr.update_traces(hovertemplate="<b>Año %{x}</b><br>Total: %{y}<br><i>Ejemplos:</i>%{customdata[0]}<extra></extra>")
update_fig_style(fig_yr, COLOR_BORDER_PURPLE)
st.plotly_chart(fig_yr, use_container_width=True)

# ==========================================
# SECCIÓN 3: ANÁLISIS DE TIEMPO Y DURACIÓN
# ==========================================
st.markdown("---")
st.header("⏱️ Análisis de Tiempo y Duración")

m1, m2, m3 = st.columns(3)
m1.metric("⌛ Duración Total", f"{round(df['duration_min'].sum()/60, 1)} hrs")
m2.metric("🎯 Duración Media", f"{round(df['duration_min'].mean(), 2)} min")
m3.metric("📉 Variabilidad", f"{round(df['duration_min'].std(), 2)} min")

sub_l, sub_s = st.columns(2)
with sub_l:
    st.markdown("#### 🟣 Las 5 más extensas")
    top_l = df.nlargest(5, "duration_min")
    fig_l = px.bar(top_l, x="duration_min", y="track_name", orientation="h", text="duration_min", color_discrete_sequence=[COLOR_PRIMARY])
    fig_l.update_traces(texttemplate='%{text} min', textposition='outside', hovertemplate="<b>%{y}</b><br>%{x} min<extra></extra>")
    update_fig_style(fig_l, COLOR_BORDER_PURPLE)
    fig_l.update_layout(height=350, yaxis={'categoryorder':'total ascending', 'title':''})
    st.plotly_chart(fig_l, use_container_width=True)

with sub_s:
    st.markdown("#### 🟢 Las 5 más breves")
    top_s = df.nsmallest(5, "duration_min")
    fig_s = px.bar(top_s, x="duration_min", y="track_name", orientation="h", text="duration_min", color_discrete_sequence=[COLOR_COMPLEMENTARY])
    fig_s.update_traces(texttemplate='%{text} min', textposition='outside', hovertemplate="<b>%{y}</b><br>%{x} min<extra></extra>")
    update_fig_style(fig_s, COLOR_BORDER_GREEN)
    fig_s.update_layout(height=350, yaxis={'categoryorder':'total descending', 'title':''})
    st.plotly_chart(fig_s, use_container_width=True)

# ==========================================
# SECCIÓN 4: CONTENIDO EXPLÍCITO (EFECTO DONUT PÚRPURA)
# ==========================================
st.markdown("---")
st.header("🚫 Análisis de Contenido")
col_pie_left, col_pie_center, col_pie_right = st.columns([1, 2, 1])

with col_pie_center:
    exp_data = df["Explícita"].value_counts().reset_index()
    exp_data.columns = ["Explícita", "count"]
    
    fig_pie = px.pie(
        exp_data, 
        names="Explícita", 
        values="count", 
        hole=0.5,
        color="Explícita", 
        color_discrete_map={"Sí": COLOR_PRIMARY, "No": COLOR_COMPLEMENTARY}
    )
    
    fig_pie.update_traces(
        textinfo="percent+label", 
        hovertemplate="<b>%{label}</b><br>%{value} canciones<extra></extra>",
        marker=dict(line=dict(color='#1A1A1A', width=2))
    )
    
    # Aplicamos el estilo base
    update_fig_style(fig_pie, COLOR_ACCENT)
    
    # AÑADIMOS EL CÍRCULO PÚRPURA EN EL HUECO Y EL TEXTO NEGRO
    fig_pie.update_layout(
        shapes=[
            dict(
                type="circle",
                xref="paper", yref="paper",
                x0=0.36, y0=0.21, x1=0.64, y1=0.79, # Coordenadas para llenar el hueco
                fillcolor=COLOR_PRIMARY,
                line_color=COLOR_PRIMARY,
                layer="below"
            )
        ],
        annotations=[dict(
            text='Explícitas', 
            x=0.5, y=0.5, 
            font_size=22, 
            font_color="black", # TEXTO EN NEGRO
            font_family="Arial Black",
            showarrow=False
        )],
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
    )
    
    st.plotly_chart(fig_pie, use_container_width=True)

# ==========================================
# SECCIÓN 5: EXPLORADOR DE DATOS
# ==========================================
st.markdown("---")
st.subheader("📋 Lista Detallada de Canciones")
df["Portada"] = df["album_cover"].apply(lambda x: f'<img src="{x}" width="50">' if pd.notna(x) else "")
df["Spotify"] = df["track_url"].apply(lambda x: f'<a href="{x}" target="_blank" style="color:{COLOR_ACCENT}; text-decoration:none;">🎧 Escuchar</a>')
table_cols = ["Portada", "track_name", "artist", "album", "release_year", "duration_min", "Explícita", "Spotify"]
st.markdown(df[table_cols].to_html(escape=False, index=False), unsafe_allow_html=True)