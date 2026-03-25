import click
from sampletool import __version__


# -----------------------------------------------------------------------------
# Groupe principal de commandes
# -----------------------------------------------------------------------------
# @click.group() crée un point d'entrée qui regroupe plusieurs sous-commandes.
# Exemple d'utilisation : sampletool --help, sampletool convert, sampletool sort-bpm

@click.group()
@click.version_option(version=__version__)
def main():
    """sampletool — A CLI toolkit for audio sample management."""
    pass


# -----------------------------------------------------------------------------
# Sous-commandes (à compléter aux prochaines étapes)
# -----------------------------------------------------------------------------

@main.command("convert")
@click.argument("folder", type=click.Path(exists=True, file_okay=False))
def convert(folder):
    """Convert all audio files in FOLDER to WAV 16-bit 48kHz."""
    # La logique sera implémentée à l'étape 2
    click.echo(f"[convert] Dossier cible : {folder} (à implémenter)")


@main.command("sort-bpm")
@click.argument("folder", type=click.Path(exists=True, file_okay=False))
def sort_bpm(folder):
    """Sort audio files in FOLDER into subfolders by BPM."""
    # La logique sera implémentée à l'étape 2
    click.echo(f"[sort-bpm] Dossier cible : {folder} (à implémenter)")
