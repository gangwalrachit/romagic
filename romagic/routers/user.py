from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from spotipy import Spotify
from spotipy.exceptions import SpotifyException
from sqlalchemy.orm import Session

from romagic.database import User, get_db
from romagic.lyrics.musixmatch import MusixMatch

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    """
    Home page view with login option.
    If the user is authenticated, display personalized content;
    otherwise, show the login button.

    :param request: FastAPI Request object
    :param db: Database session object
    :return: Rendered HTML template
    """
    user_id = request.session.get("user_id")

    if not user_id:
        # User is not logged in, render basic index with login option
        return templates.TemplateResponse(
            "index.html", {"request": request, "authenticated": False}
        )

    # Look up the user in the database
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        # If somehow user doesn't exist in DB, treat as unauthenticated
        return templates.TemplateResponse(
            "index.html", {"request": request, "authenticated": False}
        )

    # Extract profile data from user's stored Spotify info
    user_info = user.user_info
    user_name = user_info.get("display_name", user_id)
    user_profile_url = user_info.get("external_urls", {}).get("spotify")

    # Fallback to placeholder image if no profile picture is available
    user_pfp = user_info.get("images", [{}])[0].get(
        "url", "https://via.placeholder.com/150"
    )

    # Create a Spotify client using stored access token
    token_info = user.token_info
    sp = Spotify(auth=token_info["access_token"])

    try:
        # Attempt to get the user's currently playing track
        current_track = sp.current_user_playing_track()
        isrc = current_track["item"]["external_ids"]["isrc"]

        # Initialize MusixMatch with the track's ISRC
        mxm = MusixMatch(track_isrc=isrc)
        lyrics_data = mxm.get_track_lyrics()

        # Render personalized page with track and lyrics
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "authenticated": True,
                "user_name": user_name,
                "user_profile_url": user_profile_url,
                "user_pfp": user_pfp,
                "current_track": current_track,
                "is_romanized": lyrics_data.get("is_romanized", False),
                "original_lyrics": lyrics_data.get("original", None),
                "romanized_lyrics": lyrics_data.get("romanized", None),
                "combined_lyrics": lyrics_data.get("combined", None),
            },
        )

    except SpotifyException:
        # Spotify token might be invalid or expired
        return templates.TemplateResponse(
            "index.html", {"request": request, "authenticated": False}
        )

    except (TypeError, KeyError):
        # Happens when no track is currently playing or something is missing in the data
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "authenticated": True,
                "user_name": user_name,
                "user_profile_url": user_profile_url,
                "user_pfp": user_pfp,
                "current_track": None,
                "lyrics_lines": ["No track playing."],
                "is_romanized": False,
            },
        )
