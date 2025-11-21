# multi_agents_outfits

Petit guide pour installer, lancer le code et exécuter les tests.

## Prérequis
- Python 3.8+ installé (`python --version`)
- Git (optionnel)
- (Optionnel) Docker si vous préférez containeriser

## Installation (recommandée)
1. Créer et activer un environnement virtuel :
   - Linux / macOS:
     - python -m venv .venv
     - source .venv/bin/activate
   - Windows (PowerShell):
     - python -m venv .venv
     - .\.venv\Scripts\Activate.ps1

2. Installer les dépendances si un fichier `requirements.txt` est présent :
   - pip install -r requirements.txt

   Si le projet est packagé (`pyproject.toml` / `setup.py`), vous pouvez aussi :
   - pip install -e .

## Lancer le code
- Si le package expose un point d'entrée :
  - python -m multi_agents
- Sinon, exécutez le script principal s'il existe (exemples possibles) :
  - python multi_agents/main.py
  - python run.py

Regardez la racine du dépôt ou le dossier `multi_agents/` pour identifier le fichier d'entrée exact.

## Tests
- Si `pytest` est utilisé :
  - pip install pytest   # si nécessaire
  - pytest -q tests/     # ou simplement `pytest` si les tests sont à la racine
- Si un autre runner est utilisé, suivez les fichiers de configuration (`pyproject.toml`, `tox.ini`, etc.).

## Exemples d'usage
- Exécution simple (après activation du venv et installation) :
  - python -m multi_agents
- Pour un script d'analyse d'événement (si présent) :
  - python scripts/analyze_event.py "Description de l'événement"

## Dépannage rapide
- "ModuleNotFoundError": vérifier l'activation du venv et l'installation des dépendances.
- Pas de fichier `requirements.txt`: inspecter `pyproject.toml` / `setup.py` pour la liste des dépendances.
- Tests qui échouent: exécuter `pytest -q -k <nom_du_test>` pour isoler.

## Structure suggérée (à vérifier dans le dépôt)
- multi_agents/        # code principal
- tests/               # tests unitaires
- requirements.txt
- README.md

Fin.