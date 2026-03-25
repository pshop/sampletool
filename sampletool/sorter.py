import re
from pathlib import Path

AUDIO_EXTENSIONS = {
    ".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a",
    ".wma", ".aiff", ".aif", ".opus", ".mp2", ".ac3",
    ".amr", ".ape", ".mka", ".ra", ".caf"
}

# Regex : nombre entre 60 et 999 isolé des autres chiffres
BPM_PATTERN = re.compile(r'(?<!\d)(6[0-9]|[7-9][0-9]|[1-9][0-9]{2})(?!\d)')

def extract_bpm(filename: str) -> int | None:
    """Extrait le BPM d'un nom de fichier. Retourne un int ou None si pas trouvé."""
    match = BPM_PATTERN.search(filename)
    return match.group(0) if match else None

def rename_file_with_bpm(file: Path) -> bool:
    """
    Déplace le BPM au début du nom de fichier.
    Ex: trompette_135_loop.wav → 135_trompette_loop.wav
    Retourne True si renommé, False si pas de BPM ou déjà en place.
    """
    bpm = extract_bpm(file.stem)
    if bpm is None:
        return False

    # Retire le BPM (et les séparateurs autour) du nom original
    clean = BPM_PATTERN.sub('', file.stem)
    # Nettoie les underscores/tirets en double ou en début/fin
    clean = re.sub(r'[_\-]{2,}', '_', clean).strip('_-')

    new_name = f"{bpm}_{clean}{file.suffix}"

    # Déjà au bon format, rien à faire
    if file.name == new_name:
        return False

    file.rename(file.parent / new_name)
    return True

def sort_folder(source: Path) -> dict:
    """
    Renomme les fichiers audio en plaçant le BPM en début de nom.
    Les fichiers sans BPM sont laissés intacts.
    Retourne un dict avec les compteurs : renamed, skipped.
    """
    stats = {"renamed": 0, "skipped": 0}

    audio_files = [
        f for f in source.rglob("*")
        if f.is_file() and f.suffix.lower() in AUDIO_EXTENSIONS
    ]

    for file in audio_files:
        if rename_file_with_bpm(file):
            stats["renamed"] += 1
        else:
            stats["skipped"] += 1

    return stats