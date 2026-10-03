# Playlist Analyser

A small Windows desktop app for generating a short mood and style summary from a Spotify playlist. Choose **Gemini** for cloud analysis or **Qwen3 (local Ollama)** to run the model locally.

## Requirements

- Python 3.10 or newer
- A Spotify developer app with its Client ID, Client Secret, and Redirect URI
- A Gemini API key if you want to use Gemini
- Ollama with the `qwen3:8b` model if you want to use Qwen3

## Install

Install the dependencies from `requirements.txt`:

```powershell
python -m pip install -r requirements.txt
```

Create a `.env` file in the project folder with your credentials:

```dotenv
CLIENT_ID=your_spotify_client_id
CLIENT_SECRET=your_spotify_client_secret
REDIRECT_URI=http://127.0.0.1:8888/callback
GEMINI_API_KEY=your_gemini_api_key
```

Set the same Redirect URI in your Spotify developer app settings. Keep `.env` private; do not commit or share it.

For Qwen3, install Ollama, make sure its local service is running, and download the model:

```powershell
ollama pull qwen3:8b
```

## Run

```powershell
python app.py
```

Paste a Spotify playlist URL, choose a model, and select **Analyse playlist**. The first time you authorize Spotify access, a browser window may open so you can sign in and approve access. The Gemini model also requires a valid `GEMINI_API_KEY`.

## Spotify access and policy

Spotify's [current playlist items documentation](https://developer.spotify.com/documentation/web-api/reference/get-playlists-items) limits playlist item access to playlists owned by, or shared with, the connected account. Other playlists may fail even when their links are public.