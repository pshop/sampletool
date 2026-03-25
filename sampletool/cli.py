import click
from pathlib import Path
from sampletool import __version__
from sampletool.converter import convert_folder
from sampletool.sorter import sort_folder

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
@click.argument("folder", type=click.Path(exists=True, file_okay=False, path_type=Path))
def convert(folder):
    """Convert all audio files in FOLDER to WAV 16-bit 48kHz."""
    click.echo(f"Source  : {folder}")
    click.echo(f"Sortie  : {folder.parent / (folder.name + '_16BITS')}")
    click.echo("")

    stats = convert_folder(folder)

    click.echo(f"✓ Convertis : {stats['converted']}")
    click.echo(f"→ Ignorés   : {stats['skipped']}")
    click.echo(f"✗ Erreurs   : {stats['errors']}")


@main.command("sort-bpm")
@click.argument("folder", type=click.Path(exists=True, file_okay=False, path_type=Path))
def sort_bpm(folder):
    """Rename audio files in FOLDER by moving BPM to the start of filename."""
    click.echo(f"Source : {folder}")
    click.echo("")

    stats = sort_folder(folder)

    click.echo(f"✓ Renommés : {stats['renamed']}")
    click.echo(f"→ Ignorés  : {stats['skipped']}")
