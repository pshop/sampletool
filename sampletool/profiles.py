from dataclasses import dataclass, field
from pathlib import Path

try:
    import tomllib          # stdlib Python 3.11+
except ImportError:
    import tomli as tomllib # fallback pour Python 3.10


# Chemin du fichier de profils — à la racine du projet
PROFILES_PATH = Path(__file__).parent.parent / "profiles.toml"


@dataclass
class Profile:
    name: str
    description: str
    target_sample_rate: int
    target_bit_depth: int
    compatible_formats: list[str]
    convert_to: str
    max_filename_length: int = 0   # 0 = pas de limite


def load_profiles() -> dict[str, Profile]:
    """
    Charge tous les profils depuis profiles.toml.
    Retourne un dict nom → Profile.
    """
    if not PROFILES_PATH.exists():
        raise FileNotFoundError(f"profiles.toml introuvable : {PROFILES_PATH}")

    with open(PROFILES_PATH, "rb") as f:
        data = tomllib.load(f)

    profiles = {}
    for name, values in data.get("profiles", {}).items():
        profiles[name] = Profile(
            name=name,
            description=values.get("description", ""),
            target_sample_rate=values["target_sample_rate"],
            target_bit_depth=values["target_bit_depth"],
            compatible_formats=values.get("compatible_formats", []),
            convert_to=values.get("convert_to", ".wav"),
            max_filename_length=values.get("max_filename_length", 0),
        )
    return profiles


def get_profile(name: str) -> Profile:
    """
    Retourne un profil par son nom.
    Lève ValueError si le profil n'existe pas.
    """
    profiles = load_profiles()
    if name not in profiles:
        available = ", ".join(profiles.keys())
        raise ValueError(f"Profil '{name}' introuvable. Disponibles : {available}")
    return profiles[name]