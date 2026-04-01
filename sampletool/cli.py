import click
from pathlib import Path
from sampletool import __version__
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

def check_ffmpeg() -> None:
    """Vérifie que ffmpeg et ffprobe sont disponibles dans le PATH."""
    import shutil
    missing = [tool for tool in ("ffmpeg", "ffprobe") if not shutil.which(tool)]
    if missing:
        raise click.ClickException(
            f"{', '.join(missing)} introuvable(s) dans le PATH.\n"
            "  Installez FFmpeg : https://ffmpeg.org/download.html\n"
            "  Puis ajoutez le dossier bin/ à votre PATH."
        )

def write_report(report: list[dict], output_path: Path, dry_run: bool) -> None:
    """
    Écrit un rapport de conversion dans un fichier texte.
    Chaque ligne indique : AVANT → APRÈS [action] + warnings éventuels.
    """
    col_width = max((len(e["before"]) for e in report), default=40) + 2

    lines = [
        f"sampletool — Rapport de conversion{'  [DRY RUN]' if dry_run else ''}",
        f"Généré le : {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "=" * 80,
        f"{'AVANT':<{col_width}} {'APRÈS':<{col_width}} ACTION",
        "-" * 80,
    ]

    for entry in report:
        warn_str = "  ⚠ " + " | ".join(entry["warns"]) if entry["warns"] else ""
        lines.append(
            f"{entry['before']:<{col_width}} "
            f"{entry['after']:<{col_width}} "
            f"[{entry['action']}]{warn_str}"
        )

    lines += [
        "-" * 80,
        f"Total : {len(report)} fichier(s)",
        f"  convertis : {sum(1 for e in report if e['action'] == 'converti')}",
        f"  copiés    : {sum(1 for e in report if e['action'] == 'copié')}",
        f"  ignorés   : {sum(1 for e in report if e['action'] == 'ignoré')}",
        f"  erreurs   : {sum(1 for e in report if e['action'] == 'erreur')}",
    ]

    output_path.write_text("\n".join(lines), encoding="utf-8")
    click.echo(f"Rapport écrit : {output_path}")

@click.group()
@click.version_option(version=__version__)
def main():
    """sampletool — A CLI toolkit for audio sample management."""
    pass


@main.command("convert")
@click.argument("folder", type=click.Path(file_okay=False, path_type=Path), required=False)
@click.option("--profile", "-p", "profile_name",
              default="sp404", show_default=True,
              help="Conversion profile to use.")
@click.option("--sample-rate", "-r",
              type=click.Choice(["22050", "32000", "44100", "48000"]),
              default=None, help="Override profile sample rate.")
@click.option("--bit-depth", "-b",
              type=click.Choice(["8", "16", "24"]),
              default=None, help="Override profile bit depth.")
@click.option("--list-profiles", is_flag=True, default=False,
              help="List available profiles and exit.")
@click.option("--dry-run", is_flag=True, default=False,
              help="Simulate conversion without writing any file.")
@click.option("--report", is_flag=True, default=False,
              help="Write a conversion report alongside the output folder.")
def convert(folder, profile_name, sample_rate, bit_depth,
            list_profiles, dry_run, report):
    """Convert all audio files in FOLDER to WAV.

    If FOLDER is omitted, a file picker dialog will open.
    """
    if list_profiles:
        profiles = load_profiles()
        for name, p in profiles.items():
            click.echo(f"  {name:<12} — {p.description}")
        return

    check_ffmpeg()

    if folder is None:
        click.echo("Aucun dossier spécifié, ouverture du sélecteur...")
        folder = pick_folder_gui()
        if folder is None:
            raise click.ClickException("Aucun dossier sélectionné.")

    if not folder.exists() or not folder.is_dir():
        raise click.ClickException(f"Dossier introuvable : {folder}")

    try:
        profile = get_profile(profile_name)
    except ValueError as e:
        raise click.ClickException(str(e))

    override_rate  = int(sample_rate) if sample_rate else None
    override_depth = int(bit_depth)   if bit_depth   else None

    # Vérifie si le dossier de sortie existe déjà
    suffix      = f"_{profile.name}"
    output_root = folder.parent / (folder.name + suffix)

    if output_root.exists() and not dry_run:
        click.echo(f"⚠  Le dossier de sortie existe déjà : {output_root}")
        if not click.confirm("Voulez-vous continuer et écraser les fichiers existants ?"):
            raise click.ClickException("Opération annulée.")
        click.echo("")

    if dry_run:
        click.echo("*** DRY RUN — aucun fichier ne sera modifié ***\n")

    click.echo(f"Profil       : {profile.name} — {profile.description}")
    click.echo(f"Sample rate  : {override_rate  or profile.target_sample_rate} Hz")
    click.echo(f"Bit depth    : {override_depth or profile.target_bit_depth} bits")
    click.echo(f"Source       : {folder}")
    click.echo("")

    audio_files = find_audio_files(folder)
    total = len(audio_files)

    if total == 0:
        click.echo("Aucun fichier audio trouvé.")
        return

    click.echo(f"{total} fichier(s) trouvé(s)\n")

    with click.progressbar(
        length=total,
        label="Analyse" if dry_run else "Conversion",
        bar_template="%(label)s  %(bar)s  %(info)s",
        show_percent=True,
        show_pos=True,
    ) as bar:
        stats = convert_folder(
            folder, profile,
            override_rate=override_rate,
            override_depth=override_depth,
            progress_callback=lambda: bar.update(1),
            dry_run=dry_run,
        )

    click.echo("")

    if stats["warnings"]:
        click.echo("Avertissements :")
        for w in stats["warnings"]:
            click.echo(f"  ⚠  {w}", err=True)
        click.echo("")

    click.echo(f"✓ Convertis  : {stats['converted']}")
    click.echo(f"→ Copiés     : {stats['copied']}")
    click.echo(f"⊘ Ignorés    : {stats['skipped']}")
    click.echo(f"✗ Erreurs    : {stats['errors']}")

    # Génère le rapport si --report ou --dry-run
    if report or dry_run:
        report_path = folder.parent / (folder.name + "_report.txt")
        write_report(stats["report"], report_path, dry_run=dry_run)