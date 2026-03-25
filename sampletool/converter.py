import re
import subprocess
from pathlib import Path

# Extensions audio supportées
AUDIO_EXTENSIONS = {
    ".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a",
    ".wma", ".aiff", ".aif", ".opus", ".mp2", ".ac3",
    ".amr", ".ape", ".mka", ".ra", ".caf"
}

### replacer les espaces par des _
def clean_filename(name: str) -> str:
    """Retire tous les caractères non-alphanumériques d'un nom de fichier."""
    return re.sub(r'[^a-zA-Z0-9_#]', '', name)

