import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

# =====================
# 1. CONFIGURACIÓN DE AUTENTICACIÓN
# =====================
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
SCOPE = "playlist-read-private"

# Crear objeto de autenticación
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE
))

# =====================
# 2. FUNCIONES
# =====================
def fetch_playlist_tracks(playlist_id):
    """
    Devuelve todas las canciones de una playlist en una lista de diccionarios
    con popularidad real, duración en minutos y campo 'Explícita' claro.
    """
    results = sp.playlist_items(playlist_id, additional_types=["track"])
    tracks = results["items"]

    # Si hay más de 100 canciones, paginamos
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])

    # --- Paso 1: obtener IDs válidos de las canciones ---
    track_ids = [item["track"]["id"] for item in tracks if item.get("track") and item["track"].get("id")]

    # --- Paso 2: recuperar información detallada (popularidad real) ---
    popularity_dict = {}
    for i in range(0, len(track_ids), 50):  # Spotify permite máx. 50 IDs por lote
        batch = sp.tracks(track_ids[i:i+50])
        for t in batch["tracks"]:
            popularity_dict[t["id"]] = t.get("popularity", 0)

    # --- Paso 3: construir la lista final de canciones ---
    all_tracks = []
    for item in tracks:
        track = item.get("track") or item.get("item")

        if track and track.get("id"):  # Aseguramos que haya un track válido y que no sea un archivo local sin ID
            all_tracks.append({
                "track_name": track.get("name", "Desconocido"),
                "artist": ", ".join([artist["name"] for artist in track.get("artists", [])]) if track.get("artists") else "Desconocido",
                "album": track["album"]["name"] if track.get("album") else "Desconocido",
                "release_date": track["album"].get("release_date", "Desconocido") if track.get("album") else "Desconocido",
                # ⚙️ Nueva: carátula del álbum
                "album_cover": track["album"]["images"][0]["url"] if track.get("album") and track["album"].get("images") else "",
                "duration_min": round(track.get("duration_ms", 0) / 60000, 2),
                "Explícita": "Sí" if track.get("explicit") else "No",
                "track_url": track["external_urls"].get("spotify", "") if track.get("external_urls") else ""
    })
    return all_tracks


# =====================
# 3. DESCARGAR PLAYLIST
# =====================
# Cambia esto por la URL o ID de tu playlist
playlist_id ="https://open.spotify.com/playlist/2sRr4MvsBcXAWdjFlYWDbV?si=3753c3a990874171"

tracks_data = fetch_playlist_tracks(playlist_id)

# =====================
# 4. GUARDAR EN CSV
# =====================
df = pd.DataFrame(tracks_data)
df.to_csv("playlist.csv", index=False)
print(f"Se han descargado {len(df)} canciones y guardado en 'playlist.csv'")

# =====================
# 5. VISTA PREVIA
# =====================
print(df.head())