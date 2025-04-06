from musicxmatch_api import MusixMatchAPI
from romagic.lyrics.romanizer import romanize


def fetch_lyrics(track_isrc: str) -> str:
    """
    Fetch lyrics for a given track ISRC using MusixMatchAPI,
    and romanize them if they are not in English.

    :param track_isrc: International Standard Recording Code (ISRC)
    :return: Processed lyrics - romanized if not in English
    """
    api = MusixMatchAPI()
    lyrics_data = api.get_track_lyrics(track_isrc=track_isrc)

    lyrics = lyrics_data["message"]["body"]["lyrics"]["lyrics_body"]
    lang_code = lyrics_data["message"]["body"]["lyrics"].get("lyrics_language", "en")

    return romanize(lyrics, lang_code)
