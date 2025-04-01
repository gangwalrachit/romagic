import requests

from bs4 import BeautifulSoup
from typing import Dict, Tuple, Optional

from romagic.config import GENIUS_ACCESS_TOKEN


def fetch_lyrics(track_name: str, artist_name: str) -> str:
    """
    Fetches and formats lyrics for a given track and artist.

    :param track_name: Name of the track
    :param artist_name: Name of the artist
    :return: Formatted lyrics or "Lyrics not found" message
    """
    lyrics = get_lyrics_from_genius(track_name, artist_name)
    return lyrics if lyrics else "Lyrics not found."


def get_lyrics_from_genius(track_name: str, artist_name: str) -> Optional[str]:
    """
    Queries Genius API to fetch the lyrics URL and scrapes lyrics if available.

    :param track_name: Name of the track
    :param artist_name: Name of the artist
    :return: Formatted lyrics if found, else None
    """
    headers = {"Authorization": f"Bearer {GENIUS_ACCESS_TOKEN}"}
    search_url = "https://api.genius.com/search"
    params = {"q": f"{track_name} {artist_name}"}

    try:
        response = requests.get(search_url, headers=headers, params=params)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching data from Genius API: {e}")
        return None

    lyrics_url, is_romanized = extract_lyrics_url(response.json())

    if not lyrics_url:
        print("Lyrics URL not found on Genius.")
        return None

    if not is_romanized:
        print("Romanized lyrics not found, using original lyrics.")

    raw_lyrics = scrape_lyrics_from_url(lyrics_url)
    return format_lyrics(raw_lyrics) if raw_lyrics else None


def extract_lyrics_url(response: Dict) -> Tuple[Optional[str], bool]:
    """
    Extracts the romanized or original lyrics URL from the Genius API response.

    :param response: JSON response from Genius API
    :return: Tuple containing the lyrics URL (if found) and a boolean indicating if it's romanized
    """
    hits = response.get("response", {}).get("hits", [])

    # Look for Romanized lyrics first
    for hit in hits:
        artist_name = hit["result"].get("primary_artist", {}).get("name", "")
        if "Genius Romanizations" in artist_name:
            return hit["result"]["url"], True

    # If no Romanized version is found, return the first available lyrics URL
    return (hits[0]["result"]["url"], False) if hits else (None, False)


def scrape_lyrics_from_url(lyrics_url: str) -> Optional[str]:
    """
    Scrapes the lyrics from the provided Genius lyrics page.

    :param lyrics_url: URL of the Genius lyrics page
    :return: Extracted lyrics as a string or None if not found
    """
    # TODO: check song and artu=ist name on lyrics page to avoid wrong lyrics (note to compare language)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.google.com/",
        "DNT": "1",  # Do Not Track request header
        "Connection": "keep-alive",
    }
    try:
        response = requests.get(lyrics_url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to retrieve Genius lyrics page: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    lyrics_divs = soup.find_all("div", {"data-lyrics-container": "true"})

    if not lyrics_divs:
        print("No lyrics found on the page.")
        return None

    # Extract text from all found divs and join them
    lyrics = "\n".join(div.get_text("\n", strip=True) for div in lyrics_divs)
    return lyrics.strip()


def format_lyrics(lyrics: str) -> str:
    """
    Formats the lyrics for better readability by ensuring proper line spacing.

    - Adds an extra blank line before section headers (e.g., [Intro], [Chorus])
    - Keeps existing line breaks intact

    :param lyrics: Raw lyrics string
    :return: Formatted lyrics string
    """
    formatted_lines = []
    lines = lyrics.splitlines()

    for i, line in enumerate(lines):
        line = line.strip()

        # Add an extra line break before section headers
        if line.startswith("[") and line.endswith("]") and i > 0:
            formatted_lines.append("")  # Blank line before section header

        formatted_lines.append(line)

    return "\n".join(formatted_lines)
