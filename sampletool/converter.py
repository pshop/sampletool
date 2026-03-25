import re
import subprocess
from pathlib import Path

# Extensions audio supportées
AUDIO_EXTENSIONS = {
    ".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a",
    ".wma", ".aiff", ".aif", ".opus", ".mp2", ".ac3",
    ".amr", ".ape", ".mka", ".ra", ".caf"
}


def clean_filename(name: str) -> str:
    """Remplace les espaces par des underscores et\
     retire tous les caractères non-alphanumériques\
     hors d'un nom de fichier."""
    name = name.replace(' ', '_')
    name = name.replace('-', '_')
    
    return re.sub(r'[^a-zA-Z0-9_#]', '', name)

def find_audio_files(folder: Path) -> list[Path]:
    """Retourne tous les fichiers audio dans folder et ses sous-dossiers."""
    return [
        f for f in folder.rglob("*")
        if f.is_file() and f.suffix.lower() in AUDIO_EXTENSIONS
    ]

def convert_file(input_path: Path, output_path: Path) -> bool:
    """
    Convertit un fichier audio en WAV 16 bits / 48 000 Hz via FFmpeg.
    Retourne True si succès, False si erreur.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        [
            "ffmpeg", "-i", str(input_path),
            "-ar", "48000",
            "-sample_fmt", "s16",
            "-y",
            "-loglevel", "error",
            str(output_path),
        ],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0

def convert_folder(source: Path) -> dict:
    """
    Convertit tous les fichiers audio de source (récursivement).
    Les fichiers convertis sont placés dans source_16BITS.
    Retourne un dict avec les compteurs : converted, skipped, errors.
    """
    output_root = source.parent / (source.name + "_16BITS")
    stats = {"converted": 0, "skipped": 0, "errors": 0}

    for input_path in find_audio_files(source):
        # Chemin relatif par rapport au dossier source
        relative = input_path.relative_to(source)

        # Nom de fichier nettoyé + extension .wav
        clean_name = clean_filename(input_path.stem) + ".wav"
        output_path = output_root / relative.parent / clean_name

        if output_path.exists():
            stats["skipped"] += 1
            continue

        success = convert_file(input_path, output_path)
        if success:
            stats["converted"] += 1
        else:
            stats["errors"] += 1

    return stats