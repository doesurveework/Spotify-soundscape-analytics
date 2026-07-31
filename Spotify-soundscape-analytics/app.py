from flask import Flask, request, redirect, jsonify, session, render_template
import spotipy
from spotipy.exceptions import SpotifyException
from spotipy.oauth2 import SpotifyOAuth
import os
from datetime import datetime, timezone
from personality_engine import calculate_metrics
from models import get_engine, init_db, get_session, User, Artist, Track, ListeningHistory, Snapshot

app = Flask(__name__, template_folder='frontend/templates', static_folder='frontend/static')
app.secret_key = os.urandom(24)
# --- Database setup ---
engine = get_engine()
init_db(engine)
#
SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID", "YOUR_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET", "YOUR_CLIENT_SECRET")

REDIRECT_URI = "http://127.0.0.1:5000/callback"
SCOPE = "user-top-read user-read-recently-played"

sp_oauth = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE
)

def get_spotify_client():
    token_info = session.get('token_info', None)


    if not token_info or not isinstance(token_info, dict):
        return None


    try:
        if sp_oauth.is_token_expired(token_info):
            token_info = sp_oauth.refresh_access_token(token_info.get('refresh_token'))
            session['token_info'] = token_info
    except Exception as e:
        print(f"Error refreshing token: {e}")
        return None

    return spotipy.Spotify(auth=token_info['access_token'])


# --- Routes ---

@app.route('/')
def index():
    if not session.get('token_info'):
        return redirect('/login')
    return redirect('/dashboard')


@app.route('/login')
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return redirect('/login')

    # Get complete token info dictionary
    token_info = sp_oauth.get_access_token(code)

    # Store token dictionary in the Flask session
    session['token_info'] = token_info

    return redirect('/dashboard')


@app.route('/dashboard')
def dashboard():
    return render_template('index.html')


@app.route('/dashboard-data')
def dashboard_data():
    sp = get_spotify_client()
    if not sp:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        # Fetch Spotify top tracks
        results = sp.current_user_top_tracks(limit=20, time_range='short_term')
        raw_tracks = results.get('items', [])

        if not raw_tracks:
            return jsonify({'tracks': [], 'metrics': None})

        tracks = []
        for track in raw_tracks:
            tracks.append({
                'id': track.get('id'),
                'name': track.get('name', 'Unknown Track'),
                'popularity': track.get('popularity', 0),
                'album': track.get('album', {}),
                'artists': track.get('artists', [])
            })

        track_ids = [t['id'] for t in tracks if t.get('id')]


        features_list = []
        try:
            audio_feats = sp.audio_features(track_ids)
            features_list = [f for f in audio_feats if f is not None] if audio_feats else []
        except Exception as e:
            print(f"Spotify Audio Features restricted (403): {e}")


        is_fallback = False
        if features_list:
            try:
                metrics = calculate_metrics(raw_tracks, features_list)
            except Exception as pe_err:
                print(f"Warning: personality_engine error ({pe_err}). Falling back to simple metrics.")
                features_list = []  # Triggers fallback calculation below

        if not features_list:
            is_fallback = True
            avg_pop = sum(t['popularity'] for t in tracks) / len(tracks) if tracks else 0
            obscurity_score = round(100 - avg_pop)

            metrics = {
                'personalityType': 'Sonic Explorer',
                'obscurityScore': obscurity_score,
                'averages': {
                    'energy': 0.50,
                    'danceability': 0.50,
                    'valence': 0.50
                },
                'is_fallback': is_fallback
            }

        # Make sure fallback flag is present in metrics response
        if isinstance(metrics, dict):
            metrics['is_fallback'] = is_fallback

        # 4. Save snapshot to database silently
        try:
            _save_snapshot(sp, raw_tracks, features_list, metrics)
        except Exception as db_err:
            print(f"Warning: Failed to save database snapshot: {db_err}")

        return jsonify({
            'tracks': tracks,
            'metrics': metrics
        })

    except Exception as e:
        print(f"Server error in /dashboard-data: {e}")
        return jsonify({'error': str(e)}), 500


def _save_snapshot(sp, tracks_data, features_data, metrics):
    db = get_session(engine)
    try:
        me = sp.current_user()

        user = db.query(User).filter_by(spotify_id=me['id']).first()
        if not user:
            user = User(
                spotify_id=me['id'],
                display_name=me.get('display_name'),
                email=me.get('email'),
            )
            db.add(user)
            db.flush()  # get user.id before using it below

        for track_data in tracks_data:
            artist_data = track_data['artists'][0] if track_data.get('artists') else None
            artist = None
            if artist_data:
                artist = db.query(Artist).filter_by(spotify_id=artist_data['id']).first()
                if not artist:
                    artist = Artist(
                        spotify_id=artist_data['id'],
                        followers=None,
                        genres=None,
                    )
                    db.add(artist)
                    db.flush()

            track = db.query(Track).filter_by(spotify_id=track_data['id']).first()
            if not track:
                feat = next(
                    (f for f in features_data if f and f.get('id') == track_data['id']), None
                )
                track = Track(
                    spotify_id=track_data['id'],
                    artist_id=artist.id if artist else None,
                    danceability=feat['danceability'] if feat else None,
                    energy=feat['energy'] if feat else None,
                    tempo=feat['tempo'] if feat else None,
                )
                db.add(track)
                db.flush()

            db.add(ListeningHistory(
                user_id=user.id,
                track_id=track.id,
                played_at=datetime.now(timezone.utc),
            ))

        month_key = datetime.now(timezone.utc).strftime("%Y-%m")
        snapshot = db.query(Snapshot).filter_by(user_id=user.id, month=month_key).first()
        if not snapshot:
            snapshot = Snapshot(user_id=user.id, month=month_key)
            db.add(snapshot)

        snapshot.obscurity_score = metrics.get("obscurityScore")
        snapshot.diversity_score = getattr(snapshot, 'diversity_score', None)
        snapshot.discovery_score = getattr(snapshot, 'discovery_score', None)

        db.commit()
    finally:
        db.close()


if __name__ == '__main__':
    app.run(port=5000, debug=True)



