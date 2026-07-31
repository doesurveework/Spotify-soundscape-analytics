# Spotify Soundscape Analytics 🎧

A Flask web app that connects to your Spotify account and analyzes your recent listening habits — turning your top tracks into a "listener personality," an obscurity score, and mood/energy averages. Each visit snapshots your stats to a local database so you can track how your taste evolves over time.

## Features

- **Spotify OAuth login** — securely connects to your Spotify account (`user-top-read`, `user-read-recently-played` scopes)
- **Top tracks dashboard** — pulls your top 20 tracks (short-term listening window)
- **Listener personality engine** — classifies your taste into types like *Kinetic Hedonist*, *Melancholic Introspector*, *Solar Optimist*, or *Sonic Eclectic* based on audio features (energy, danceability, valence)
- **Obscurity score** — how mainstream vs. niche your listening is, based on track popularity
- **Graceful fallback** — if Spotify's audio-features endpoint is unavailable, falls back to a simplified popularity-based score so the dashboard still works
- **Historical snapshots** — persists users, artists, tracks, listening history, and monthly snapshots to a database via SQLAlchemy

## Tech Stack

- **Backend:** Flask, Spotipy (Spotify Web API client)
- **Database:** SQLAlchemy ORM (SQLite by default)
- **Frontend:** HTML/CSS/JS (served via Flask templates/static files)

## Project Structure

```
Spotify-soundscape-analytics/
├── app.py                  # Flask app, routes, OAuth flow, dashboard API
├── models.py                # SQLAlchemy models (User, Artist, Track, ListeningHistory, Snapshot)
├── personality_engine.py    # Computes obscurity score + personality type from audio features
└── frontend/
    ├── templates/
    │   └── index.html       # Dashboard page
    └── static/
        ├── css/
        └── js/
requirements.txt
```

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/doesurveework/spotify-soundscape-analytics.git
cd spotify-soundscape-analytics
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create a Spotify app

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) and create an app.
2. Add `http://127.0.0.1:5000/callback` as a Redirect URI in your app settings.
3. Note your **Client ID** and **Client Secret**.

### 4. Set environment variables

```bash
export SPOTIFY_CLIENT_ID="your_client_id"
export SPOTIFY_CLIENT_SECRET="your_client_secret"
```

### 5. Run the app

```bash
cd Spotify-soundscape-analytics
python app.py
```

Visit `http://127.0.0.1:5000` in your browser, log in with Spotify, and view your dashboard.

## How It Works

1. **Login (`/login`)** redirects to Spotify's OAuth authorization page.
2. **Callback (`/callback`)** exchanges the auth code for an access token, stored in the Flask session.
3. **Dashboard (`/dashboard`)** renders the frontend, which calls `/dashboard-data`.
4. **`/dashboard-data`** fetches your top tracks and their audio features from Spotify, computes your personality/obscurity metrics, saves a snapshot to the database, and returns everything as JSON for the frontend to render.

## Database Schema

- **Users** — Spotify account info
- **Artists** — artist metadata
- **Tracks** — track metadata + audio features (danceability, energy, tempo)
- **ListeningHistory** — per-user, per-track listening events
- **Snapshots** — monthly rollup of a user's obscurity/diversity/discovery scores

The SQLite database file (`soundscape.db`) is created automatically on first run.

## Notes

- Spotify's `audio-features` endpoint may be restricted for some apps/accounts; when unavailable, the app falls back to a simpler popularity-based obscurity score so the dashboard doesn't break.
- Uses the `short_term` time range (approx. last 4 weeks) for top tracks.

## License

No license specified yet — add one if you plan to share or open source this project.
