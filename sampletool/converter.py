import re
import shutil
import subprocess
from pathlib import Path

from sampletool.key_parser import parse_filename, build_filename
from sampletool.profiles import Profile

AUDIO_EXTENSIONS = {
    ".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a",
    ".wma", ".aiff", ".aif", ".opus", ".mp2", ".ac3",
    ".amr", ".ape", ".mka", ".ra", ".caf"
}

BIT_DEPTH_FORMAT = {
    8:  "u8",
    16: "s16",
    24: "s32",
}


def clean_filename(name: str) -> str:
    """Remplace espaces et tirets par underscores,
    retire les caractères non-alphanumériques hors underscore et #."""
    name = name.replace(' ', '_').replace('-', '_').replace('.', '_')
    name = re.sub(r'[^a-zA-Z0-9_#]', '', name)
    name = re.sub(r'_{2,}', '_', name)

    return name.strip('_')


def find_audio_files(folder: Path) -> list[Path]:
    """Retourne tous les fichiers audio dans folder et ses sous-dossiers."""
    return [
        f for f in folder.rglob("*")
        if f.is_file() and f.suffix.lower() in AUDIO_EXTENSIONS
    ]


def probe_audio(path: Path) -> dict | None:
    """
    Utilise ffprobe pour lire sample_rate et bit_depth d'un fichier.
    Retourne None si ffprobe échoue.
    """
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-select_streams", "a:0",
            "-show_entries", "stream=sample_rate,bits_per_raw_sample",
            "-of", "default=noprint_wrappers=1",
            str(path),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None

    info = {}
    for line in result.stdout.splitlines():
        key, _, value = line.partition("=")
        if key == "sample_rate" and value.isdigit():
            info["sample_rate"] = int(value)
        elif key == "bits_per_raw_sample" and value.isdigit():
            info["bit_depth"] = int(value)

    return info if info else None


def effective_params(src_rate: int, src_depth: int,
                     target_rate: int, target_depth: int) -> tuple[int, int]:
    """
    Calcule les paramètres effectifs de conversion.
    On ne monte jamais ni le sample rate ni le bit depth.
    """
    return min(src_rate, target_rate), min(src_depth, target_depth)


def needs_conversion(src_rate: int, src_depth: int,
                     target_rate: int, target_depth: int) -> bool:
    """
    Retourne True si le fichier doit être converti.
    Un fichier est copié tel quel si son rate ET sa depth
    sont déjà inférieurs ou égaux à la cible.
    """
    eff_rate, eff_depth = effective_params(src_rate, src_depth, target_rate, target_depth)
    return eff_rate != src_rate or eff_depth != src_depth


def build_output_path(input_path: Path, source: Path,
                      output_root: Path, profile: Profile) -> tuple[Path, list[str]]:
    """
    Calcule le chemin de sortie en appliquant parsing BPM+tonalité,
    nettoyage du nom, troncature et gestion des conflits.
    """
    warnings = []
    relative = input_path.relative_to(source)

    src_ext = input_path.suffix.lower()
    out_ext = src_ext if src_ext in profile.compatible_formats else profile.convert_to

    parsed = parse_filename(input_path.stem)
    if parsed.key_warning:
        warnings.append(
            f"Tonalité ambiguë détectée '{parsed.key}' dans '{input_path.name}'"
        )

    parsed.clean_stem = clean_filename(parsed.clean_stem)
    parsed.clean_stem = parsed.clean_stem.strip('_')
    new_name = build_filename(parsed, out_ext)

    # Troncature si nécessaire
    if profile.max_filename_length > 0:
        stem     = Path(new_name).stem
        ext      = Path(new_name).suffix
        max_stem = profile.max_filename_length - len(ext)
        if len(stem) > max_stem:
            warnings.append(f"Nom tronqué : '{new_name}' → '{stem[:max_stem]}{ext}'")
            new_name = stem[:max_stem] + ext

    output_path = output_root / relative.parent / new_name

    # Gestion des conflits : si le nom existe déjà (produit par un autre fichier source)
    # on ajoute un suffixe _2, _3, etc.
    if output_path.exists():
        stem = Path(new_name).stem
        ext  = Path(new_name).suffix
        counter = 2
        while output_path.exists():
            candidate = output_root / relative.parent / f"{stem}_{counter}{ext}"
            if not candidate.exists():
                warnings.append(
                    f"Conflit de nom : '{new_name}' renommé en '{stem}_{counter}{ext}'"
                )
                output_path = candidate
                break
            counter += 1

    return output_path, warnings

def convert_file(input_path: Path, output_path: Path,
                 sample_rate: int, bit_depth: int) -> bool:
    """Convertit un fichier audio via FFmpeg. Retourne True si succès."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [
            "ffmpeg", "-i", str(input_path),
            "-ar", str(sample_rate),
            "-sample_fmt", BIT_DEPTH_FORMAT[bit_depth],
            "-y", "-loglevel", "error",
            str(output_path),
        ],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def convert_folder(source: Path, profile: Profile,
                   override_rate: int | None = None,
                   override_depth: int | None = None,
                   progress_callback=None,
                   dry_run: bool = False) -> dict:
    """
    Convertit tous les fichiers audio de source selon le profil donné.
    dry_run=True : calcule les opérations sans les exécuter.
    Retourne un dict : converted, copied, skipped, errors, warnings, report.
    """
    target_rate  = override_rate  or profile.target_sample_rate
    target_depth = override_depth or profile.target_bit_depth

    suffix      = f"_{profile.name}"
    output_root = source.parent / (source.name + suffix)
    stats: dict = {
        "converted": 0, "copied": 0, "skipped": 0,
        "errors": 0, "warnings": [],
        # Liste de dicts décrivant chaque opération — utilisée pour le rapport
        "report": []
    }

    for input_path in find_audio_files(source):

        output_path, warns = build_output_path(
            input_path, source, output_root, profile
        )
        stats["warnings"].extend(warns)

        # Détermine l'action qui sera effectuée
        if output_path.exists():
            action = "ignoré"
            stats["skipped"] += 1
            stats["report"].append({
                "before": input_path.name,
                "after":  output_path.name,
                "action": action,
                "warns":  warns,
            })
            if progress_callback:
                progress_callback()
            continue

        info      = probe_audio(input_path)
        if info is None:
            stats["warnings"].append(f"Impossible de lire les infos audio de '{input_path.name}'")
        src_rate  = info.get("sample_rate", 0) if info else 0
        src_depth = info.get("bit_depth", 0)   if info else 0
        src_ext   = input_path.suffix.lower()

        format_incompatible = src_ext not in profile.compatible_formats

        if format_incompatible or (
            src_rate  > 0 and src_depth > 0 and
            needs_conversion(src_rate, src_depth, target_rate, target_depth)
        ):
            action = "converti"
        else:
            action = "copié"

        stats["report"].append({
            "before": input_path.name,
            "after":  output_path.name,
            "action": action,
            "warns":  warns,
        })

        if dry_run:
            # En dry-run on comptabilise sans toucher aux fichiers
            if action == "converti":
                stats["converted"] += 1
            else:
                stats["copied"] += 1
            if progress_callback:
                progress_callback()
            continue

        output_path.parent.mkdir(parents=True, exist_ok=True)

        if action == "converti":
            eff_rate, eff_depth = effective_params(
                src_rate  or target_rate,
                src_depth or target_depth,
                target_rate, target_depth
            )
            success = convert_file(input_path, output_path, eff_rate, eff_depth)
            if success:
                stats["converted"] += 1
            else:
                stats["errors"] += 1
                # Corrige l'action dans le rapport
                stats["report"][-1]["action"] = "erreur"
        else:
            shutil.copy2(input_path, output_path)
            stats["copied"] += 1

        if progress_callback:
            progress_callback()

    return stats