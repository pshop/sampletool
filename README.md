# sampletool

A CLI toolkit for audio sample management.

![Tests](https://github.com/TON_USERNAME/sampletool/actions/workflows/tests.yml/badge.svg)

## Features

- **convert** — Convert audio files to WAV 16-bit / 48 000 Hz (recursively)
- **sort-bpm** — Sort audio files into BPM subfolders based on filename

## Requirements

- Python 3.10+
- [FFmpeg](https://ffmpeg.org/download.html) installed and available in your PATH

## Installation

```bash
# Cloner le repo
git clone https://github.com/TON_USERNAME/sampletool.git
cd sampletool

# Créer un environnement virtuel
python -m venv .venv

# Activer l'environnement virtuel
# Windows :
.venv\Scripts\activate
# macOS / Linux :
source .venv/bin/activate

# Installer le projet en mode développement
pip install -e ".[dev]"
```

## Usage

```bash
# Convertir tous les fichiers audio d'un dossier
sampletool convert /chemin/vers/dossier

# Trier par BPM
sampletool sort-bpm /chemin/vers/dossier

# Aide
sampletool --help
```

## Development

```bash
# Lancer les tests
pytest

# Lancer les tests avec couverture de code
pytest --cov=sampletool
```

## Project Structure

```
sampletool/
├── .github/workflows/   # CI GitHub Actions
├── sampletool/          # Code source
│   ├── __init__.py
│   └── cli.py           # Point d'entrée CLI (Click)
├── tests/               # Tests unitaires (pytest)
├── .gitignore
├── pyproject.toml       # Configuration du projet
└── README.md
```
