# sampletool

A CLI toolkit for audio sample management.

![Tests](https://github.com/pshop/sampletool/actions/workflows/tests.yml/badge.svg)

## Features

- **convert** — Convertit récursivement des fichiers audio selon un profil cible (sample rate, bit depth, format)
- Renommage automatique : extraction du BPM et de la tonalité depuis le nom de fichier
- Rapport de conversion optionnel

## Requirements

- Python 3.10+
- [FFmpeg](https://ffmpeg.org/download.html) installé et disponible dans le PATH

## Installation

```bash
git clone https://github.com/pshop/sampletool.git
cd sampletool

python -m venv .venv
source .venv/bin/activate      # macOS / Linux
# .venv\Scripts\activate       # Windows

pip install -e ".[dev]"
```

## Usage

```bash
# Convertir un dossier (ouvre un sélecteur de dossier si omis)
sampletool convert /chemin/vers/dossier

# Choisir un profil
sampletool convert /chemin/vers/dossier --profile lo-fi

# Surcharger le sample rate ou le bit depth
sampletool convert /chemin/vers/dossier --sample-rate 44100 --bit-depth 16

# Simuler sans écrire de fichiers
sampletool convert /chemin/vers/dossier --dry-run

# Générer un rapport de conversion
sampletool convert /chemin/vers/dossier --report

# Lister les profils disponibles
sampletool convert --list-profiles

# Aide
sampletool --help
sampletool convert --help
```

## Profiles

Les profils sont définis dans `profiles.toml` à la racine du projet.

| Profil  | Description             | Sample rate | Bit depth |
|---------|-------------------------|-------------|-----------|
| sp404   | Roland SP-404 MK II     | 48 000 Hz   | 16 bits   |
| lo-fi   | Lo-fi / artefacts       | 22 050 Hz   | 8 bits    |

## Development

```bash
pytest
pytest --cov=sampletool
```

## Project Structure

```
sampletool/
├── .github/workflows/   # CI GitHub Actions
├── sampletool/          # Code source
│   ├── cli.py           # Point d'entrée CLI (Click)
│   ├── converter.py     # Moteur de conversion audio (FFmpeg)
│   ├── key_parser.py    # Extraction BPM et tonalité depuis les noms de fichiers
│   └── profiles.py      # Chargement des profils (profiles.toml)
├── tests/               # Tests unitaires (pytest)
├── profiles.toml        # Définition des profils de conversion
├── pyproject.toml       # Configuration du projet
└── README.md
```
