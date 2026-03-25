import re
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Patterns de détection
# ---------------------------------------------------------------------------

# BPM : nombre entre 60 et 249 isolé par des non-chiffres
BPM_PATTERN = re.compile(r'(?<!\d)(6[0-9]|[7-9][0-9]|1[0-9]{2}|2[0-3][0-9])(?!\d)')

# Séparateur : underscore, tiret, espace (utilisé pour isoler les tokens)
SEP = r'(?<=[_\-\s])'
END = r'(?=$|[_\-\s])'

# Tonalités — construites explicitement pour éviter les faux positifs
_NOTES       = r'[A-G]'
_SHARP_FLAT  = r'(?:#|b)?'
_MINOR       = r'(?:m|min|minor)'
_MAJOR       = r'(?:maj|major)'

# Mineur avec ou sans bémol/dièse : Am, C#m, Bbmin, F#minor
KEY_MINOR = re.compile(
    SEP + r'(' + _NOTES + _SHARP_FLAT + _MINOR + r')' + END,
    re.IGNORECASE
)

# Tonalité entre parenthèses : (C), (F#), (Am)
KEY_PARENTHESES = re.compile(
    r'\((' + _NOTES + _SHARP_FLAT + r'(?:' + _MINOR + r'|' + _MAJOR + r')?' + r')\)',
    re.IGNORECASE
)

# Majeur explicite — jamais en début de nom
KEY_MAJOR_EXPLICIT = re.compile(
    SEP + r'(' + _NOTES + _SHARP_FLAT + _MAJOR + r')' + END,
    re.IGNORECASE
)

# Majeur implicite — jamais en début de nom
KEY_MAJOR_IMPLICIT = re.compile(
    SEP + r'(' + _NOTES + _SHARP_FLAT + r')' + END
)

# Camelot : 1A-12A (mineur) ou 1B-12B (majeur)
KEY_CAMELOT = re.compile(
    SEP + r'((?:1[0-2]|[1-9])[AB])' + END,
    re.IGNORECASE
)



# ---------------------------------------------------------------------------
# Dataclass résultat
# ---------------------------------------------------------------------------

@dataclass
class ParseResult:
    bpm: str | None          # ex: "140"
    key: str | None          # ex: "Am", "C#maj", "7A"
    key_warning: bool        # True si tonalité majeure implicite (ambiguë)
    clean_stem: str          # nom sans BPM ni tonalité


# ---------------------------------------------------------------------------
# Fonctions publiques
# ---------------------------------------------------------------------------

def extract_bpm(stem: str) -> tuple[str | None, str]:
    """
    Extrait le BPM du nom de fichier.
    Retourne (bpm, stem_sans_bpm).
    """
    match = BPM_PATTERN.search(stem)
    if not match:
        return None, stem
    bpm = match.group()
    clean = BPM_PATTERN.sub('', stem)
    clean = _clean_separators(clean)
    return bpm, clean


def extract_key(stem: str) -> tuple[str | None, bool, str]:
    """
    Extrait la tonalité du nom de fichier.
    Retourne (key, is_warning, stem_sans_key).
    """
    for pattern, warning in [
        (KEY_CAMELOT,          False),
        (KEY_PARENTHESES,      False),  # (C), (F#), (Am)
        (KEY_MINOR,            False),
        (KEY_MAJOR_EXPLICIT,   False),
        (KEY_MAJOR_IMPLICIT,   True),   # lettre seule, jamais en début
    ]:
        match = pattern.search(stem)
        if match:
            key   = match.group(1)
            clean = stem[:match.start()] + stem[match.end():]
            clean = _clean_separators(clean)
            return key, warning, clean

    return None, False, stem


def parse_filename(stem: str) -> ParseResult:
    """
    Parse complètement un nom de fichier (sans extension).
    Extrait BPM et tonalité, retourne le reste nettoyé.
    """
    bpm,  stem_no_bpm = extract_bpm(stem)
    key, warning, clean = extract_key(stem_no_bpm)
    return ParseResult(bpm=bpm, key=key, key_warning=warning, clean_stem=clean)


def build_filename(result: ParseResult, extension: str) -> str:
    """
    Reconstruit le nom de fichier au format BPM_TONALITE_reste.ext
    Les éléments absents sont simplement omis.
    """
    parts = [p for p in [result.bpm, result.key, result.clean_stem] if p]
    return "_".join(parts) + extension


# ---------------------------------------------------------------------------
# Utilitaire interne
# ---------------------------------------------------------------------------

def _clean_separators(s: str) -> str:
    """Nettoie les séparateurs multiples consécutifs et en début/fin."""
    s = re.sub(r'[_\-\s]{2,}', '_', s)
    return s.strip('_- ')