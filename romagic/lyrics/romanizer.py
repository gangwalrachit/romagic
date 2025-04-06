from enum import Enum
import pykakasi
from hangul_romanize import Transliter
from hangul_romanize.rule import academic


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


def romanize(text: str, lang: Lang) -> str:
    """
    Romanize lyrics based on the language provided.

    :param text: Original lyrics text
    :param lang: Language enum of the lyrics
    :return: Romanized or original text based on the language
    """
    if lang == Lang.JA.value:
        return romanize_japanese(text)
    elif lang == Lang.KO.value:
        return romanize_korean(text)
    return text  # fallback for unsupported or English


def romanize_japanese(text: str) -> str:
    """
    Romanize Japanese text using Hepburn system with word spacing.

    :param text: Japanese lyrics
    :return: Romanized lyrics
    """
    kakasi = pykakasi.kakasi()
    kakasi.setMode("H", "a")  # Hiragana to ascii
    kakasi.setMode("K", "a")  # Katakana to ascii
    kakasi.setMode("J", "a")  # Japanese to ascii
    kakasi.setMode("r", "Hepburn")  # Use Hepburn Romanization
    kakasi.setMode("s", True)  # Add spaces between words

    converter = kakasi.getConverter()
    return converter.do(text)


def romanize_korean(text: str) -> str:
    """
    Romanize Korean text using academic transliteration rules.

    :param text: Korean lyrics
    :return: Romanized lyrics
    """
    transliter = Transliter(rule=academic)
    return transliter.translit(text)
