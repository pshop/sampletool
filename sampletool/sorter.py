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

def sort_folder(source: Path) -> dict:
    """
    Trie les fichiers audio de source dans des sous-dossiers _XXX_BPM.
    Les fichiers sans BPM détectable sont laissés en place.
    Retourne un dict avec les compteurs : moved, skipped.
    """
    stats = {"moved": 0, "skipped": 0}

    audio_files = [
        f for f in source.rglob("*")
        if f.is_file()
        and f.suffix.lower() in AUDIO_EXTENSIONS
        and not re.search(r'_\d+_BPM', str(f.parent))
    ]

    for file in audio_files:
        bpm = extract_bpm(file.stem)
        if bpm is None:
            stats["skipped"] += 1
            continue

        bpm_folder = source / f"_{bpm}_BPM"
        bpm_folder.mkdir(exist_ok=True)

        destination = bpm_folder / file.name

        # Gestion des conflits de noms
        counter = 2
        while destination.exists():
            destination = bpm_folder / f"{file.stem}_{counter}{file.suffix}"
            counter += 1

        file.rename(destination)
        stats["moved"] += 1

    return stats