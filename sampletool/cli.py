import click
from pathlib import Path
from sampletool import __version__
from sampletool.converter import convert_folder
from sampletool.sorter import sort_folder
from sampletool.profiles import get_profile, load_profiles


@click.group()
@click.version_option(version=__version__)
def main():
    """sampletool — A CLI toolkit for audio sample management."""
    pass


@main.command("convert")
@click.argument("folder", type=click.Path(exists=True, file_okay=False, path_type=Path))
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
    """Convert all audio files in FOLDER using a profile."""

    if list_profiles:
        profiles = load_profiles()
        for name, p in profiles.items():
            click.echo(f"  {name:<12} — {p.description}")
        return

    try:
        profile = get_profile(profile_name)
    except ValueError as e:
        raise click.ClickException(str(e))

    override_rate  = int(sample_rate) if sample_rate else None
    override_depth = int(bit_depth)   if bit_depth   else None

    click.echo(f"Profil       : {profile.name} — {profile.description}")
    click.echo(f"Sample rate  : {override_rate or profile.target_sample_rate} Hz")
    click.echo(f"Bit depth    : {override_depth or profile.target_bit_depth} bits")
    click.echo(f"Source       : {folder}")
    click.echo("")

    stats = convert_folder(folder, profile,
                           override_rate=override_rate,
                           override_depth=override_depth)

    if stats["warnings"]:
        click.echo("Avertissements :")
        for w in stats["warnings"]:
            click.echo(f"  ⚠  {w}", err=True)
        click.echo("")

    click.echo(f"✓ Convertis  : {stats['converted']}")
    click.echo(f"→ Copiés     : {stats['copied']}")
    click.echo(f"⊘ Ignorés    : {stats['skipped']}")
    click.echo(f"✗ Erreurs    : {stats['errors']}")


@main.command("sort-bpm")
@click.argument("folder", type=click.Path(exists=True, file_okay=False, path_type=Path))
def sort_bpm(folder):
    """Rename audio files in FOLDER by moving BPM to the start of filename."""
    click.echo(f"Source : {folder}")
    click.echo("")

    stats = sort_folder(folder)

    click.echo(f"✓ Renommés : {stats['renamed']}")
    click.echo(f"→ Ignorés  : {stats['skipped']}")