from decouple import config
from spotipy.oauth2 import SpotifyOAuth


# Session secret key for FastAPI app
SESSION_SECRET_KEY = config("SESSION_SECRET_KEY")

# Database details
DATABASE_URL = config("DATABASE_URL", default="sqlite:///./spotispy.db")

# Spotify credentials and OAuth setup
SPOTIFY_CLIENT_ID = config("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = config("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = config("SPOTIFY_REDIRECT_URI")
SPOTIFY_SCOPE = (
    "user-read-currently-playing"  # Scope to read user's currently playing track
)

sp_oauth = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope=SPOTIFY_SCOPE,
    cache_path=None,  # Disable cache
)

# Genius API Credentials
GENIUS_CLIENT_ID = config("GENIUS_CLIENT_ID")
GENIUS_CLIENT_SECRET = config("GENIUS_CLIENT_SECRET")
GENIUS_ACCESS_TOKEN = config("GENIUS_ACCESS_TOKEN")
