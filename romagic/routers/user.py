from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from spotipy import Spotify
from spotipy.exceptions import SpotifyException
from sqlalchemy.orm import Session

from romagic.database import User, get_db
from romagic.lyrics.genius import fetch_lyrics


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
    # Fetch user_id from the session
    user_id = request.session.get("user_id")

    if not user_id:
        # Render the template with login option for unauthenticated users
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "authenticated": False},
        )

    # Fetch user-specific information from the database
    user = db.query(User).filter(User.id == user_id).first()

    if user:
        # Fetch user-specific information
        user_info = user.user_info
        user_name = user_info.get("display_name", user_id)
        user_profile_url = user_info.get("external_urls", {}).get("spotify")

        # Check if the user has profile images, if not, set a default placeholder
        user_pfp = "https://via.placeholder.com/150"  # Default image
        if user_info.get("images"):
            user_pfp = user_info["images"][0].get("url", user_pfp)

        # Fetch the user's token information
        token_info = user.token_info

        # Initialize Spotify client with the access token
        sp = Spotify(auth=token_info["access_token"])

        # Fetch the user's top 50 tracks and artists
        try:
            current_track = sp.current_user_playing_track()
            track_lyrics = fetch_lyrics(
                current_track["item"]["name"],
                current_track["item"]["artists"][0]["name"],
            )

            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "user_name": user_name,
                    "user_profile_url": user_profile_url,
                    "user_pfp": user_pfp,
                    "current_track": current_track,
                    "track_lyrics": track_lyrics,
                    "authenticated": True,
                },
            )
        except SpotifyException as e:
            # If the access token has expired, redirect to the login page
            return templates.TemplateResponse(
                "index.html",
                {"request": request, "authenticated": False},
            )
        except TypeError as e:
            # If the user is not playing any track currently
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "user_name": user_name,
                    "user_profile_url": user_profile_url,
                    "user_pfp": user_pfp,
                    "current_track": None,
                    "track_lyrics": "No track playing",
                    "authenticated": True,
                },
            )

    # If the user is not found in the database, redirect to the login page
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "authenticated": False},
    )
