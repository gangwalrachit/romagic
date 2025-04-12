from musicxmatch_api import MusixMatchAPI
from romagic.lyrics.romanizer import Romanizer, Lang
from typing import List, Union, Dict


class MusixMatch:
    """
    Wrapper for the MusixMatch API to fetch track data, lyrics, and translations.
    """

    def __init__(self, track_isrc: str) -> None:
        """
        Initialize with a track's ISRC (International Standard Recording Code).

        :param track_isrc: ISRC of the track
        """
        self.track_isrc = track_isrc
        self.api = MusixMatchAPI()

    def get_track(self) -> Dict[str, Union[str, Dict]]:
        """
        Get metadata for the track.

        :return: Track data as a dictionary
        """
        return self.api.get_track(track_isrc=self.track_isrc)

    def get_track_lyrics(self) -> Dict[str, Union[str, List, None]]:
        """
        Get lyrics and apply romanization if the language is supported.

        :return: Dictionary with flags and versions of lyrics:
            - is_romanized: whether romanization was applied
            - original: original lyrics
            - romanized: romanized full text (or None)
            - combined: list of (original, romanized) line tuples if romanized
        """
        lyrics_data = self.api.get_track_lyrics(track_isrc=self.track_isrc)
        lyrics = lyrics_data["message"]["body"]["lyrics"]["lyrics_body"]
        lang_code = lyrics_data["message"]["body"]["lyrics"].get(
            "lyrics_language", "en"
        )

        try:
            lang = Lang(lang_code)
        except ValueError:
            lang = Lang.EN  # fallback for unsupported languages

        return Romanizer(lyrics, lang).run()

    def get_track_lyrics_translation(self) -> Dict[str, Union[str, Dict]]:
        """
        Get translated lyrics if available.

        :return: Translation data as a dictionary
        """
        return self.api.get_track_lyrics_translation(track_isrc=self.track_isrc)
