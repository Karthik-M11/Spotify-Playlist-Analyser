import json
import os
import re
import spotipy
from dotenv import load_dotenv
from google import genai
from ollama import chat
from spotipy.exceptions import SpotifyException
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()


def _spotify_client():
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        redirect_uri=os.getenv("REDIRECT_URI"),
        scope="playlist-read-private playlist-read-collaborative",
    ))


def get_playlist_data(playlist_id):
    data = []
    sp = _spotify_client()
    try:
        results = sp.playlist_tracks(playlist_id)
    except SpotifyException as exc:
        if exc.http_status in (403, 404):
            raise ValueError(
                "Spotify would not provide this playlist's tracks. Its current API "
                "only exposes playlist items for playlists owned by your connected "
                "Spotify account or playlists you collaborate on. Try one of those playlists."
            ) from exc
        raise
    while results is not None:
        for item in results["items"]:
            track = item.get("item") or item.get("track")
            if not track:
                continue
            data.append({
                "song_name": track.get("name"),
                "artists": ", ".join(a["name"] for a in track.get("artists", [])),
                "album": track.get("album", {}).get("name"),
                "is_explicit": track.get("explicit"),
            })
        try:
            results = sp.next(results) if results.get("next") else None
        except SpotifyException as exc:
            if exc.http_status in (403, 404):
                raise ValueError(
                    "Spotify would not provide the remaining playlist tracks. "
                    "Try a playlist owned by your connected Spotify account or one you collaborate on."
                ) from exc
            raise
    return data


def ask_gemini(playlist, question, api_key):
    """Load playlist tracks when given a Spotify link/ID, then analyze them."""
    match = re.search(r"(?:playlist/)?([A-Za-z0-9]{22})(?:[?&#/]|$)", playlist.strip())
    if match:
        tracks = get_playlist_data(match.group(1))
        playlist_data = json.dumps(tracks[:20], ensure_ascii=False, indent=2)
    else:
        playlist_data = playlist.strip()

    prompt = f"""{question}

Analyze the playlist's mood, emotional atmosphere, likely genres or time period
preferences, and overall vibe. Use a fun, sassy tone. Write 5-7 sentences, no
bullets, and do not suggest songs.

Playlist tracks/data:
{playlist_data}"""
    client = genai.Client(api_key=api_key)
    chat_session = client.chats.create(model="gemini-3.8-flash")
    response = chat_session.send_message(prompt)
    return response.text.strip()


def ask_qwen3(playlist, question):
    """Analyze a Spotify playlist URL/ID or pasted track list with local Ollama Qwen3."""
    match = re.search(r"(?:playlist/)?([A-Za-z0-9]{22})(?:[?&#/]|$)", playlist.strip())
    if match:
        tracks = get_playlist_data(match.group(1))
        playlist_data = json.dumps(tracks[:20], ensure_ascii=False, indent=2)
    else:
        playlist_data = playlist.strip()

    prompt = f"""{question}

Analyze the playlist's mood, emotional atmosphere, likely genres or time period
preferences, and overall vibe. Use a fun, sassy tone. Write 5-7 sentences, no
bullets, and do not suggest songs.

Playlist tracks/data:
{playlist_data}"""
    response = chat(
        model="qwen3:8b",
        messages=[{"role": "user", "content": prompt}],
    )
    message = response.get("message", {})
    return message.get("content", "").strip()
