import pykakasi

from enum import Enum
from hangul_romanize import Transliter
from hangul_romanize.rule import academic
from typing import List, Dict, Tuple, Union, Optional


class Lang(Enum):
    """
    Enum for supported languages.

    EN: English
    JA: Japanese
    KO: Korean
    """

    EN = "en"
    JA = "ja"
    KO = "ko"


class Romanizer:
    """
    Romanizes lyrics based on language.
    """

    def __init__(self, text: str, lang: Lang) -> None:
        """
        Initialize the Romanizer with text and language.

        :param text: Original lyrics
        :param lang: Language enum
        """
        self.text = text
        self.lang = lang
        self.romanize_fn = None

        if lang == Lang.JA:
            self._init_japanese()
        elif lang == Lang.KO:
            self._init_korean()

    def _init_japanese(self) -> None:
        """
        Set up romanizer for Japanese using pykakasi.
        """
        kakasi = pykakasi.kakasi()
        kakasi.setMode("H", "a")
        kakasi.setMode("K", "a")
        kakasi.setMode("J", "a")
        kakasi.setMode("r", "Hepburn")
        kakasi.setMode("s", True)
        kakasi.setMode("C", True)
        self.romanize_fn = kakasi.getConverter().do

    def _init_korean(self) -> None:
        """
        Set up romanizer for Korean using hangul_romanize.
        """
        self.romanize_fn = Transliter(rule=academic).translit

    def run(self) -> Dict[str, Union[str, bool, Optional[List[Tuple[str, str]]]]]:
        """
        Run romanization and return results.

        :return: Dictionary with flags and versions of lyrics:
            - is_romanized: whether romanization was applied
            - original: original lyrics
            - romanized: romanized full text (or None)
            - combined: list of (original, romanized) line tuples if romanized
        """
        if not self.romanize_fn:
            return {
                "is_romanized": False,
                "original": self.text,
                "romanized": None,
                "combined": None,
            }

        lines = [line.strip() for line in self.text.splitlines() if line.strip()]
        return {
            "is_romanized": True,
            "original": self.text,
            "romanized": self.romanize_fn(self.text),
            "combined": [(line, self.romanize_fn(line)) for line in lines],
        }
