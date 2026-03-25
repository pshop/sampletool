import click
from pathlib import Path
from sampletool import __version__
<<<<<<< Updated upstream
from sampletool.converter import convert_folder
from sampletool.profiles import get_profile, load_profiles
=======
from sampletool.converter import convert_folder, find_audio_files
from sampletool.profiles import get_profile, load_profiles


def pick_folder_gui() -> Path | None:
    """
    Ouvre une boîte de dialogue pour sélectionner un dossier.
    Retourne le chemin choisi ou None si annulé.
    tkinter est inclus dans Python, aucune installation requise.
    """
    try:
        import tkinter as tk
        from tkinter import filedialog

        # On crée une fenêtre racine invisible — nécessaire pour filedialog
        root = tk.Tk()
        root.withdraw()
        # Forcer la fenêtre au premier plan
        root.lift()
        root.attributes("-topmost", True)

        folder = filedialog.askdirectory(title="Sélectionnez le dossier à convertir")
        root.destroy()

        return Path(folder) if folder else None

    except ImportError:
        raise click.ClickException(
            "tkinter n'est pas disponible sur ce système. "
            "Passez le dossier en argument : sampletool convert /chemin/dossier"
        )
>>>>>>> Stashed changes


@click.group()
@click.version_option(version=__version__)
def main():
    """sampletool — A CLI toolkit for audio sample management."""
    pass


@main.command("convert")
<<<<<<< Updated upstream
@click.argument("folder", type=click.Path(exists=True, file_okay=False, path_type=Path))
=======
@click.argument("folder", type=click.Path(file_okay=False, path_type=Path), required=False)
>>>>>>> Stashed changes
@click.option("--profile", "-p", "profile_name",
              default="sp404", show_default=True,
              help="Conversion profile to use.")
@click.option("--sample-rate", "-r",
              type=click.Choice(["22050", "32000", "44100", "48000"]),
              default=None,
              help="Override profile sample rate.")
@click.option("--bit-depth", "-b",
              type=click.Choice(["8", "16", "24"]),
              default=None,
              help="Override profile bit depth.")
@click.option("--list-profiles", is_flag=True, default=False,
              help="List available profiles and exit.")
def convert(folder, profile_name, sample_rate, bit_depth, list_profiles):
<<<<<<< Updated upstream
    """Convert all audio files in FOLDER using a profile."""

=======
    """Convert all audio files in FOLDER to WAV.

    If FOLDER is omitted, a file picker dialog will open.
    """
>>>>>>> Stashed changes
    if list_profiles:
        profiles = load_profiles()
        for name, p in profiles.items():
            click.echo(f"  {name:<12} — {p.description}")
        return

<<<<<<< Updated upstream
=======
    # Si aucun dossier fourni → ouvre la boîte de dialogue
    if folder is None:
        click.echo("Aucun dossier spécifié, ouverture du sélecteur...")
        folder = pick_folder_gui()
        if folder is None:
            raise click.ClickException("Aucun dossier sélectionné.")

    if not folder.exists() or not folder.is_dir():
        raise click.ClickException(f"Dossier introuvable : {folder}")

>>>>>>> Stashed changes
    try:
        profile = get_profile(profile_name)
    except ValueError as e:
        raise click.ClickException(str(e))

    override_rate  = int(sample_rate) if sample_rate else None
    override_depth = int(bit_depth)   if bit_depth   else None

    click.echo(f"Profil       : {profile.name} — {profile.description}")
<<<<<<< Updated upstream
    click.echo(f"Sample rate  : {override_rate or profile.target_sample_rate} Hz")
=======
    click.echo(f"Sample rate  : {override_rate  or profile.target_sample_rate} Hz")
>>>>>>> Stashed changes
    click.echo(f"Bit depth    : {override_depth or profile.target_bit_depth} bits")
    click.echo(f"Source       : {folder}")
    click.echo("")

<<<<<<< Updated upstream
    stats = convert_folder(folder, profile,
                           override_rate=override_rate,
                           override_depth=override_depth)

    if stats["warnings"]:
        click.echo("Avertissements :")
        for w in stats["warnings"]:
            click.echo(f"  ⚠  {w}", err=True)
        click.echo("")

=======
    # Compte les fichiers à traiter pour la barre de progression
    audio_files = find_audio_files(folder)
    total = len(audio_files)

    if total == 0:
        click.echo("Aucun fichier audio trouvé.")
        return

    click.echo(f"{total} fichier(s) trouvé(s)\n")

    # Barre de progression
    with click.progressbar(
        length=total,
        label="Conversion",
        bar_template="%(label)s  %(bar)s  %(info)s",
        show_percent=True,
        show_pos=True,
    ) as bar:
        def on_progress(n: int = 1):
            bar.update(n)

        stats = convert_folder(
            folder, profile,
            override_rate=override_rate,
            override_depth=override_depth,
            progress_callback=on_progress,
        )

    click.echo("")

    if stats["warnings"]:
        click.echo("Avertissements :")
        for w in stats["warnings"]:
            click.echo(f"  ⚠  {w}", err=True)
        click.echo("")

>>>>>>> Stashed changes
    click.echo(f"✓ Convertis  : {stats['converted']}")
    click.echo(f"→ Copiés     : {stats['copied']}")
    click.echo(f"⊘ Ignorés    : {stats['skipped']}")
    click.echo(f"✗ Erreurs    : {stats['errors']}")