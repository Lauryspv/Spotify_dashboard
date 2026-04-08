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
    """
    results = sp.playlist_items(playlist_id, additional_types=["track"])
    tracks = results["items"]

    # Si hay más de 100 canciones, paginamos
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])

    all_tracks = []
    for item in tracks:
        # Dependiendo del endpoint/parámetros en la API de Spotify,
        # la canción puede estar bajo la clave "track" o "item"
        track = item.get("track") or item.get("item")
        
        if track and track.get("id"):  # Aseguramos que haya un track válido y que no sea un archivo local sin ID
            all_tracks.append({
                "track_name": track.get("name", "Desconocido"),
                "artist": ", ".join([artist["name"] for artist in track.get("artists", [])]) if track.get("artists") else "Desconocido",
                "album": track["album"]["name"] if track.get("album") else "Desconocido",
                "release_date": track["album"]["release_date"] if track.get("album") and "release_date" in track["album"] else "Desconocido",
                "popularity": track.get("popularity", 0),
                "duration_ms": track.get("duration_ms", 0),
                "track_url": track["external_urls"]["spotify"] if track.get("external_urls") and "spotify" in track["external_urls"] else ""
            })
    return all_tracks

# =====================
# 3. DESCARGAR PLAYLIST
# =====================
# Cambia esto por la URL o ID de tu playlist
playlist_id = "https://open.spotify.com/playlist/2sRr4MvsBcXAWdjFlYWDbV?si=7784e35e62e24d68"

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